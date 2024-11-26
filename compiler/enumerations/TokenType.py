from enum import Enum

class TokenType(Enum):
  SYMBOL = "symbol"
  KEYWORD = "keyword"
  IDENTIFIER = "identifier"
  INT_CONST = "intConst"
  STRING_CONST = "stringConst"