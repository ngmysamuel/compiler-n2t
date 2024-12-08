# I have <expression> and <term> unneccessarily

from compiler.init_logging import logger
from compiler.symbol_table import SymbolTable

from compiler.enumerations.TokenType import TokenType
from compiler.enumerations.SubRoutineType import SubRoutineType
from compiler.enumerations.SymbolKind import SymbolKind
from compiler.enumerations.SegmentTypes import SegmentTypes

class CompilationEngine:

  def __init__(self, vmwriter):
    self.tokenizer = None
    self.operator_list = ["+","-","*","/","&","|","<",">","="]
    self.unary_operator_list = ["-", "~"]
    self.keyword_constant_list = ["true", "false", "null", "this"]
    self.converted_symbols = {"<": "&lt;", ">": "&gt;", "\"": "&quot;", "&": "&amp;"}
    self.term_global_counter = 0
    self.expression_global_counter = 0
    self.writer = vmwriter
    self.class_symbol_table = SymbolTable()
    self.subroutine_symbol_table = SymbolTable()
    self.class_name = None
    self.class_var_config = {}
    self.subroutine_config = {}
    self.operator = {}
    self.if_count = 0
    self.whilte_count = 0

  def set_tokenizer(self, t):
    self.tokenizer = t

  def compile(self):
    self.compile_class()

  def compile_class(self):
    self.process_rule(TokenType.KEYWORD, "class")
    self.class_name = self.process_token(TokenType.IDENTIFIER)
    self.process_rule(TokenType.SYMBOL, "{")
    while self.tokenizer.peek().lower() not in SubRoutineType:
      logger.debug(f"self.tokenizer.peek() not in SubRoutineType: {self.tokenizer.peek() not in SubRoutineType}. peek: {self.tokenizer.peek()}")
      self.compile_class_var_dec()
    while self.tokenizer.peek() != "}":
      self.compile_sub_routine_dec()
    self.process_rule(TokenType.SYMBOL, "}")

  def compile_sub_routine_dec(self):
    self.if_count = 0
    self.subroutine_config["type"] = self.process_rule(TokenType.KEYWORD, *[i.value for i in SubRoutineType]) # constructor | function | method
    self.subroutine_config["return_type"] = self.process_token("any") # void | type - can be either IDENTIFIER or KEYWORD
    self.subroutine_config["name"] = self.process_token(TokenType.IDENTIFIER) # subRoutine name
    if self.subroutine_config["type"] == SubRoutineType.METHOD.value:
      self.subroutine_symbol_table.define("this", self.class_name, SymbolKind.ARG.value) # add THIS to the ARG list
    self.process_rule(TokenType.SYMBOL, "(")
    self.compile_parameter_list()
    self.process_rule(TokenType.SYMBOL, ")")
    self.compile_sub_routine_body()

  def compile_sub_routine_body(self):
    logger.debug("<subroutineBody>")
    self.process_rule(TokenType.SYMBOL, "{")
    while self.tokenizer.peek() == "var":
      self.compile_var_dec()
    self.write_subroutine_signature()
    self.compile_statments()
    self.process_rule(TokenType.SYMBOL, "}")
    logger.debug("</subroutineBody>")

  def write_subroutine_signature(self):
    self.writer.write_function(f"{self.class_name}.{self.subroutine_config['name']}", self.subroutine_symbol_table.var_count(SymbolKind.VAR.value))
    if self.subroutine_config["type"] == SubRoutineType.METHOD.value:
      self.writer.write_push(SegmentTypes.ARGUMENT.value, 0) # push argument 0
      self.write.write_pop(SegmentTypes.POINTER, 0) # pop pointer 0 -> set THIS
    elif self.subroutine_config["type"] == SubRoutineType.CONSTRUCTOR.value:
      self.writer.write_push(SegmentTypes.CONSTANT.value, self.class_symbol_table.var_count(SymbolKind.FIELD.value)) # push constant numVar
      self.writer.write_call("Memory.alloc", 1) # call memory.alloc 1 -> allocate memory for object
      self.write.write_pop(SegmentTypes.POINTER, 0) # pop pointer 0 -> set THIS


  def compile_var_dec(self):
    logger.debug("<varDec>")
    self.process_rule(TokenType.KEYWORD, "var")
    var_type = self.process_token("any") # variable type - can be either IDENTIFIER or KEYWORD
    var_name = self.process_token(TokenType.IDENTIFIER) # variable name
    self.subroutine_symbol_table.define(var_name, var_type, SymbolKind.VAR)
    while self.tokenizer.peek() == ",":
      var_type = self.process_token("any") # variable type
      var_type = self.process_token(TokenType.IDENTIFIER) # variable name
      self.subroutine_symbol_table.define(var_name, var_type, SymbolKind.VAR)
    self.process_rule(TokenType.SYMBOL, ";")
    logger.debug("</varDec>")

  def compile_statments(self):
    logger.debug("<statements>")
    while self.tokenizer.peek() != "}":
      match self.tokenizer.peek():
        case "let":
          self.compile_let_statment()
        case "if":
          self.compile_if_statment()
        case "while":
          self.compile_while_statment()
        case "do":
          self.compile_do_statment()
        case "return":
          self.compile_return_statment()
    logger.debug("</statements>")

  def compile_let_statment(self):
    logger.debug("<letStatement>")
    is_assignment_to_array = False
    self.process_rule(TokenType.KEYWORD, "let")
    var_name = self.process_token(TokenType.IDENTIFIER)
    var_kind = self.subroutine_symbol_table.kind_of(var_name)
    var_idx = self.subroutine_symbol_table.index_of(var_name)
    _, class_kind, class_index = self.resolve_class_type_to_call(var_name)
    self.writer.write_push(class_kind, class_index)
    if self.tokenizer.peek() == "[": # LHS array
      self.process_rule(TokenType.SYMBOL, "[")
      self.compile_expression()
      self.process_rule(TokenType.SYMBOL, "]")
      self.writer.write_arithmetic("add")
      is_assignment_to_array = True
    self.process_rule(TokenType.SYMBOL, "=")
    self.compile_expression() # potentially RHS of the array
    if is_assignment_to_array:
      self.writer.write_pop(SegmentTypes.TEMP.value, 0) # place evaluated RHS into TEMP 0
      self.writer.write_pop(SegmentTypes.POINTER.value, 1) # align to the LHS array
      self.writer.write_push(SegmentTypes.TEMP.value, 0) # place TEMP 0 back onto the stack
      self.writer.write_pop(SegmentTypes.THAT.value, 0) # pop off the stack and into THAT
    else:
      self.writer.write_pop(var_kind, var_idx)
    self.process_rule(TokenType.SYMBOL, ";")
    logger.debug("</letStatement>")

  def compile_if_statment(self):
    logger.debug("<ifStatement>")
    self.process_rule(TokenType.KEYWORD, "if")
    self.process_rule(TokenType.SYMBOL, "(")
    self.compile_expression()
    self.writer.write_arithmetic("not")
    self.writer.write_if(f"{self.class_name}.{self.subroutine_config["name"]}.{self.if_count}.pathA") # go if not true
    self.process_rule(TokenType.SYMBOL, ")")
    self.process_rule(TokenType.SYMBOL, "{")
    self.compile_statments()
    self.writer.write_goto(f"{self.class_name}.{self.subroutine_config["name"]}.{self.if_count}.pathB") # skip statements for if not true
    self.process_rule(TokenType.SYMBOL, "}")
    if self.tokenizer.peek() == "else":
      self.process_rule(TokenType.KEYWORD, "else")
      self.process_rule(TokenType.SYMBOL, "{")
      self.writer.write_label(f"{self.class_name}.{self.subroutine_config["name"]}.{self.if_count}.pathA")
      self.compile_statments()
      self.process_rule(TokenType.SYMBOL, "}")
    self.writer.write_label(f"{self.class_name}.{self.subroutine_config["name"]}.{self.if_count}.pathB")
    logger.debug("</ifStatement>")
    self.if_count += 1

  def compile_while_statment(self):
    logger.debug("<whileStatement>")
    self.writer.write_label(f"{self.class_name}.{self.subroutine_config["name"]}.{self.if_count}.pathA") # top
    self.process_rule(TokenType.KEYWORD, "while")
    self.process_rule(TokenType.SYMBOL, "(")
    self.compile_expression()
    self.writer.write_arithmetic("not")
    self.writer.write_if(f"{self.class_name}.{self.subroutine_config["name"]}.{self.if_count}.pathB") # break
    self.process_rule(TokenType.SYMBOL, ")")
    self.process_rule(TokenType.SYMBOL, "{")
    self.compile_statments()
    self.writer.write_goto(f"{self.class_name}.{self.subroutine_config["name"]}.{self.if_count}.pathA") # back to top
    self.process_rule(TokenType.SYMBOL, "}")
    self.writer.write_label(f"{self.class_name}.{self.subroutine_config["name"]}.{self.if_count}.pathB") # break label
    logger.debug("</whileStatement>")

  def compile_do_statment(self):
    logger.debug("<doStatement>")
    self.process_rule(TokenType.KEYWORD, "do")
    self.compile_expression(False)
    self.process_rule(TokenType.SYMBOL, ";")
    self.writer.write_pop(SegmentTypes.TEMP.value, 0)
    logger.debug("</doStatement>")

  def compile_return_statment(self):
    logger.debug("<returnStatement>")
    self.process_rule(TokenType.KEYWORD, "return")
    if self.tokenizer.peek() != ";":
      self.compile_expression()
    if self.subroutine_config["return_type"] == "void":
      self.writer.write_push(SegmentTypes.CONSTANT.value, 0)
    self.writer.write_return()
    self.process_rule(TokenType.SYMBOL, ";")
    logger.debug("</returnStatement>")

  def compile_expression_list(self):
    count = 1
    logger.debug("<expressionList>")
    if self.tokenizer.peek() != ")": # end of expression list
      self.compile_expression()
      while self.tokenizer.peek() == ",":
        self.process_rule(TokenType.SYMBOL, ",")
        self.compile_expression()
        count += 1
    logger.debug("</expressionList>")
    return count

  def compile_expression(self, to_print = True):
    logger.debug(f"{self.expression_global_counter}.{self.term_global_counter} compile_expression()")
    self.expression_global_counter += 1
    if to_print:
      logger.debug("<expression>")
    self.compile_term(to_print)
    while self.tokenizer.peek() in self.operator_list:
      self.operator[len(self.operator) + 1] = self.process_rule(TokenType.SYMBOL, *self.operator_list)
      self.compile_term()
    while len(self.operator) > 0:
      self.process_operator(
        self.operator.pop(
          len(self.operator)
          )
        )

    if to_print:
      logger.debug("</expression>")

  def compile_term(self, to_print = True):
    logger.debug(f"{self.expression_global_counter}.{self.term_global_counter}. compile_term()")
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
        self.writer.write_call("String.appendChar", 1)
    elif current_token in self.keyword_constant_list:
      keyword_constant = self.process_rule(TokenType.KEYWORD, *self.keyword_constant_list)
      if keyword_constant == "true":
        self.writer.write_push(SegmentTypes.CONSTANT.value, 1)
        self.writer.write_arithmetic("neg")
      elif keyword_constant == "this":
        self.writer.write_push(SegmentTypes.POINTER.value, 0)
      else: # false | null
        self.writer.write_push(SegmentTypes.CONSTANT.value, 0)
    elif current_token == "(": # expression list
      self.process_rule(TokenType.SYMBOL, "(")
      self.compile_expression()
      self.process_rule(TokenType.SYMBOL, ")")
    elif current_token in self.unary_operator_list:
      unary_op = self.process_rule(TokenType.SYMBOL, *self.unary_operator_list)
      self.process_unary_operator(unary_op)
      self.compile_term()
    elif current_type == TokenType.IDENTIFIER:
      self.process_token(TokenType.IDENTIFIER)
      advance_token = self.tokenizer.peek()
      if advance_token == "[":
        class_type, class_kind, class_index = self.resolve_class_type_to_call(current_token)
        self.writer.write_push(class_kind, class_index) # push base address of array onto stack
        self.process_rule(TokenType.SYMBOL, "[")
        self.compile_expression() # resolve internals of []
        self.writer.write_arithmetic("add") # get address of where we are addressing
        self.process_rule(TokenType.SYMBOL, "]")
        self.writer.write_pop(SegmentTypes.POINTER.value, 1) # set THAT to where we are addressing
        self.writer.write_push(SegmentTypes.THAT.value, 0) # push value at THAT onto stack
      elif advance_token == "(":
        self.process_rule(TokenType.SYMBOL, "(")
        arg_count = self.compile_expression_list()
        if current_token not in self.class_symbol_table and current_token not in self.subroutine_symbol_table: # is a local method e.g. distance(p2)
          self.writer.write_push(SegmentTypes.ARGUMENT.value, 0) # push THIS onto the stack
          self.writer.write_call(f"{self.class_name}.{current_token}", arg_count)
        self.process_rule(TokenType.SYMBOL, ")")
      elif advance_token == ".": # is a method on an external class
        variable_to_call = current_token
        self.process_rule(TokenType.SYMBOL, ".")
        subroutine_to_call = self.process_token(TokenType.IDENTIFIER)
        self.process_rule(TokenType.SYMBOL, "(")
        arg_count = self.compile_expression_list()
        class_type, class_kind, class_index = self.resolve_class_type_to_call(variable_to_call)
        if class_index > -1:
          self.writer.write_push(class_kind, class_index) # push the class that the method is being called on
          arg_count += 1
        self.writer.write_call(f"{class_type}.{subroutine_to_call}", arg_count)
        self.process_rule(TokenType.SYMBOL, ")")
    if to_print:
      logger.debug("</term>")

  def compile_parameter_list(self):
    logger.debug("<parameterList>")
    while self.tokenizer.peek() != ")":
      var_type = self.process_token("any") # variable type
      var_name = self.process_token(TokenType.IDENTIFIER) # variable name
      self.subroutine_symbol_table.define(var_name, var_type, SymbolKind.ARG.value)
      while self.tokenizer.peek() == ",":
        self.process_rule(TokenType.SYMBOL, ",")
        var_type = self.process_token("any") # variable type
        var_name = self.process_token(TokenType.IDENTIFIER) # variabble name
        self.subroutine_symbol_table.define(var_name, var_type, SymbolKind.ARG.value)
    logger.debug("</parameterList>")

  def compile_class_var_dec(self):
    self.class_var_config["kind"] = self.process_rule(TokenType.KEYWORD, "static", "field") # static | field
    self.class_var_config["type"] = self.process_token("any") # variable type
    self.class_var_config["name"] = self.process_token(TokenType.IDENTIFIER) # variable name
    self.class_symbol_table.define(self.class_var_config["name"], self.class_var_config["type"], self.class_var_config["kind"])
    while self.tokenizer.peek() == ",":
      self.process_rule(TokenType.SYMBOL, ",")
      self.class_var_config["name"] = self.process_token(TokenType.IDENTIFIER) # variable name
      self.class_symbol_table.define(self.class_var_config["name"], self.class_var_config["type"], self.class_var_config["kind"])
    self.process_rule(TokenType.SYMBOL, ";")

  def process_rule(self, type, *s):
    logger.debug("process_rule()")
    current_token = self.tokenizer.advance(False)
    current_type = self.tokenizer.token_type
    if current_token in s and current_type == type:
      if current_token in self.converted_symbols:
        logger.debug(f"<{current_type.value}>{self.converted_symbols[current_token]}</{current_type.value}>\n")
      else:
        logger.debug(f"<{current_type.value}> {current_token} </{current_type.value}>\n")
    else:
      raise ValueError(f"Current Token: {current_token}, Current Type: {current_type.name}, Expected Token: {s}, Expected Type: {type.name}")
    return current_token
  
  def process_token(self, type):
    logger.debug("process_token()")
    current_token = self.tokenizer.advance(False).strip()
    current_type = self.tokenizer.token_type
    if current_token in self.converted_symbols:
      logger.debug(f"<{current_type.value}>{self.converted_symbols[current_token]}</{current_type.value}>\n")
    elif current_type == TokenType.STRING_CONST:
      logger.debug(f"<{current_type.value}>{current_token}</{current_type.value}>\n")
    elif type == "any" or current_type == type:
      logger.debug(f"<{current_type.value}> {current_token} </{current_type.value}>\n")
    else:
      raise ValueError(f"Current Type: {current_type.name}, Expected Type: {type.name}")
    return current_token

    # self.operator_list = ["+","-","*","/","&","|","<",">","="]
    # self.unary_operator_list = ["-", "~"]

  def process_operator(self, op):
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

  def process_unary_operator(self, op):
    match op:
      case "-":
        self.writer.write_arithmetic("neg")
      case "~":
        self.writer.write_arithmetic("not")

  def resolve_class_type_to_call(self, name):
    if name in self.subroutine_symbol_table.table:
      return (self.subroutine_symbol_table.type_of(name), self.subroutine_symbol_table.kind_of(name), self.subroutine_symbol_table.index_of(name))
    elif name in self.subroutine_symbol_table.table:
      return (self.class_symbol_table.type_of(name), self.class_symbol_table.kind_of(name), self.class_symbol_table.index_of(name))
    return (name, -1, -1)
  