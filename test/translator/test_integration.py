import unittest
from tempfile import NamedTemporaryFile
import os

import translator.VMTranslator as vmt

class TestIntegration(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.src_file = NamedTemporaryFile(
      delete=False,
      mode="w",
      newline="",
      suffix=".vm",
    )
    cls.src_file_name = cls.src_file.name
    cls.src_file.write(VM)
    cls.src_file.close()

    cls.dest_file_ans = NamedTemporaryFile(
      delete=False,
      mode="w",
      newline="",
      suffix=".asm",
    )
    cls.dest_file_ans_name = cls.dest_file_ans.name
    cls.dest_file_ans.write(ASM)
    cls.dest_file_ans.close()

    cls.dest_file_name = cls.src_file_name.replace(".vm", ".asm")

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.temp_file_name)
        os.remove(cls.dest_file_name)
        os.remove(cls.dest_file_ans_name)

  def test_integration(self):
    vmt.main(self.src_file_name)
    with open(self.dest_file_name) as dest_file, open(self.dest_file_ans_name) as dest_file_ans:
      self.assertListEqual(list(dest_file), list(dest_file_ans))

VM = """// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/7/MemoryAccess/BasicTest/BasicTest.vm

// Executes pop and push commands.

push constant 10
pop local 0
push constant 21
push constant 22
pop argument 2
pop argument 1
push constant 36
pop this 6
push constant 42
push constant 45
pop that 5
pop that 2
push constant 510
pop temp 6
push local 0
push that 5
add
push argument 1
sub
push this 6
push this 6
add
sub
push temp 6
add
"""

ASM = """
// PUSH CONSTANT 10

@10
D=A
@SP
A=M
M=D
@SP
M=M+1

// POP LOCAL 0

@0
D=A
@LCL
D=D+M
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D

// PUSH CONSTANT 21

@21
D=A
@SP
A=M
M=D
@SP
M=M+1

// PUSH CONSTANT 22

@22
D=A
@SP
A=M
M=D
@SP
M=M+1

// POP ARGUMENT 2

@2
D=A
@ARG
D=D+M
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D

// POP ARGUMENT 1

@1
D=A
@ARG
D=D+M
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D

// PUSH CONSTANT 36

@36
D=A
@SP
A=M
M=D
@SP
M=M+1

// POP THIS 6

@6
D=A
@THIS
D=D+M
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D

// PUSH CONSTANT 42

@42
D=A
@SP
A=M
M=D
@SP
M=M+1

// PUSH CONSTANT 45

@45
D=A
@SP
A=M
M=D
@SP
M=M+1

// POP THAT 5

@5
D=A
@THAT
D=D+M
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D

// POP THAT 2

@2
D=A
@THAT
D=D+M
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D

// PUSH CONSTANT 510

@510
D=A
@SP
A=M
M=D
@SP
M=M+1

// POP TEMP 6

@6
D=A
@5
D=D+A
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D

// PUSH LOCAL 0

@0
D=A
@LCL
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1

// PUSH THAT 5

@5
D=A
@THAT
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1

// ADD

@SP
A=M
A=A-1
D=M
A=A-1
M=D+M
@SP
M=M-1

// PUSH ARGUMENT 1

@1
D=A
@ARG
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1

// SUB

@SP
A=M
A=A-1
D=M
A=A-1
M=M-D
@SP
M=M-1

// PUSH THIS 6

@6
D=A
@THIS
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1

// PUSH THIS 6

@6
D=A
@THIS
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1

// ADD

@SP
A=M
A=A-1
D=M
A=A-1
M=D+M
@SP
M=M-1

// SUB

@SP
A=M
A=A-1
D=M
A=A-1
M=M-D
@SP
M=M-1

// PUSH TEMP 6

@6
D=A
@5
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1

// ADD

@SP
A=M
A=A-1
D=M
A=A-1
M=D+M
@SP
M=M-1
"""

