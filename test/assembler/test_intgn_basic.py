import os
import unittest
from tempfile import NamedTemporaryFile

from assembler import driver


class TestIntegrationBasic(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.src_file = NamedTemporaryFile(
            delete=False,
            mode="w",
            newline="",
            suffix=".asm",
        )
        cls.src_file_name = cls.src_file.name
        cls.src_file.write(ASM)
        cls.src_file.close()

        cls.dest_file = NamedTemporaryFile(
            delete=False,
            mode="w",
            newline="",
            suffix=".hack",
        )
        cls.dest_file_name = cls.dest_file.name
        cls.dest_file.close()

        cls.dest_file_ans = NamedTemporaryFile(
            delete=False,
            mode="w",
            newline="",
            suffix=".hack",
        )
        cls.dest_file_ans_name = cls.dest_file_ans.name
        cls.dest_file_ans.write(HACK)
        cls.dest_file_ans.close()

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove(cls.src_file_name)
        os.remove(cls.dest_file_name)
        os.remove(cls.dest_file_ans_name)

    def test_integration(self) -> None:
        driver.main(self.src_file_name, self.dest_file_name)
        with open(self.dest_file_name) as dest_file, open(
            self.dest_file_ans_name,
        ) as dest_file_ans:
            self.assertListEqual(list(dest_file), list(dest_file_ans))


ASM = """// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/6/rect/Rect.asm

// Draws a rectangle at the top-left corner of the screen.
// The rectangle is 16 pixels wide and R0 pixels high.
// Usage: Before executing, put a value in R0.

   // If (R0 <= 0) goto END else n = R0
   @R0
   D=M
   @END
   D;JLE 
   @n
   M=D
   // addr = base address of first screen row
   @SCREEN
   D=A
   @addr
   M=D
(LOOP)
   // RAM[addr] = -1
   @addr
   A=M
   M=-1
   // addr = base address of next screen row
   @addr
   D=M
   @32
   D=D+A
   @addr
   M=D
   // decrements n and loops
   @n
   MD=M-1
   @LOOP
   D;JGT
(END)
   @END
   0;JMP
"""
HACK = """0000000000000000
1111110000010000
0000000000010111
1110001100000110
0000000000010000
1110001100001000
0100000000000000
1110110000010000
0000000000010001
1110001100001000
0000000000010001
1111110000100000
1110111010001000
0000000000010001
1111110000010000
0000000000100000
1110000010010000
0000000000010001
1110001100001000
0000000000010000
1111110010011000
0000000000001010
1110001100000001
0000000000010111
1110101010000111
"""
