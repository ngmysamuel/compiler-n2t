
// PUSH CONSTANT 111

@111
D=A
@SP
A=M
M=D
@SP
M=M+1

// PUSH CONSTANT 333

@333
D=A
@SP
A=M
M=D
@SP
M=M+1

// PUSH CONSTANT 888

@888
D=A
@SP
A=M
M=D
@SP
M=M+1

// POP STATIC 8

@0
D=A
@StaticTest.8
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

// POP STATIC 3

@0
D=A
@StaticTest.3
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

// POP STATIC 1

@0
D=A
@StaticTest.1
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

// PUSH STATIC 3

@0
D=A
@StaticTest.3
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1

// PUSH STATIC 1

@0
D=A
@StaticTest.1
A=D+A
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

// PUSH STATIC 8

@0
D=A
@StaticTest.8
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
