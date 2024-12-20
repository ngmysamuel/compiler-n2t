# import parser
# import codewriter

import os
import sys

from translator import codewriter, parser


def main(src_path, dest_path):
    """Driver function.

    Args:
        src_path: Input VM file to translate into assembly
        dest_path: Output ASM file containing assembly
    """
    src_path = "." if src_path is None else src_path
    src_path = os.path.abspath(src_path)
    if os.path.isfile(src_path):
        directory_name = os.path.basename(os.path.dirname(src_path))
    else:
        clean_path = src_path.rstrip(os.sep)
        directory_name = os.path.basename(clean_path)
    if dest_path is None:
        dest_path = os.path.join(os.path.dirname(src_path), f"{directory_name}.asm")
    elif os.path.isdir(dest_path):
        dest_path = os.path.join(dest_path, f"{directory_name}.asm")
    print(f"> reading from: {src_path}, writing to {dest_path}")
    c = codewriter.CodeWriter()

    if os.path.isdir(src_path):
        files_and_dirs = os.listdir(src_path)
        files_to_process = [f for f in files_and_dirs if f[-3:] == ".vm"]
        if len(files_to_process) > 1: # this peculiarity is for the course where bootstrapping is not well defined.
            # Bootstrap code
            bootstrap_parser = parser.Parser(src_path)
            bootstrap_parser.current_line = "call Sys.init 0"
            bootstrap_parser.command_type = "C_CALL"
            bootstrap_parser.file_name = "SYS"
            bootstrap_parser.arg1 = "SYS.INIT"
            bootstrap_parser.arg2 = "0"
            bootstrap_parser.func_name = "SYS.INIT"
            call_sys_init = c.map(bootstrap_parser)
            call_sys_init = strip_lines(call_sys_init)
            with open(dest_path, "w") as dest:
                dest.write(f"""
/////////// BOOTSTRAP CODE ///////////
// SP = 256
@256
D=A
@SP
M=D
// call Sys.init
{call_sys_init}
/////////// End of BOOTSTRAP CODE ///////////
              """)
            print("> bootstrap code written")

    # Actual code
    with parser.Parser(src_path) as p, open(dest_path, "a") as dest:
        while p.advance():
            ans = c.map(p)
            if ans:
                dest.write(f"\n\n// {p.current_line}\n")
                dest.write(strip_lines(ans))


def strip_lines(ans: str) -> str:
    """Strip white space.

    Strips all white space charaters while leaving comments as is.
    New line characters are added back after.
    """
    lines = ans.strip().split("\n")
    for counter, i in enumerate(lines):
        parts = i.strip().split("//")
        parts[0] = parts[0].replace(" ", "")
        lines[counter] = " //".join(parts)
    return "\n".join(lines)


if __name__ == "__main__":
    main(
        sys.argv[1], sys.argv[2]
    )  # TODO: allow for times when no arguments are passed - use current directory
