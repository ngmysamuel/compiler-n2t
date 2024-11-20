# A language that is 1 lookahead means that its grammar only needs the current token to know which rule to apply for parsing
# "Indeed, in the simple grammar shown in figure 10.3, looking ahead one token suffices to resolve, without ambiguity, which rule to use next."
# Chp 10
# Thus, that does not apply to the tokenizer.
# 1 lookahead is 1 TOKEN - you need to solve the tokenizing problem first

class JackTokenizer:
    def __init__(self, path):
        self.file = None
        self.file_path = path
        self.keywords = ["class", "construnctor", "function", "method", ]
        self.symbols = ["{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", ">", "<", "=", "~"]
        self.temp = ""
        self.current_token = ""
        self.token_type = "" # TODO: use enum

    def __enter__(self):
        self.file = open(self.file_path, "r")
        return self

    def __exit__(self, exc_type, exc_value, tb):
        try:
            self.file.close()
        except:
            pass
        finally:
            print("File is closed")
    
    def advance(self):
        is_comment = False
        is_numeric = False
        is_alpha = False
        is_str_const = False
        one_lookahead = ""
        while True:
            if one_lookahead != "":
                self.current_token = one_lookahead
                one_lookahead = ""
                return self.current_token
            ch = self.file.read(1)
            print(f"ch: {ch}, temp: {self.temp}, is_comment: {is_comment}")
            if self.temp == "/" and ch == "/": # start of a comment
                print("start of comment")
                is_comment = True
                self.temp = "//"
                continue
            elif self.temp == "/" and ch != "/": # we thought it might be a comment but it turns out that its not. So we return the single "/". The current ch will be returned on a subsequent call to this method without moving forward in the file
                print("1")
                one_lookahead = ch
                return self.temp
            if ch == "/" and not is_comment: # potential start of a comment
                print("6")
                self.current_token = self.temp
                self.temp = ch
                if self.current_token != "":
                    print("5")
                    return self.current_token
                continue
            if is_comment and (ch == "\n"): # end of a comment
                print("end of comment")
                is_comment = False
                self.temp = ""
                self.current_token = ""
                continue
            if is_comment: # currently in a comment
                print("currently")
                continue
            if (self.is_whitespace(ch) or ch in self.symbols) and self.temp != "": # we have reached the end of the current_token and can return it
                print("2")
                self.current_token = self.temp
                self.temp = ""
                if is_numeric and not is_alpha:
                    self.token_type = "INT_CONST"
                elif is_alpha:
                    self.token_type = "IDENTIFIER"
                is_numeric = False
                is_alpha = False
                return self.current_token
            if ch.isnumeric():
                is_numeric = True
                self.temp += ch
            elif ch.isalpha() or ch == "_":
                is_alpha = True
                self.temp += ch
            elif ch in self.symbols: # character is a symbol and we can return
                print("3")
                self.token_type = "SYMBOL"
                self.current_token = ch
                return self.current_token
            elif ch == "\"":
                print("4")
                if is_str_const: # this is the end of a string constant
                    self.token_type = "STRING_CONST"
                    is_str_const = False
                    return self.temp
                else: # this is the start of a string constant
                    is_str_const = True
                    self.temp += ch
            

    def is_whitespace(self, ch):
        return not (ch.isalpha() or ch.isnumeric() or ch in self.symbols)