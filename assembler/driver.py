import sys
import os
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
    if os.path.isfile(src) and os.path.isfile(dest):
        with parser.Parser(src, s) as p:
            while p.advance_first_pass():  # first pass
                pass
        with parser.Parser(src, s) as p, open(dest, "w") as dest_file:
            while p.advance_second_pass():  # second pass
                ans = c.map(p)
                if ans:
                    dest_file.write(ans + "\n")
    elif os.path.isdir(src) and os.path.isdir(dest):
        files_and_dirs = os.listdir(src)
        files_to_process = [f for f in files_and_dirs if f[-4:] == ".asm"]
        for p in files_to_process:
            print(p)
            src_file_path = os.path.join(src, p)
            dest_file_path = os.path.join(src, p).replace(".asm", ".hack")
            print(f"src_file_path: {src_file_path}, dest_file_path:{dest_file_path}")
            with parser.Parser(src_file_path, s) as p:
                while p.advance_first_pass():  # first pass
                    pass
            with parser.Parser(src_file_path, s) as p, open(dest_file_path, "w") as dest_file:
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
