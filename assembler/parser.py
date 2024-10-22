class Parser:

  __slots__ = ("path", "src_file", "current_line", "instr_type", "sym", "dest", "comp", "jmp", "instruction_counter", "memory_counter", "symbolTable")

  def __init__(self, path, symbolTable):
    if ".asm" not in path:
      raise ValueError(f"Please load a file with extension .asm - attempted to load {path}")
    self.path = path
    self.instruction_counter = 0
    self.memory_counter = 16
    self.symbolTable = symbolTable
    self.reset()

  def reset(self):
    self.instr_type = None
    self.sym = None
    self.dest = None
    self.comp = None
    self.jmp = None

  def __enter__(self):
    self.src_file = open(self.path, "r")
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
    self.current_line = line
    return False

  def advance_first_pass(self):
    current_line = self.src_file.readline()

    is_eof = self.clean_lines(current_line)
    if self.current_line == "":
      return not is_eof

    if "(" == self.current_line[0]: # Label
      self.sym = self.current_line[1:-1]
      self.symbolTable.put(self.sym, str(self.instruction_counter))
    else: # A and C instructions
      self.instruction_counter += 1

    return not is_eof

  def advance_second_pass(self):
    current_line = self.src_file.readline()

    is_eof = self.clean_lines(current_line)
    if self.current_line == "":
      self.reset()
      return not is_eof

    self.reset()

    if "(" == self.current_line[0]: # Label
      return True

    elif "@" == self.current_line[0]: # A instruction
      self.instr_type = "A"
      self.sym = self.current_line[1:]
      if not self.sym.isnumeric():
        if self.sym not in self.symbolTable:
          self.symbolTable.put(self.sym, str(self.memory_counter))
          self.memory_counter += 1
        self.sym = self.symbolTable[self.sym]

    else:
      self.instr_type = "C" # C instruction
      if "=" in self.current_line and ";" in self.current_line:
        tmp = self.current_line.split("=")
        self.dest = tmp[0].strip()
        tmp = tmp[1].split(";")
        self.comp = tmp[0].strip()
        self.jmp = tmp[1].strip()
      elif "=" in self.current_line:
        tmp = self.current_line.split("=")
        self.dest = tmp[0].strip()
        self.comp = tmp[1].strip()
      elif ";" in self.current_line:
        tmp = self.current_line.split(";")
        self.comp = tmp[0].strip()
        self.jmp = tmp[1].strip()
      else:
        self.comp = self.current_line.strip()

    return not is_eof


