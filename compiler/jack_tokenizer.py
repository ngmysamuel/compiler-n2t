# A language that is 1 lookahead means that its grammar only needs the current token to know which rule to apply for parsing
# "Indeed, in the simple grammar shown in figure 10.3, looking ahead one token suffices to resolve, without ambiguity, which rule to use next."
# Chp 10
# Thus, that does not apply to the tokenizer.
# 1 lookahead is 1 TOKEN - you need to solve the tokenizing problem first

from init_logging import logger

class JackTokenizer:
    def __init__(self, path):
        self.file = None
        self.file_path = path
        self.keywords = ["class", "construnctor", "function", "method", ]
        self.symbols = ["{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", ">", "<", "=", "~"]
        self.temp = ""
        self.current_token = ""
        self.token_type = "" # TODO: use enum
        self.one_lookahead = ""

    def __enter__(self):
        self.file = open(self.file_path, "r")
        return self

    def __exit__(self, exc_type, exc_value, tb):
        try:
            self.file.close()
        except:
            pass
        finally:
            logger.info("File is closed")
    
    def advance(self):
        is_comment = False
        is_numeric = False
        is_alpha = False
        is_str_const = False
        while True:
            if self.one_lookahead != "":
                self.current_token = self.one_lookahead
                self.one_lookahead = ""
                return self.current_token
            ch = self.file.read(1)
            if ch == "":
                break
            logger.debug(f"====== ch: {ch}, temp: {self.temp}, is_comment: {is_comment} ======")
            if (self.temp == "/" and ch == "/") or (self.temp == "/" and ch == "*"): # start of a comment
                logger.debug("start of comment")
                is_comment = True
                self.temp = ""
                continue
            elif self.temp == "/" and (ch != "/" or ch != "*")  and not is_comment: # we thought it might be a comment but it turns out that its not. So we return the single "/". The current ch will be returned on a subsequent call to this method without moving forward in the file
                logger.debug("1. not actually a comment")
                self.one_lookahead = ch
                return self.temp
            if ch == "/" and not is_comment: # potential start of a comment
                logger.debug("6. potential start of a comment")
                self.current_token = self.temp
                self.temp = ch
                if self.current_token != "":
                    logger.debug("5. we return the current token we have first before embarking on a potential comment")
                    return self.current_token
                continue
            if ch == "*" and is_comment: # potential end of alt comment
                logger.debug("7. potential end of alt comment")
                self.temp = "*"
                continue
            if is_comment and (ch == "\n" or (self.temp == "*" and ch == "/")): # end of a comment
                logger.debug("end of comment")
                is_comment = False
                self.temp = ""
                self.current_token = ""
                continue
            if is_comment: # currently in a comment
                logger.debug("currently in a comment")
                self.temp = ""
                continue
            if (self.is_whitespace(ch) or ch in self.symbols) and self.temp != "": # we have reached the end of the current_token and can return it
                logger.debug("2. end of current token")
                self.current_token = self.temp
                self.one_lookahead = ch if ch != " " else "" # this is for the case where we find game.run(). We are going to return "game" and need to save "." to return. We also need to ignore " "
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
                logger.debug(f"8. numeric. adding to {self.temp} + {ch} = {self.temp + ch}")
                self.temp += ch
            elif ch.isalpha() or ch == "_":
                is_alpha = True
                logger.debug(f"8. alpha. adding to {self.temp} + {ch} = {self.temp + ch}")
                self.temp += ch
            elif ch in self.symbols: # character is a symbol and we can return
                logger.debug("3. current is a symbol, returning")
                self.token_type = "SYMBOL"
                self.current_token = ch
                return self.current_token
            elif ch == "\"":
                logger.debug("4. end of string literal")
                if is_str_const: # this is the end of a string constant
                    self.token_type = "STRING_CONST"
                    is_str_const = False
                    return self.temp
                else: # this is the start of a string constant
                    is_str_const = True
                    self.temp += ch
            

    def is_whitespace(self, ch):
        return not (ch.isalpha() or ch.isnumeric() or ch in self.symbols)