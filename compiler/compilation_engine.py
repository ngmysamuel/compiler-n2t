# I have <expression> and <term> unneccessarily

from compiler.init_logging import logger

from compiler.enumerations.TokenType import TokenType
from compiler.enumerations.SubRoutineType import SubRoutineType

class CompilationEngine:

  def __init__(self, path):
    self.path = path
    self.tokenizer = None
    self.operator_list = ["+","-","*","/","&","|","<",">","+"]
    self.unary_operator_list = ["-", "~"]
    self.keyword_constant_list = ["true", "false", "null", "this"]
    self.converted_symbols = {"<": "&lt;", ">": "&gt;", "\"": "&quot;", "&": "&amp;"}
    self.term_global_counter = 0
    self.expression_global_counter = 0

  def __enter__(self):
    self.file = open(self.path, "w")
    return self

  def __exit__(self, exc_type, exc_value, tb):
    try:
      self.file.close()
    except:
      pass
    finally:
      logger.debug("Compilation Engine is closed")

  def set_tokenizer(self, t):
    self.tokenizer = t

  def compile(self):
    self.compile_class()

  def compile_class(self):
    self.file.write("<class>")
    self.process_rule(TokenType.KEYWORD, "class")
    self.process_token(TokenType.IDENTIFIER)
    self.process_rule(TokenType.SYMBOL, "{")
    while self.tokenizer.peek().lower() not in SubRoutineType:
      logger.debug(f"self.tokenizer.peek() not in SubRoutineType: {self.tokenizer.peek() not in SubRoutineType}. peek: {self.tokenizer.peek()}")
      self.compile_class_var_dec()
    while self.tokenizer.peek() != "}":
      self.compile_sub_routine_dec()
    self.process_rule(TokenType.SYMBOL, "}")
    self.file.write("</class>")

  def compile_sub_routine_dec(self):
    self.file.write("<subroutineDec>")
    self.process_rule(TokenType.KEYWORD, *[i.value for i in SubRoutineType]) # constructor | function | method
    self.process_token("any") # void | type - can be either IDENTIFIER or KEYWORD
    self.process_token(TokenType.IDENTIFIER) # subRoutine name
    self.process_rule(TokenType.SYMBOL, "(")
    self.compile_parameter_list()
    self.process_rule(TokenType.SYMBOL, ")")
    self.compile_sub_routine_body()
    self.file.write("</subroutineDec>")

  def compile_sub_routine_body(self):
    self.file.write("<subroutineBody>")
    self.process_rule(TokenType.SYMBOL, "{")
    while self.tokenizer.peek() == "var":
      self.compile_var_dec()
    self.compile_statments()
    self.process_rule(TokenType.SYMBOL, "}")
    self.file.write("</subroutineBody>")

  def compile_var_dec(self):
    self.file.write("<varDec>")
    self.process_rule(TokenType.KEYWORD, "var")
    self.process_token("any") # variable type - can be either IDENTIFIER or KEYWORD
    self.process_token(TokenType.IDENTIFIER) # variable name
    while self.tokenizer.peek() == ",":
      self.process_token("any") # variable type
      self.process_token(TokenType.IDENTIFIER) # variable name
    self.process_rule(TokenType.SYMBOL, ";")
    self.file.write("</varDec>")

  def compile_statments(self):
    self.file.write("<statements>")
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
    self.file.write("</statements>")

  def compile_let_statment(self):
    self.file.write("<letStatement>")
    self.process_rule(TokenType.KEYWORD, "let")
    self.process_token(TokenType.IDENTIFIER)
    if self.tokenizer.peek() == "[":
      self.process_rule(TokenType.SYMBOL, "[")
      self.compile_expression()
      self.process_rule(TokenType.SYMBOL, "]")
    self.process_rule(TokenType.SYMBOL, "=")
    self.compile_expression()
    self.process_rule(TokenType.SYMBOL, ";")
    self.file.write("</letStatement>")

  def compile_if_statment(self):
    self.file.write("<ifStatement>")
    self.process_rule(TokenType.KEYWORD, "if")
    self.process_rule(TokenType.SYMBOL, "(")
    self.compile_expression()
    self.process_rule(TokenType.SYMBOL, ")")
    self.process_rule(TokenType.SYMBOL, "{")
    self.compile_statments()
    self.process_rule(TokenType.SYMBOL, "}")
    if self.tokenizer.peek() == "else":
      self.process_rule(TokenType.KEYWORD, "else")
      self.process_rule(TokenType.SYMBOL, "{")
      self.compile_statments()
      self.process_rule(TokenType.SYMBOL, "}")
    self.file.write("</ifStatement>")

  def compile_while_statment(self):
    self.file.write("<whileStatement>")
    self.process_rule(TokenType.KEYWORD, "while")
    self.process_rule(TokenType.SYMBOL, "(")
    self.compile_expression()
    self.process_rule(TokenType.SYMBOL, ")")
    self.process_rule(TokenType.SYMBOL, "{")
    self.compile_statments()
    self.process_rule(TokenType.SYMBOL, "}")
    self.file.write("</whileStatement>")

  def compile_do_statment(self):
    self.file.write("<doStatement>")
    self.process_rule(TokenType.KEYWORD, "do")
    self.compile_expression(False)
    self.process_rule(TokenType.SYMBOL, ";")
    self.file.write("</doStatement>")

  def compile_return_statment(self):
    self.file.write("<returnStatement>")
    self.process_rule(TokenType.KEYWORD, "return")
    if self.tokenizer.peek() != ";":
      self.compile_expression()
    self.process_rule(TokenType.SYMBOL, ";")
    self.file.write("</returnStatement>")

  def compile_expression_list(self):
    self.file.write("<expressionList>")
    if self.tokenizer.peek() != ")": # end of expression list
      self.compile_expression()
      while self.tokenizer.peek() == ",":
        self.process_rule(TokenType.SYMBOL, ",")
        self.compile_expression()
    self.file.write("</expressionList>")

  def compile_term(self, to_print = True):
    logger.debug(f"{self.expression_global_counter}.{self.term_global_counter}. compile_term()")
    self.term_global_counter += 1
    if to_print:
      self.file.write("<term>")
    current_token = self.tokenizer.peek()
    current_type = self.tokenizer.token_type
    if current_type == TokenType.INT_CONST:
      self.process_token(TokenType.INT_CONST)
    elif current_type == TokenType.STRING_CONST:
      self.process_token(TokenType.STRING_CONST)
    elif current_token in self.keyword_constant_list:
      self.process_rule(TokenType.KEYWORD, *self.keyword_constant_list)
    elif current_token == "(": # expression list
      self.process_rule(TokenType.SYMBOL, "(")
      self.compile_expression_list()
      self.process_rule(TokenType.SYMBOL, ")")
    elif current_token in self.unary_operator_list:
      self.process_rule(TokenType.SYMBOL, *self.unary_operator_list)
      self.compile_term()
    elif current_type == TokenType.IDENTIFIER:
      self.process_token(TokenType.IDENTIFIER)
      advance_token = self.tokenizer.peek()
      if advance_token == "[":
        self.process_rule(TokenType.SYMBOL, "[")
        self.compile_expression()
        self.process_rule(TokenType.SYMBOL, "]")
      elif advance_token == "(":
        self.process_rule(TokenType.SYMBOL, "(")
        self.compile_expression_list()
        self.process_rule(TokenType.SYMBOL, ")")
      elif advance_token == ".":
        self.process_rule(TokenType.SYMBOL, ".")
        self.process_token(TokenType.IDENTIFIER)
        self.process_rule(TokenType.SYMBOL, "(")
        self.compile_expression_list()
        self.process_rule(TokenType.SYMBOL, ")")
    if to_print:
      self.file.write("</term>")

  def compile_expression(self, to_print = True):
    logger.debug(f"{self.expression_global_counter}.{self.term_global_counter} compile_expression()")
    self.expression_global_counter += 1
    if to_print:
      self.file.write("<expression>")
    self.compile_term(to_print)
    while self.tokenizer.peek() in self.operator_list:
      self.process_rule(TokenType.SYMBOL, *self.operator_list)
      self.compile_term()
    if to_print:
      self.file.write("</expression>")

  def compile_parameter_list(self):
    self.file.write("<parameterList>")
    while self.tokenizer.peek() != ")":
      self.process_token("any") # variable type
      self.process_token(TokenType.IDENTIFIER) # variable name
      while self.tokenizer.peek() == ",":
        self.process_rule(TokenType.SYMBOL, ",")
        self.process_token(TokenType.KEYWORD)
        self.process_token(TokenType.IDENTIFIER)
    self.file.write("</parameterList>")

  def compile_class_var_dec(self):
    self.file.write("<classVarDec>")
    self.process_rule(TokenType.KEYWORD, "static", "field") # static | field
    self.process_token("any") # variable type
    self.process_token(TokenType.IDENTIFIER) # variable name
    while self.tokenizer.peek() == ",":
      self.process_rule(TokenType.SYMBOL, ",")
      self.process_token(TokenType.IDENTIFIER)
    self.process_rule(TokenType.SYMBOL, ";")
    self.file.write("</classVarDec>")

  def process_rule(self, type, *s):
    logger.debug("process_rule()")
    current_token = self.tokenizer.advance(False)
    current_type = self.tokenizer.token_type
    if current_token in s and current_type == type:
      if current_token in self.converted_symbols:
        self.file.write(f"<{current_type.value}>{self.converted_symbols[current_token]}</{current_type.value}>\n")
      else:
        self.file.write(f"<{current_type.value}> {current_token} </{current_type.value}>\n")
    else:
      raise ValueError(f"Current Token: {current_token}, Current Type: {current_type.name}, Expected Token: {s}, Expected Type: {type.name}")
    return current_token
  
  def process_token(self, type):
    logger.debug("process_token()")
    current_token = self.tokenizer.advance(False).strip()
    current_type = self.tokenizer.token_type
    if current_token in self.converted_symbols:
      self.file.write(f"<{current_type.value}>{self.converted_symbols[current_token]}</{current_type.value}>\n")
    elif current_type == TokenType.STRING_CONST:
      self.file.write(f"<{current_type.value}>{current_token}</{current_type.value}>\n")
    elif type == "any" or current_type == type:
      self.file.write(f"<{current_type.value}> {current_token} </{current_type.value}>\n")
    else:
      raise ValueError(f"Current Type: {current_type.name}, Expected Type: {type.name}")
    return current_token