import argparse
import os

from compiler import JackAnalyzer
from translator import VMTranslator
from assembler import driver

def main(input_path: str, log_level: str, output_path: str) -> None:
    """
    Driver Function
    Calls the corresponding driver functions of the other 3 modules
    """
    input_path = "." if input_path is None else input_path
    input_path = os.path.abspath(input_path)
    directory = input_path
    if os.path.isfile(input_path):
      directory = os.path.dirname(input_path)
    output_path = directory if output_path is None else output_path
    if os.path.isfile(output_path):
       raise ValueError("Output path cannot be a file. Provide a directory instead.")
    JackAnalyzer.main(directory, log_level, output_path)
    VMTranslator.main(output_path, output_path)
    driver.main(output_path, output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", help="Path to JACK file to compile")
    parser.add_argument("-l", "--log_level", help="Logging level")
    parser.add_argument("-o", "--output", help="Path to output file")
    args = parser.parse_args()
    main(args.path, args.log_level, args.output)