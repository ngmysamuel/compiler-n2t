class SymbolTable:
    """
    Helper Class
    Mainly a dictionary to keep a record of variables seen at the class/subroutine level
    Has helper functions to return the type, kind, and index of the variable
    """
    def __init__(self):
        self.table = {}  # { var_name : (idx, type, kind) }
        self.count_of_kinds = {}

    def reset(self):
        self.table = {}
        self.count_of_kinds = {}

    def define(self, name, type, kind):
        try:
            self.table[name] = (self.count_of_kinds[kind], type, kind)
            self.count_of_kinds[kind] += 1
        except KeyError:
            self.table[name] = (0, type, kind)
            self.count_of_kinds[kind] = 1

    def var_count(self, kind):
        count = 0
        try:
            count = self.count_of_kinds[kind]
        except KeyError:
            return count
        finally:
            return count

    def kind_of(self, name):
        return self.table[name][2]

    def type_of(self, name):
        return self.table[name][1]

    def index_of(self, name):
        return self.table[name][0]
