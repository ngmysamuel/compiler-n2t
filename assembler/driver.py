import assembler.parser as parser
import assembler.code as code
import assembler.symboltable as symboltable

import sys

def assemble(src, dest):
  print("Initializing classes")
  c = code.Code()
  s = symboltable.SymbolTable()
  with parser.Parser(src, s) as p:
    while p.advance_first_pass(): # first pass
      pass
  with parser.Parser(src, s) as p, open(dest, 'w') as dest:
    while p.advance_second_pass(): # second pass
      ans = c.map(p)
      if ans:
        dest.write(ans + "\n")

def main(src, dest):
  print("Assembler staring from Command Line")
  assemble(src, dest)

if __name__ == "__main__":
  main(sys.argv[1], sys.argv[2])