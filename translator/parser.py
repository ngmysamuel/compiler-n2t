import os

class Parser:

  __slots__ = ("path", "src_file", "file_name", "current_line", "command_type", "arg1", "arg2", "arg3")

  def __init__(self, path):
    if ".vm" not in path:
      raise ValueError(f"Please load a file with extension .vm - attempted to load {path}")
    self.path = path
    self.reset()

  def reset(self):
    self.command_type = None
    self.arg1 = None
    self.arg2 = None

  def __enter__(self):
    self.src_file = open(self.path, "r")
    self.file_name = os.path.basename(self.src_file.name).replace(".vm", "")
    return self

  def __exit__(self, exc_type, exc_value, tb):
    if exc_type is not None:
       print(exc_type, exc_value, tb)
    self.path = None
    self.src_file.close()
    return True
  
  def clean_lines(self, line):
    """Sets the cleaned line into self.current_line. And returns True if its the end of the file, else, False"""
    if not line: # EOF
      self.current_line = ""
      return True

    line = line.strip() # Remove trailing and leading white spaces

    if len(line) == 0: # Empty line
      self.current_line = ""
      return False

    if "//" in line: # Comments
      position = line.index("//")
      if position == 0:
        self.current_line = ""
        return False # Entire line is a comment
      else:
        line = line[:position].strip()
    self.current_line = line.upper()
    return False

  def advance(self):
    current_line = self.src_file.readline()

    is_eof = self.clean_lines(current_line)
    if not self.current_line:
      self.reset()
      return not is_eof
    
    parts = self.current_line.split(" ")
    self.arg3 = None

    if len(parts) > 1:
      match parts[0]: # TODO: migrate to enum
        case "POP":
          self.command_type = "C_POP"
          self.arg2 = parts[2]
        case "PUSH":
          self.command_type = "C_PUSH"
          self.arg2 = parts[2]
      match parts[1]:
        case "LOCAL":
          self.arg1 = "LCL"
        case "ARGUMENT":
          self.arg1 = "ARG"
        case "STATIC":
          self.arg1 = f"{self.file_name}.{self.arg2}"
          self.arg2 = 0
          self.arg3 = "STATIC"
        case "TEMP":
          self.arg1 = "5"
          self.arg3 = "TEMP"
        case "POINTER":
          if parts[2] == "0":
            self.arg1 = "THIS"
          else:
            self.arg1 = "THAT"
          self.arg2 = 0
          self.arg3 = "POINTER"
        case _:
          self.arg1 = parts[1]
    else: # TODO: catch all for arithmetic, when functions + branching comes in, will need rework
      self.command_type = "C_ARITHMETIC"
      self.arg2 = parts[0]
      match parts[0]:
        case "NEG":
          self.arg1 = 1
        case "NOT":
          self.arg1 = 1
        case _:
          self.arg1 = 2

    return not is_eof


# Commands are always in 3 parts
# 1) is it a push or pop
# 2) which mem segment should it go to? This will decide the assembly's @xxx part
# 3) what is the offset to read off of
# 
# Code Structure
# 1) driver - needs to be called "VMTranslator.py"
# 2) Parser
# 3) CodeWriter







