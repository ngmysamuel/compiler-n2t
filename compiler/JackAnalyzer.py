from jack_tokenizer import JackTokenizer

import sys
import init_logging as il

def main(path, log_level):
    il.set_level(log_level)
    with JackTokenizer(path) as jt:
        cont = True
        while cont:
            cont = jt.advance()
            il.logger.info(f"=== return: {cont}, type: {jt.token_type} ===")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])


# py JackAnalyzer.py C:\Users\samue\Documents\Nand2Tetris\06-08_10-11\10\test\test.jack i
# cd C:\Users\samue\Documents\Nand2Tetris\06-08_10-11\compiler
# py JackAnalyzer.py C:\Users\samue\Documents\Nand2Tetris\06-08_10-11\10\ExpressionLessSquare\Main.jack i