from compiler.enumerations.SegmentTypes import SegmentTypes
from compiler.enumerations.SubRoutineType import SubRoutineType
from compiler.enumerations.SymbolKind import SymbolKind
from compiler.enumerations.TokenType import TokenType
from compiler.init_logging import logger
from compiler.symbol_table import SymbolTable
from compiler.jack_tokenizer import JackTokenizer

class CompilationEngine:
    def __init__(self, vmwriter):
        self.tokenizer = None
        self.operator_list = ["+", "-", "*", "/", "&", "|", "<", ">", "="]
        self.unary_operator_list = ["-", "~"]
        self.keyword_constant_list = ["true", "false", "null", "this"]
        self.converted_symbols = {"<": "&lt;", ">": "&gt;", '"': "&quot;", "&": "&amp;"}
        self.term_global_counter = 0
        self.expression_global_counter = 0
        self.writer = vmwriter
        self.class_symbol_table = SymbolTable()
        self.subroutine_symbol_table = SymbolTable()
        self.class_name = None
        self.class_var_config = {}
        self.subroutine_config = {}
        self.if_count = 0
        self.while_count = 0

    def set_tokenizer(self, t: JackTokenizer) -> None:
        """
        Helper method - sets a tokenizer the instance can use
        """
        self.tokenizer = t

    def compile(self) -> None:
        """
        Entry method for compilation - every JACK file that needs to be compiled must be in a class
        """
        self.compile_class()

    def compile_class(self) -> None:
        """
        Compiles the semantics related to a class.
        For example, the name of the class.
        Kicks off the process of compiling other components of the class e.g. class level variables
        """
        self.process_rule(TokenType.KEYWORD, "class")
        self.class_name = self.process_token(TokenType.IDENTIFIER)
        self.process_rule(TokenType.SYMBOL, "{")
        while self.tokenizer.peek().lower() not in SubRoutineType:
            logger.debug(
                f"self.tokenizer.peek() not in SubRoutineType: {self.tokenizer.peek() not in SubRoutineType}. peek: {self.tokenizer.peek()}"
            )
            self.compile_class_var_dec()
        while self.tokenizer.peek() != "}":
            self.compile_sub_routine_dec()
            self.subroutine_symbol_table.reset()
        self.process_rule(TokenType.SYMBOL, "}")

    def compile_sub_routine_dec(self) -> None:
        """
        Compiles the semantics related the declaration of sub routines
        Sub routines are either methods, functions, or constructors
        Config details of the sub routine is captures in the instance variable
        subroutine_config for use later when more information is available.
        """
        self.if_count = 0
        self.while_count = 0
        # constructor | function | method
        self.subroutine_config["type"] = self.process_rule(
            TokenType.KEYWORD, *[i.value for i in SubRoutineType]
        )
        # void | type - can be either IDENTIFIER or KEYWORD
        self.subroutine_config["return_type"] = self.process_token(
            "any"
        )
        # subRoutine name
        self.subroutine_config["name"] = self.process_token(
            TokenType.IDENTIFIER
        )
        if self.subroutine_config["type"] == SubRoutineType.METHOD.value:
            # add THIS to the ARG list
            self.subroutine_symbol_table.define(
                "this", self.class_name, SymbolKind.ARG.value
            )
        self.process_rule(TokenType.SYMBOL, "(")
        self.compile_parameter_list()
        self.process_rule(TokenType.SYMBOL, ")")
        self.compile_sub_routine_body()

    def compile_sub_routine_body(self) -> None:
        """
        Compiles the semantics related to the body in the sub routine
        Subroutine declaration is actually converted to VM here
        compile_statements is called here
        """
        logger.debug("<subroutineBody>")
        self.process_rule(TokenType.SYMBOL, "{")
        while self.tokenizer.peek() == "var":
            self.compile_var_dec()
        self.write_subroutine_signature()
        self.compile_statments()
        self.process_rule(TokenType.SYMBOL, "}")
        logger.debug("</subroutineBody>")

    def write_subroutine_signature(self):
        """
        Makes use of the instance variable 'subroutine_config' to write subroutine signature in VM
        """
        self.writer.write_function(
            f"{self.class_name}.{self.subroutine_config['name']}",
            self.subroutine_symbol_table.var_count(SegmentTypes.LOCAL.value),
        )
        if self.subroutine_config["type"] == SubRoutineType.METHOD.value:
            self.writer.write_push(SegmentTypes.ARGUMENT.value, 0)  # push argument 0
            self.writer.write_pop(
                SegmentTypes.POINTER.value, 0
            )  # pop pointer 0 -> set THIS
        elif self.subroutine_config["type"] == SubRoutineType.CONSTRUCTOR.value:
            self.writer.write_push(
                SegmentTypes.CONSTANT.value,
                self.class_symbol_table.var_count(SegmentTypes.THIS.value),
            )  # push constant numVar
            self.writer.write_call(
                "Memory.alloc", 1
            )  # call memory.alloc 1 -> allocate memory for object
            self.writer.write_pop(
                SegmentTypes.POINTER.value, 0
            )  # pop pointer 0 -> set THIS

    def compile_var_dec(self) -> None:
        """
        At the top of every subroutine body, the user can decide to declare some
        local variables.
        This method converts those declarations into their representations in the 
        symbol table
        """
        logger.debug("<varDec>")
        self.process_rule(TokenType.KEYWORD, "var")
        var_type = self.process_token(
            "any"
        )  # variable type - can be either IDENTIFIER or KEYWORD
        var_name = self.process_token(TokenType.IDENTIFIER)  # variable name
        self.subroutine_symbol_table.define(
            var_name, var_type, SegmentTypes.LOCAL.value
        )
        logger.debug(f"Subroutine defined - var_name: {var_name}, var_type: {var_type}")
        while self.tokenizer.peek() == ",":
            var_type = self.process_token("any")  # variable type
            var_name = self.process_token(TokenType.IDENTIFIER)  # variable name
            self.subroutine_symbol_table.define(
                var_name, var_type, SegmentTypes.LOCAL.value
            )
            logger.debug(
                f"Subroutine defined - var_name: {var_name}, var_type: {var_type}"
            )
        self.process_rule(TokenType.SYMBOL, ";")
        logger.debug("</varDec>")

    def compile_statments(self) -> None:
        """
        The meat of every sub routine - statements
        Decides what kind of statement the current line represents and 
        dispatches appropriately
        """
        logger.debug("<statements>")
        while self.tokenizer.peek() != "}":
            match self.tokenizer.peek():
                case "let":
                    self.compile_let_statment()
                case "if":
                    self.compile_if_statment(self.if_count)
                case "while":
                    self.compile_while_statment(self.while_count)
                case "do":
                    self.compile_do_statment()
                case "return":
                    self.compile_return_statment()
        logger.debug("</statements>")

    def compile_let_statment(self) -> None:
        """
        Compiles a LET statment
        Some complications arises when we are assigning/reading from an array
        """
        logger.debug("<letStatement>")
        is_assignment_to_array = False
        self.process_rule(TokenType.KEYWORD, "let")
        var_name = self.process_token(TokenType.IDENTIFIER)
        var_type, var_kind, var_idx = self.resolve_class_type_to_call(var_name)
        logger.debug(
            f"let statement - type: {var_type}, var_kind: {var_kind}, var_idx: {var_idx}"
        )
        if self.tokenizer.peek() == "[":  # LHS array
            self.writer.write_push(var_kind, var_idx)  # base address of the array
            self.process_rule(TokenType.SYMBOL, "[")
            self.compile_expression()
            self.process_rule(TokenType.SYMBOL, "]")
            self.writer.write_arithmetic(
                "add"
            )  # get the particular index we are addresssing
            is_assignment_to_array = True
        self.process_rule(TokenType.SYMBOL, "=")
        self.compile_expression()  # potentially RHS of the array
        if is_assignment_to_array:
            self.writer.write_pop(
                SegmentTypes.TEMP.value, 0
            )  # place evaluated RHS into TEMP 0
            self.writer.write_pop(
                SegmentTypes.POINTER.value, 1
            )  # align to the LHS array
            self.writer.write_push(
                SegmentTypes.TEMP.value, 0
            )  # place TEMP 0 back onto the stack
            self.writer.write_pop(
                SegmentTypes.THAT.value, 0
            )  # pop off the stack and into THAT
        else:
            self.writer.write_pop(var_kind, var_idx)
        self.process_rule(TokenType.SYMBOL, ";")
        logger.debug("</letStatement>")

    def compile_if_statment(self, if_count: int) -> None:
        """
        Compiles an IF statement
        Some complication arises from nested IF statements
        """
        self.if_count += 1
        if_count += 1
        logger.debug("<ifStatement>")
        self.process_rule(TokenType.KEYWORD, "if")
        self.process_rule(TokenType.SYMBOL, "(")
        self.compile_expression()
        self.writer.write_arithmetic("not")
        self.writer.write_if(
            f"{self.class_name}.{self.subroutine_config["name"]}.if_{if_count}.pathA"
        )  # go if not true
        self.process_rule(TokenType.SYMBOL, ")")
        self.process_rule(TokenType.SYMBOL, "{")
        self.compile_statments()
        self.writer.write_goto(
            f"{self.class_name}.{self.subroutine_config["name"]}.if_{if_count}.pathB"
        )  # skip statements for if not true
        self.process_rule(TokenType.SYMBOL, "}")
        there_is_else = False
        if self.tokenizer.peek() == "else":
            there_is_else = True
            self.process_rule(TokenType.KEYWORD, "else")
            self.process_rule(TokenType.SYMBOL, "{")
        self.writer.write_label(
            f"{self.class_name}.{self.subroutine_config["name"]}.if_{if_count}.pathA"
        )
        if there_is_else:  # there has to be a more elegant way of doing this. Line above MUST be printed regardless. Lines below cannot be printed if no ELSE
            self.compile_statments()
            self.process_rule(TokenType.SYMBOL, "}")
        self.writer.write_label(
            f"{self.class_name}.{self.subroutine_config["name"]}.if_{if_count}.pathB"
        )
        logger.debug("</ifStatement>")

    def compile_while_statment(self, while_count: int) -> None:
        """
        Compiles a WHILE statement
        Some complication arises from nested WHILE statements
        """
        self.while_count += 1
        while_count += 1
        logger.debug("<whileStatement>")
        self.writer.write_label(
            f"{self.class_name}.{self.subroutine_config["name"]}.while_{while_count}.pathA"
        )  # top
        self.process_rule(TokenType.KEYWORD, "while")
        self.process_rule(TokenType.SYMBOL, "(")
        self.compile_expression()
        self.writer.write_arithmetic("not")
        self.writer.write_if(
            f"{self.class_name}.{self.subroutine_config["name"]}.while_{while_count}.pathB"
        )  # break
        self.process_rule(TokenType.SYMBOL, ")")
        self.process_rule(TokenType.SYMBOL, "{")
        self.compile_statments()
        self.writer.write_goto(
            f"{self.class_name}.{self.subroutine_config["name"]}.while_{while_count}.pathA"
        )  # back to top
        self.process_rule(TokenType.SYMBOL, "}")
        self.writer.write_label(
            f"{self.class_name}.{self.subroutine_config["name"]}.while_{while_count}.pathB"
        )  # break label
        logger.debug("</whileStatement>")

    def compile_do_statment(self) -> None:
        """
        Compiles a DO statement
        """
        logger.debug("<doStatement>")
        self.process_rule(TokenType.KEYWORD, "do")
        self.compile_expression(False)
        self.process_rule(TokenType.SYMBOL, ";")
        self.writer.write_pop(SegmentTypes.TEMP.value, 0)
        logger.debug("</doStatement>")

    def compile_return_statment(self) -> None:
        """
        Compiles a RETURN statement
        """
        logger.debug("<returnStatement>")
        self.process_rule(TokenType.KEYWORD, "return")
        if self.tokenizer.peek() != ";":
            self.compile_expression()
        if self.subroutine_config["return_type"] == "void":
            self.writer.write_push(SegmentTypes.CONSTANT.value, 0)
        self.writer.write_return()
        self.process_rule(TokenType.SYMBOL, ";")
        logger.debug("</returnStatement>")

    def compile_expression_list(self) -> None:
        """
        Compiles the innards of a sub routine call
        """
        count = 0
        logger.debug("<expressionList>")
        if self.tokenizer.peek() != ")":  # end of expression list
            count = 1
            self.compile_expression()
            while self.tokenizer.peek() == ",":
                self.process_rule(TokenType.SYMBOL, ",")
                self.compile_expression()
                count += 1
        logger.debug("</expressionList>")
        return count

    def compile_expression(self, to_print=True) -> None:
        """
        1 of 2 parts that make up the heart of the compiler
        Some complications arise from handling bracket priority in mathematical operations
        """
        operator = {}
        logger.debug(
            f"{self.expression_global_counter}.{self.term_global_counter} compile_expression()"
        )
        self.expression_global_counter += 1
        if to_print:
            logger.debug("<expression>")
        self.compile_term(to_print)
        while self.tokenizer.peek() in self.operator_list:
            operator[len(operator) + 1] = self.process_rule(
                TokenType.SYMBOL, *self.operator_list
            )
            self.compile_term()
        while len(operator) > 0:
            self.process_operator(
                operator.pop(
                    len(operator),
                ),
            )

        if to_print:
            logger.debug("</expression>")

    def compile_term(self, to_print=True) -> None:
        """
        1 of 2 parts that make up the heart of the compiler
        Composed of 2 parts
        - Decides what to do when it encounters integers, strings, keywords, operators, expressions lists
        - if it encounters an identifier, it will take 1 look ahead to decide if its an array, function
        call, or a method call
        """
        logger.debug(
            f"{self.expression_global_counter}.{self.term_global_counter}. compile_term()"
        )
        self.term_global_counter += 1
        if to_print:
            logger.debug("<term>")
        current_token = self.tokenizer.peek()
        current_type = self.tokenizer.token_type
        if current_type == TokenType.INT_CONST:
            int_const = self.process_token(TokenType.INT_CONST)
            self.writer.write_push(SegmentTypes.CONSTANT.value, int_const)
        elif current_type == TokenType.STRING_CONST:
            string_const = self.process_token(TokenType.STRING_CONST)
            self.writer.write_push(SegmentTypes.CONSTANT.value, len(string_const))
            self.writer.write_call("String.new", 1)
            for c in string_const:
                self.writer.write_push(SegmentTypes.CONSTANT.value, ord(c))
                self.writer.write_call("String.appendChar", 2)
        elif current_token in self.keyword_constant_list:
            keyword_constant = self.process_rule(
                TokenType.KEYWORD, *self.keyword_constant_list
            )
            if keyword_constant == "true":
                self.writer.write_push(SegmentTypes.CONSTANT.value, 1)
                self.writer.write_arithmetic("neg")
            elif keyword_constant == "this":
                self.writer.write_push(SegmentTypes.POINTER.value, 0)
            else:  # false | null
                self.writer.write_push(SegmentTypes.CONSTANT.value, 0)
        elif current_token == "(":  # expression list
            self.process_rule(TokenType.SYMBOL, "(")
            self.compile_expression()
            self.process_rule(TokenType.SYMBOL, ")")
        elif current_token in self.unary_operator_list:
            unary_op = self.process_rule(TokenType.SYMBOL, *self.unary_operator_list)
            self.compile_term()
            self.process_unary_operator(unary_op)
        elif current_type == TokenType.IDENTIFIER:
            self.process_token(TokenType.IDENTIFIER)
            advance_token = self.tokenizer.peek()
            if advance_token == "[":
                class_type, class_kind, class_index = self.resolve_class_type_to_call(
                    current_token
                )
                # push base address of array onto stack
                self.writer.write_push(
                    class_kind, class_index
                )
                self.process_rule(TokenType.SYMBOL, "[")
                self.compile_expression()  # resolve internals of []
                # get address of where we are addressing
                self.writer.write_arithmetic("add")
                self.process_rule(TokenType.SYMBOL, "]")
                # set THAT to where we are addressing
                self.writer.write_pop(
                    SegmentTypes.POINTER.value, 1
                )
                # push value at THAT onto stack
                self.writer.write_push(
                    SegmentTypes.THAT.value, 0
                )
            elif advance_token == "(":
                self.process_rule(TokenType.SYMBOL, "(")
                # is a local method e.g. distance(p2)
                if (
                    current_token not in self.class_symbol_table.table
                    and current_token not in self.subroutine_symbol_table.table
                ):
                    # push THIS onto the stack
                    self.writer.write_push(SegmentTypes.POINTER.value, 0)
                    arg_count = self.compile_expression_list()
                    self.writer.write_call(
                        f"{self.class_name}.{current_token}", arg_count + 1
                    )
                else:
                    self.compile_expression_list()
                self.process_rule(TokenType.SYMBOL, ")")
            elif advance_token == ".":  # is a method on an external class
                variable_to_call = current_token
                class_type, class_kind, class_index = self.resolve_class_type_to_call(
                    variable_to_call
                )
                if class_index > -1: # push the class that the method is being called on
                    self.writer.write_push(
                        class_kind, class_index
                    )
                self.process_rule(TokenType.SYMBOL, ".")
                subroutine_to_call = self.process_token(TokenType.IDENTIFIER)
                self.process_rule(TokenType.SYMBOL, "(")
                arg_count = self.compile_expression_list()
                self.writer.write_call(
                    f"{class_type}.{subroutine_to_call}",
                    arg_count + 1 if class_index > -1 else arg_count,
                )
                self.process_rule(TokenType.SYMBOL, ")")
            else:
                class_type, class_kind, class_index = self.resolve_class_type_to_call(
                    current_token
                )
                self.writer.write_push(class_kind, class_index)
        if to_print:
            logger.debug("</term>")

    def compile_parameter_list(self) -> None:
        """
        Compiles a param list
        """
        logger.debug("<parameterList>")
        while self.tokenizer.peek() != ")":
            var_type = self.process_token("any")  # variable type
            var_name = self.process_token(TokenType.IDENTIFIER)  # variable name
            self.subroutine_symbol_table.define(
                var_name, var_type, SymbolKind.ARG.value
            )
            while self.tokenizer.peek() == ",":
                self.process_rule(TokenType.SYMBOL, ",")
                var_type = self.process_token("any")  # variable type
                var_name = self.process_token(TokenType.IDENTIFIER)  # variabble name
                self.subroutine_symbol_table.define(
                    var_name, var_type, SymbolKind.ARG.value
                )
        logger.debug("</parameterList>")

    def compile_class_var_dec(self) -> None:
        """
        Compiles class level variable declarations
        Similar to the subroutine level one
        """
        # static | field
        self.class_var_config["kind"] = (
            SegmentTypes.THIS.value
            if self.process_rule(TokenType.KEYWORD, "static", "field") == "field"
            else SegmentTypes.STATIC.value
        )
        self.class_var_config["type"] = self.process_token("any")  # variable type
        # variable name
        self.class_var_config["name"] = self.process_token(
            TokenType.IDENTIFIER
        )
        self.class_symbol_table.define(
            self.class_var_config["name"],
            self.class_var_config["type"],
            self.class_var_config["kind"],
        )
        logger.debug(
            f"Class Variable defined - var_name: {self.class_var_config["name"]}, var_type: {self.class_var_config["type"]}"
        )
        while self.tokenizer.peek() == ",":
            self.process_rule(TokenType.SYMBOL, ",")
            self.class_var_config["name"] = self.process_token(
                TokenType.IDENTIFIER
            )  # variable name
            self.class_symbol_table.define(
                self.class_var_config["name"],
                self.class_var_config["type"],
                self.class_var_config["kind"],
            )
            logger.debug(
                f"Class Variable defined - var_name: {self.class_var_config["name"]}, var_type: {self.class_var_config["type"]}"
            )
        self.process_rule(TokenType.SYMBOL, ";")

    def process_rule(self, type: str, *s) -> None:
        """
        Helper function 
        Ensures that argument 'type' matches the token's type we are getting
        Passing in argument S also ensures that the token we get must be a
        value from S
        """
        logger.debug("process_rule()")
        current_token = self.tokenizer.advance(False)
        current_type = self.tokenizer.token_type
        if current_token in s and current_type == type:
            if current_token in self.converted_symbols:
                logger.debug(
                    f"<{current_type.value}>{self.converted_symbols[current_token]}</{current_type.value}>\n"
                )
            else:
                logger.debug(
                    f"<{current_type.value}> {current_token} </{current_type.value}>\n"
                )
        else:
            raise ValueError(
                f"Current Token: {current_token}, Current Type: {current_type.name}, Expected Token: {s}, Expected Type: {type.name}"
            )
        return current_token

    def process_token(self, type: str) -> None:
        """
        Helper function
        Relaxed method where only the type matters. If type also does not matter,
        pass in 'any'
        """
        logger.debug("process_token()")
        current_token = self.tokenizer.advance(False).strip()
        current_type = self.tokenizer.token_type
        if current_token in self.converted_symbols:
            logger.debug(
                f"<{current_type.value}>{self.converted_symbols[current_token]}</{current_type.value}>\n"
            )
        elif current_type == TokenType.STRING_CONST:
            logger.debug(
                f"<{current_type.value}>{current_token}</{current_type.value}>\n"
            )
        elif type == "any" or current_type == type:
            logger.debug(
                f"<{current_type.value}> {current_token} </{current_type.value}>\n"
            )
        else:
            raise ValueError(
                f"Current Type: {current_type.name}, Expected Type: {type.name}"
            )
        return current_token

    def process_operator(self, op: str) -> None:
        """
        Helper function
        Converts binary operator symbols into VM
        """
        match op:
            case "+":
                self.writer.write_arithmetic("add")
            case "-":
                self.writer.write_arithmetic("sub")
            case "*":
                self.writer.write_call("Math.multiply", 2)
            case "/":
                self.writer.write_call("Math.divide", 2)
            case "&":
                self.writer.write_arithmetic("and")
            case "|":
                self.writer.write_arithmetic("or")
            case "<":
                self.writer.write_arithmetic("lt")
            case ">":
                self.writer.write_arithmetic("gt")
            case "=":
                self.writer.write_arithmetic("eq")

    def process_unary_operator(self, op: str) -> None:
        """
        Helper function
        Converts unary operator symbols into VM
        """
        match op:
            case "-":
                self.writer.write_arithmetic("neg")
            case "~":
                self.writer.write_arithmetic("not")

    def resolve_class_type_to_call(self, name: str) -> tuple:
        """
        Helper function
        Converts an identifier to the various semantics needed to make a call to it
        """
        if name in self.subroutine_symbol_table.table:
            return (
                self.subroutine_symbol_table.type_of(name),
                self.subroutine_symbol_table.kind_of(name),
                self.subroutine_symbol_table.index_of(name),
            )
        if name in self.class_symbol_table.table:
            return (
                self.class_symbol_table.type_of(name),
                self.class_symbol_table.kind_of(name),
                self.class_symbol_table.index_of(name),
            )
        return (name, -1, -1)
