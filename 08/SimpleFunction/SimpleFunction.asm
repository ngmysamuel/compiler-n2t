// FUNCTION SIMPLEFUNCTION.TEST 2
(SimpleFunction.SIMPLEFUNCTION.TEST)
@0
D=A // set the value in @value into D
@SP
A=M
M=D // push value onto stack
@SP
M=M+1 // increment stack pointer

@0
D=A // set the value in @value into D
@SP
A=M
M=D // push value onto stack
@SP
M=M+1 // increment stack pointer

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

// PUSH LOCAL 1
@1
D=A
@LCL
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

// NOT
@SP
A=M
A=A-1
M=!M

// PUSH ARGUMENT 0
@0
D=A
@ARG
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

// RETURN
@LCL
D=M
D=D-1
D=D-1
D=D-1
D=D-1
D=D-1
A=D
D=M // D now contains the return address
@R13
M=D // R13 now contains the return address
@SP
A=M-1
D=M // D now contains the return value
@ARG
A=M
M=D // Set D (return value) into ARG's location
@ARG
D=M // D now contains ARG's address
@SP
M=D+1 // Reposition SP to ARG plus 1

@LCL
D=M // store LCL's location into D. This is FRAME
@R14
M=D-1
A=M // set register to the address that holds the previous THAT's address
D=M // D contains the previous THAT's address
@THAT
M=D // rewrites THAT's location to the previous THAT's address

@R14
M=M-1
A=M // set register to the address that holds the previous THIS's address
D=M // D contains the previous THIS's address
@THIS
M=D // rewrites THIS's location to the previous THIS's address

@R14
M=M-1
A=M // set register to the address that holds the previous ARG's address
D=M // D contains the previous ARG's address
@ARG
M=D // rewrites THIS's location to the previous ARG's address

@R14
M=M-1
A=M // set register to the address that holds the previous LCL's address
D=M // D contains the previous LCL's address
@LCL
M=D // rewrites LCL's location to the previous LCL's address

@R13 // stores the return address
A=M
0;JMP // jumps to return address