class SymbolTable:
    """Dictionary with various helper methods.

    Initializes a class level dictionary with pre-filled entries that is the Nand2Tetris
    convention.
    """

    hm = {
        "SP": "0",
        "LCL": "1",
        "ARG": "2",
        "THIS": "3",
        "THAT": "4",
        "R0": "0",
        "R1": "1",
        "R2": "2",
        "R3": "3",
        "R4": "4",
        "R5": "5",
        "R6": "6",
        "R7": "7",
        "R8": "8",
        "R9": "9",
        "R10": "10",
        "R11": "11",
        "R12": "12",
        "R13": "13 ",
        "R14": "14 ",
        "R15": "15 ",
        "SCREEN": "16384",
        "KBD": "24576",
    }

    def put(self, key: str, value: str) -> None:
        SymbolTable.hm[key] = value

    def __contains__(self, key: str) -> str:
        return key in SymbolTable.hm

    def __getitem__(self, key: str) -> str:
        if key in SymbolTable.hm:
            return SymbolTable.hm[key]
        return None
