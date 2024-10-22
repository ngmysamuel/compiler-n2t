import parser
import codewriter

import sys

def main(src_path):
  dest_path = src_path.replace(".vm", ".asm")
  c = codewriter.CodeWriter()
  with parser.Parser(src_path) as p, open(dest_path, 'w') as dest:
    while p.advance():
      ans = c.map(p)
      if ans:
        dest.write(f"\n// {p.current_line}\n")
        dest.write(ans.replace(" ", ""))

if __name__ == "__main__":
  main(sys.argv[1])