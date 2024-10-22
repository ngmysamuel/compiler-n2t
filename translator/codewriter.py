class CodeWriter:

  __slots__ = ("cmp_counter")

  def __init__(self):
    self.cmp_counter = 0

  def map(self, p):
    ans = ""
    if p.command_type is None:
      return ans
    elif p.command_type == "C_POP":
      if p.arg3 in ("TEMP", "POINTER", "STATIC"): # POP TEMP xxx OR POP POINTER xxx OR POP STATIC xxx
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
      else: # POP xxx xxx
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
      if p.arg1 == "CONSTANT": # PUSH CONSTANT xxx
        ans = f"""
              @{p.arg2}
              D=A
              @SP
              A=M
              M=D
              @SP
              M=M+1
              """
      elif p.arg3 in ("TEMP", "POINTER", "STATIC"): # PUSH TEMP xxx OR PUSH POINTER xxx OR PUSH STATIC xxx
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
      else: # PUSH xxx xxx
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
        if p.arg2 == "NEG": # NEG
          ans = f"""
                @SP
                A=M
                A=A-1
                M=-M
                """
        else: # NOT
          ans = f"""
                @SP
                A=M
                A=A-1
                M=!M
                """
      else: # P.ARG1 == 2:
        op = ""
        match p.arg2:
          case "ADD": # ADD
            op = "M=D+M"
          case "SUB": # SUB
            op = "M=M-D"
          case "EQ" | "GT" | "LT": # EQ, GT, LT
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
          case "AND": # AND
            op = f"""
                  M=D&M
                  """
          case "OR": # OR
            op = f"""
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

    return ans