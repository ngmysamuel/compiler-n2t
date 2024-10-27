import sys

from assembler import code, parser, symboltable


def assemble(src: str, dest: str) -> None:
    """Driver function.

    Args:
        src: Input assembly file to assemble into binary
        dest: Output binary file

    """
    print("Initializing classes")
    c = code.Code()
    s = symboltable.SymbolTable()
    with parser.Parser(src, s) as p:
        while p.advance_first_pass():  # first pass
            pass
    with parser.Parser(src, s) as p, open(dest, "w") as dest_file:
        while p.advance_second_pass():  # second pass
            ans = c.map(p)
            if ans:
                dest_file.write(ans + "\n")


def main(src: str, dest: str) -> None:
    """Entry function.

    Args:
        src: Input assembly file to assemble into binary
        dest: Output binary file

    """
    print("Assembler staring from Command Line")
    assemble(src, dest)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
