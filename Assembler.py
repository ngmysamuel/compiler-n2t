from Parser import Parser
from Code import Code
from SymbolTable import SymbolTable

import sys

def assemble(src, dest):
  print("Initializing classes")
  c = Code()
  s = SymbolTable()
  with Parser(src, s) as p:
    while p.advance_first_pass(): # first pass
      pass
  with Parser(src, s) as p, open(dest, 'w') as dest:
    while p.advance_second_pass(): # second pass
      ans = c.map(p)
      if ans:
        dest.write(ans + "\n")

def main(src, dest):
  print("Assembler staring from Command Line")
  assemble(src, dest)

if __name__ == "__main__":
  main(sys.argv[1], sys.argv[2])