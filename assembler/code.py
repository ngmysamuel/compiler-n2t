"""Outputs binary.

Using the Parser class that was initialized and set in a previous step, it will return
the relevant binary for that assmbly command
"""

from assembler import parser


class Code:
    def map(self, p: parser.Parser) -> str:
        """Forms up binary given various pieces of information from the Parser class.

        If the instruction type is "L", return None.
        If the instruction type is "A", converts parser.sym to binary and return
        If the instruction type is "C", makes use of parser.comp, parser.dest, and
        parser.jmp to form up the relevant binary

        Args:
            p: Pass in a Parser class which has been initialized with the relevant
            information from a previous step

        Returns:
            A binary string that is the conversion of the assembly string

        """
        if p.instr_type == "L":
            pass
        elif p.instr_type == "A":
            return "0" + self.dec_to_bin(int(p.sym), 15)
        elif p.instr_type == "C":
            prefix = "111"

            match p.comp:
                case "0":
                    comp = "0101010"
                case "1":
                    comp = "0111111"
                case "-1":
                    comp = "0111010"
                case "D":
                    comp = "0001100"
                case "A":
                    comp = "0110000"
                case "!D":
                    comp = "0001101"
                case "!A":
                    comp = "0110001"
                case "-D":
                    comp = "0001111"
                case "-A":
                    comp = "0110011"
                case "D+1":
                    comp = "0011111"
                case "A+1":
                    comp = "0110111"
                case "D-1":
                    comp = "0001110"
                case "A-1":
                    comp = "0110010"
                case "D+A":
                    comp = "0000010"
                case "D-A":
                    comp = "0010011"
                case "A-D":
                    comp = "0000111"
                case "D&A":
                    comp = "0000000"
                case "D|A":
                    comp = "0010101"
                case "M":
                    comp = "1110000"
                case "!M":
                    comp = "1110001"
                case "-M":
                    comp = "1110011"
                case "M+1":
                    comp = "1110111"
                case "M-1":
                    comp = "1110010"
                case "D+M":
                    comp = "1000010"
                case "D-M":
                    comp = "1010011"
                case "M-D":
                    comp = "1000111"
                case "D&M":
                    comp = "1000000"
                case "D|M":
                    comp = "1010101"
                case _:
                    comp = ""

            match p.dest:
                case "M":
                    dest = "001"
                case "D":
                    dest = "010"
                case "MD":
                    dest = "011"
                case "A":
                    dest = "100"
                case "AM":
                    dest = "101"
                case "AD":
                    dest = "110"
                case "AMD":
                    dest = "111"
                case _:
                    dest = "000"

            match p.jmp:
                case "JGT":
                    jmp = "001"
                case "JEQ":
                    jmp = "010"
                case "JGE":
                    jmp = "011"
                case "JLT":
                    jmp = "100"
                case "JNE":
                    jmp = "101"
                case "JLE":
                    jmp = "110"
                case "JMP":
                    jmp = "111"
                case _:
                    jmp = "000"
            return prefix + comp + dest + jmp
        return None

    def dec_to_bin(self, dec: int, padding_width: int) -> str:
        """Convert decimal into binary.

        Args:
            dec: The value in decimal to be converted into binary
            padding_width: Sets a width that the resulting binary must have

        Returns:
            The value in binary, padded with 0 up to "padding_width"

        """
        binary = bin(dec)[2:]
        return binary.rjust(padding_width, "0")
