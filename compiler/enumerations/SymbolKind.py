from enum import Enum

class SymbolKind(Enum):
  STATIC = "static"
  FIELD = "field"
  ARG = "arg"
  VAR = "var"