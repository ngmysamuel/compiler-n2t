from enum import Enum


class SymbolKind(Enum):
    STATIC = "static"
    FIELD = "field"
    ARG = "argument"
    VAR = "var"
