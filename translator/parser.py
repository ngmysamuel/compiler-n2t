import os

class Parser:

  __slots__ = ("paths", "src_file", "src_file_counter", "file_name", "func_name", "func_counter", "current_line", "command_type", "arg1", "arg2", "arg3")

  def __init__(self, path):
    print(f"> attempting to load {path}")
    if os.path.isfile(path):
      if ".vm" in path:
        self.paths = [path]
      else:
        raise ValueError(f"Please load a file with extension .vm - attempted to load {path}")
    else:
      print("> you are loading a directory")
      files_and_dirs = os.listdir(path)
      files = [os.path.join(path, file) for file in files_and_dirs if file[-3:] == ".vm"]
      if files:
        self.paths = files
      else:
        raise ValueError(f"No VM files found in directory. Please load a file with extension .vm - attempted to load {path}")
    self.src_file_counter = -1
    self.func_counter = 0
    self.reset()

  def reset(self):
    self.command_type = None
    self.arg1 = None
    self.arg2 = None
    self.arg3 = None
    self.func_name = None

  def __enter__(self):
    self.rotate_file()
    return self

  def __exit__(self, exc_type, exc_value, tb):
    if exc_type is not None:
       print(exc_type, exc_value, tb)
    self.paths = None
    self.src_file.close()
    return True
  
  def rotate_file(self):
    if self.src_file_counter < len(self.paths)-1:
      self.src_file_counter += 1
      self.src_file = open(self.paths[self.src_file_counter], "r")
      self.file_name = os.path.basename(self.src_file.name).replace(".vm", "").upper()
      print(f"> file rotated; now reading from {self.src_file.name}")
      return True
    return False

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
    if not self.current_line: # self.current_line is empty
      self.reset()
      if is_eof:
        return self.rotate_file() # we've rotated the file, return True if there are still more files to parse, else return False
      else:
        return True # is always not is_eof
    
    parts = self.current_line.split(" ")
    self.arg3 = None

    if len(parts) == 3: # PUSH/POP commands, FUNCTION commands, CALL commands
      self.arg2 = parts[2]
      match parts[0]: # TODO: migrate to enum
        case "POP":
          self.command_type = "C_POP"
        case "PUSH":
          self.command_type = "C_PUSH"
        case "FUNCTION":
          self.command_type = "C_FUNCTION"
          self.func_name = parts[1].upper()
        case "CALL":
          self.command_type = "C_CALL"
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
    elif len(parts) == 2: # BRANCHING commands
      match parts[0]:
        case "LABEL":
          self.command_type = "C_LABEL"
        case "GOTO":
          self.command_type = "C_GOTO"
        case "IF-GOTO":
          self.command_type = "C_IF"
      self.arg1 = parts[1]
    else: # ARITHMETIC/LOGICAL commands (arg1: no. of arguments; arg2: arithmetic/logical command), RETURN command
      self.command_type = "C_ARITHMETIC"
      self.arg2 = parts[0]
      match parts[0]:
        case "NEG":
          self.arg1 = 1
        case "NOT":
          self.arg1 = 1
        case "RETURN":
          self.command_type = "C_RETURN"
          self.arg2 = None
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








