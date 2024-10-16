import unittest
import assembler.parser as parser
import assembler.symboltable as symboltable

class TestParser(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.testSymboltableClass = symboltable.SymbolTable()
    cls.testParserClass = parser.Parser(".asm", cls.testSymboltableClass)

  def test_clean_lines(self):
    line_ls = [
      ("// This is a comment", False, ""),
      ("", True, ""),
      ("a+b // This is a comment with code", False, "a+b"),
      ("   a+b // This is a comment with code and leading space", False, "a+b")
    ]
    for line in line_ls:
      with self.subTest(line=line):
        b = self.testParserClass.clean_lines(line[0])
        self.assertEqual(b, line[1])
        self.assertEqual(self.testParserClass.current_line, line[2])