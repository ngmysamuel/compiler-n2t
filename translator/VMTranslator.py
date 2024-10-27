# import parser
# import codewriter

import translator.parser as parser
import translator.codewriter as codewriter

import sys
import os

def main(src_path):
  if os.path.isfile(src_path):
    dest_path = src_path.replace(".vm", ".asm")
  else:
    dest_path = os.path.join(os.path.abspath(src_path), f"{os.path.basename(src_path)}.asm")
  print(f"> writing to {dest_path}")
  c = codewriter.CodeWriter()

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
  with parser.Parser(src_path) as p, open(dest_path, 'a') as dest:
    while p.advance():
      ans = c.map(p)
      if ans:
        dest.write(f"\n\n// {p.current_line}\n")
        dest.write(strip_lines(ans))

def strip_lines(ans):
  lines = ans.strip().split("\n")
  for counter, i in enumerate(lines):
    parts = i.strip().split("//")
    parts[0] = parts[0].replace(" ", "")
    lines[counter] = " //".join(parts)
  ans = "\n".join(lines)
  return ans

if __name__ == "__main__":
  main(sys.argv[1]) # TODO: allow for times when no arguments are passed - use current directory