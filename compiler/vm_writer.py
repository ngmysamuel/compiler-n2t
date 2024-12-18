class VMWriter:
    def __init__(self, path):
        self.path = path
        self.file = None

    def __enter__(self):
        self.file = open(self.path, "w")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.file.close()
        except:
            pass

    def write_push(self, segment, index):
        self.write(f"push {segment} {index}")

    def write_pop(self, segment, index):
        self.write(f"pop {segment} {index}")

    def write_arithmetic(self, command):
        self.write(f"{command}")

    def write_label(self, label):
        self.write(f"label {label}")

    def write_goto(self, label):
        self.write(f"goto {label}")

    def write_if(self, label):  # if-goto
        self.write(f"if-goto {label}")

    def write_call(self, name, arg_count):
        self.write(f"call {name} {arg_count}")

    def write_function(self, name, var_count):
        self.write(f"function {name} {var_count}")

    def write_return(self):
        self.write("return")

    def write(self, str):
        self.file.write(str)
        self.file.write("\n")
