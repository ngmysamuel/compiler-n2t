from jack_tokenizer import JackTokenizer

import sys

def main(path):
    with JackTokenizer(path) as jt:
        for _ in range(1):
            print(f"return: {jt.advance()}")

if __name__ == "__main__":
    main(sys.argv[1])


# py JackAnalyzer.py C:\Users\samue\Documents\Nand2Tetris\06-08_10-11\10\test\test.jack
# cd C:\Users\samue\Documents\Nand2Tetris\06-08_10-11\compiler
# py JackAnalyzer.py C:\Users\samue\Documents\Nand2Tetris\06-08_10-11\10\ExpressionLessSquare\Main.jack