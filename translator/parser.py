import contextlib
import os


class Parser:
    __slots__ = (
        "paths",
        "src_file",
        "src_file_counter",
        "file_name",
        "func_name",
        "func_counter",
        "current_line",
        "command_type",
        "arg1",
        "arg2",
        "arg3",
    )

    def __init__(self, path: str) -> None:
        """Initialize the Parser with path(s) to the VM file(s).

        Takes the supplied path and decides if its a single file or a directory.
        If its the former, sets it into the attribute: paths
        If its the latter, scans the directory for all VM files and sets them into the
        attribute: paths.

        """
        print(f"> attempting to load {path}")
        if os.path.isfile(path):
            if ".vm" in path:
                self.paths = [path]
            else:
                msg = f"Please load a file with extension .vm - attempted to \
                        load {path}"
                raise ValueError(
                    msg,
                )
        else:
            print("> you are loading a directory")
            files_and_dirs = os.listdir(path)
            files = [
                os.path.join(path, file)
                for file in files_and_dirs
                if file[-3:] == ".vm"
            ]
            if files:
                files.sort()  # for deterministic output
                self.paths = files
            else:
                msg = f"No VM files found in directory. Please load a file with \
                        extension .vm - attempted to load {path}"
                raise ValueError(
                    msg,
                )
        self.src_file_counter = -1
        self.func_counter = 0
        self.reset()

    def reset(self):
        self.command_type = None
        self.arg1 = None
        self.arg2 = None
        self.arg3 = None
        self.func_name = None

    def __enter__(self) -> "Parser":
        """Create Parser.

        When creating parser using "with" method, sets src_file using the rotate method.

        """
        self.rotate_file()
        return self

    def __exit__(self, exc_type, exc_value, tb) -> bool:
        """On exit of the "with" method, cleans up src_file."""
        if exc_type is not None:
            print(exc_type, exc_value, tb)
        self.paths = None
        self.src_file.close()
        return True

    def rotate_file(self) -> bool:
        """Allow for operation on a directory seamlessly.

        A counter is used to track which file we are translating at.
        This method is called at initialzation and whenever we are at the end of the
        file.
        It checks if there are any more files to translate, if there are, set src_file
        to the new file.
        Else, return False
        """
        if self.src_file_counter < len(self.paths) - 1:
            with contextlib.suppress(
                AttributeError,
            ):  # there's no src_file opened yet; is fine
                self.src_file.close()
            self.src_file_counter += 1
            self.src_file = open(self.paths[self.src_file_counter])
            self.file_name = (
                os.path.basename(self.src_file.name).replace(".vm", "").upper()
            )
            print(f"> file rotated; now reading from {self.src_file.name}")
            return True
        return False

    def clean_lines(self, line: str) -> bool:
        """Clean up assembly code.

        Set the cleaned line into self.current_line.
        And returns True if its the end of the file, else, False.

        Args:
          line: the assembly code to be cleaned

        """
        if not line:  # EOF
            self.current_line = ""
            return True

        line = line.strip()  # Remove trailing and leading white spaces

        if len(line) == 0:  # Empty line
            self.current_line = ""
            return False

        if "//" in line:  # Comments
            position = line.index("//")
            if position == 0:
                self.current_line = ""
                return False  # Entire line is a comment
            line = line[:position].strip()
        self.current_line = line.upper()
        return False

    def advance(self) -> bool:
        """Parse the next line of VM code.

        Used in a while loop in the driver method
        Returns false when there are no more lines to parse (dependent on rotate_file)
        Takes VM code and splits into it its sematic parts using " " as a delimiter.
        Based on the number of resulting parts, it becomes possible to assign various
        attributes with the required information.

        """
        current_line = self.src_file.readline()

        is_eof = self.clean_lines(current_line)
        if not self.current_line:  # self.current_line is empty
            self.reset()
            if is_eof:
                # we've rotated the file, return True if there are still more files to
                # parse, else return False
                return self.rotate_file()
            return True  # is always not is_eof

        parts = self.current_line.split(" ")
        self.arg3 = None

        # PUSH/POP commands, FUNCTION commands, CALL commands
        if len(parts) == 3:
            self.arg2 = parts[2]
            match parts[0]:  # TODO: migrate to enum
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

        # BRANCHING commands
        elif len(parts) == 2:
            match parts[0]:
                case "LABEL":
                    self.command_type = "C_LABEL"
                case "GOTO":
                    self.command_type = "C_GOTO"
                case "IF-GOTO":
                    self.command_type = "C_IF"
            self.arg1 = parts[1]

        # ARITHMETIC/LOGICAL commands (arg1: no. of arguments; arg2: arithmetic/logical
        # command), RETURN command
        else:
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
