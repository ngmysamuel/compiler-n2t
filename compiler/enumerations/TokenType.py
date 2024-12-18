from enum import Enum


class TokenType(Enum):
    SYMBOL = "symbol"
    KEYWORD = "keyword"
    IDENTIFIER = "identifier"
    INT_CONST = "integerConstant"
    STRING_CONST = "stringConstant"
