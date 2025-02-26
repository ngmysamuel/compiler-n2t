from translator import parser


class CodeWriter:
    __slots__ = ("cmp_counter", )

    def __init__(self) -> None:
        self.cmp_counter = 0

    def map(self, p: parser.Parser) -> str:
        """Map VM code into Assembly.

        This method first breaks down according to command type e.g. if its a POP
        command, a PUSH command, etc
        Within each if block, there are additional conditions to catch specific
        scenarios that need special handling
        For example, if its an Arithmetic command, there can be 2 types (unary and
        binary). Pushing a CONSTANT is also different from pushing a TEMP.

        """
        ans = ""
        if p.command_type is None:
            return ans

        if p.command_type == "C_POP":
            if p.arg3 in (
                "TEMP",
                "POINTER",
                "STATIC",
            ):  # POP TEMP xxx OR POP POINTER xxx OR POP STATIC xxx
                ans = f"""
              @{p.arg2}
              D=A
              @{p.arg1}
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
              """
            else:  # POP xxx xxx
                ans = f"""
              @{p.arg2}
              D=A
              @{p.arg1}
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
              """
        elif p.command_type == "C_PUSH":
            if p.arg1 == "CONSTANT":  # PUSH CONSTANT xxx
                ans = f"""
              @{p.arg2}
              D=A
              @SP
              A=M
              M=D
              @SP
              M=M+1
              """
            elif p.arg3 in (
                "TEMP",
                "POINTER",
                "STATIC",
            ):  # PUSH TEMP xxx OR PUSH POINTER xxx OR PUSH STATIC xxx
                ans = f"""
              @{p.arg2}
              D=A
              @{p.arg1}
              A=D+A
              D=M
              @SP
              A=M
              M=D
              @SP
              M=M+1
              """
            else:  # PUSH xxx xxx
                ans = f"""
              @{p.arg2}
              D=A
              @{p.arg1}
              A=D+M
              D=M
              @SP
              A=M
              M=D
              @SP
              M=M+1
              """
        elif p.command_type == "C_ARITHMETIC":
            if p.arg1 == 1:
                if p.arg2 == "NEG":  # NEG
                    ans = """
                @SP
                A=M
                A=A-1
                M=-M
                """
                else:  # NOT
                    ans = """
                @SP
                A=M
                A=A-1
                M=!M
                """
            else:  # P.ARG1 == 2:
                op = ""
                match p.arg2:
                    case "ADD":  # ADD
                        op = "M=D+M"
                    case "SUB":  # SUB
                        op = "M=M-D"
                    case "EQ" | "GT" | "LT":  # EQ, GT, LT
                        op = f"""
                D=M-D
                @EQ.{self.cmp_counter}
                D;J{p.arg2}
                @SP
                A=M-1
                A=A-1
                M=0
                @DN.{self.cmp_counter}
                0;JMP
                (EQ.{self.cmp_counter})
                @SP
                A=M-1
                A=A-1
                M=-1
                (DN.{self.cmp_counter})
                """
                        self.cmp_counter += 1
                    case "AND":  # AND
                        op = """
                  M=D&M
                  """
                    case "OR":  # OR
                        op = """
                  M=D|M
                  """
                ans = f"""
              @SP
              A=M
              A=A-1
              D=M
              A=A-1
              {op}
              @SP
              M=M-1
              """
        elif p.command_type == "C_LABEL":  # LABEL xxx
            ans = f"({p.func_name}${p.arg1})"
        elif p.command_type == "C_GOTO":  # GOTO xxx
            ans = f"""
            @{p.func_name}${p.arg1}
            0;JMP
            """
        elif p.command_type == "C_IF":  # IF-GOTO xxx
            ans = f"""
            @SP
            M=M-1
            @SP
            A=M
            D=M
            @{p.func_name}${p.arg1}
            D;JNE
            """
        elif p.command_type == "C_CALL":
            ans_rt_add = self.push_value_onto_stack(f"{p.arg1}$ret.{p.func_counter}")
            ans_lcl = self.push_address_onto_stack("LCL")
            ans_arg = self.push_address_onto_stack("ARG")
            ans_this = self.push_address_onto_stack("THIS")
            ans_that = self.push_address_onto_stack("THAT")
            ans_new_arg = self.complex_arith("SP", "sub", 5 + int(p.arg2))
            ans = f"""
            // store return address
            {ans_rt_add}
            // store LCL address
            {ans_lcl}
            // store ARG address
            {ans_arg}
            // store THIS address
            {ans_this}
            // store THAT address
            {ans_that}
            // set new ARG location
            {ans_new_arg} // ARG = SP - 5 - nArgs
            @ARG
            M=D // D register contains the new ARG address after assembly generated by complex_arith() was called
            // Set LCL to SP
            @SP
            D=M
            @LCL
            M=D
            // GOTO function
            @{p.arg1}
            0;JMP // jump to function
            ({p.arg1}$ret.{p.func_counter}) // return point
            """
            p.func_counter += 1
        elif p.command_type == "C_RETURN":
            ans_sub = self.complex_arith("LCL", "sub", 5)
            ans = f"""
            // Get return address
            {ans_sub}
            A=D
            D=M // D now contains the return address
            @R13
            M=D // R13 now contains the return address

            // Repositions return value for the caller
            @SP
            A=M-1
            D=M // D now contains the return value
            @ARG
            A=M
            M=D // Set D (return value) into ARG's location

            // Reposition SP to ARG plus 1
            @ARG
            D=M // D now contains ARG's address
            @SP
            M=D+1

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

            @R13 // contains the return address
            A=M
            0;JMP // jumps to return address
            """
        elif p.command_type == "C_FUNCTION":
            ans_temp = ""
            for _ in range(int(p.arg2)):
                ans_temp += f"{self.push_value_onto_stack(0)}"
            ans = f"""
            ({p.func_name}){ans_temp}
            """
        return ans

    def push_value_onto_stack(self, value: str) -> str:
        """Pushes value onto stack.

        Pushes the value inside of the register pointed to by address onto the stack.
        Then, increments the stack pointer
        """
        return f"""
            @{value}
            D=A // set the value in @value into D
            @SP
            A=M
            M=D // push value onto stack
            @SP
            M=M+1 // increment stack pointer
            """

    def push_address_onto_stack(self, address: str) -> str:
        """Pushes value onto stack.

        Pushes the value inside of the register pointed to by address onto the stack.
        Then, increments the stack pointer
        """
        return f"""
            @{address}
            D=M // set the value held by @value into D
            @SP
            A=M
            M=D // push value onto stack
            @SP
            M=M+1 // increment stack pointer
            """

    def complex_arith_address(self, address: str, op: str, times: int) -> str:
        """Operate on a value.

        Uses the value inside of the register pointed to by address. Resulting value
        will be found in the D register.

        Args:
          address: The value that will be set into the A register using @
          op: The operation that needs to take place on the value. Only supports
          subtract now.
          times: Number of times the operation should take place

        """
        ans = f"""
          @{address}
          A=M
          D=M"""
        for _ in range(times):
            match op:
                case "sub":
                    ans += "\nD=D-1"
        return ans

    def complex_arith(self, value: str, op: str, times: int) -> int:
        """Operate on a value.

        Resulting value will be found in the D register.

        Args:
          value: Set into the A register using @
          op: The operation that needs to take place on the value. Only supports
          subtract now.
          times: Number of times the operation should take place

        """
        ans = f"""
          @{value}
          D=M"""
        for _ in range(times):
            match op:
                case "sub":
                    ans += "\nD=D-1"
        return ans
