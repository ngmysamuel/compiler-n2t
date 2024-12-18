import argparse
import os

from compiler import init_logging as il
from compiler.compilation_engine import CompilationEngine
from compiler.init_logging import logger
from compiler.jack_tokenizer import JackTokenizer
from compiler.vm_writer import VMWriter


def main(path, log_level, dest_path):
    print(f"path: {path}\nlog_level: {log_level}\ndest_path: {dest_path}")
    il.set_level("d" if log_level is None else log_level)
    path = "." if path is None else path

    if os.path.isfile(path):
        logger.debug(f"Input file is {path}")
        if ".jack" not in path:
            raise ValueError("Input file path needs to be a JACK file")
        if dest_path is not None and os.path.isdir(dest_path):
            dest_path = os.path.join(
                dest_path, str(os.path.basename(path)).replace(".jack", ".vm")
            )
        elif ".vm" not in dest_path:
            raise ValueError("Destination file path needs to be a XML file")
        elif dest_path is None:
            dest_path = os.path.join(
                os.path.dirname(path),
                str(os.path.basename(path)).replace(".jack", ".vm"),
            )
        logger.debug(f"dest_path is: {dest_path}")
        run(path, dest_path)
    else:
        logger.debug(f"Input directory is {path}")
        if dest_path is not None and not os.path.isdir(dest_path):
            raise ValueError(
                f"Destination path ({dest_path}) needs to be a directory as input path is a directory ({path})"
            )
        if dest_path is None:
            dest_path = os.path.abspath(path)
        logger.debug(f"dest path is: {dest_path}")
        files_and_dirs = os.listdir(path)
        files_to_process = [f for f in files_and_dirs if f[-5:] == ".jack"]
        logger.debug(f"Files to process: {files_to_process}")
        for p in files_to_process:
            run(
                os.path.join(path, p),
                os.path.join(dest_path, p.replace(".jack", ".vm")),
            )


def run(path, dest_path):
    with VMWriter(dest_path) as vm, JackTokenizer(path) as jt:
        ce = CompilationEngine(vm)
        try:
            ce.set_tokenizer(jt)
        except Exception as e:
            print(e)
        ce.compile()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", help="Path to VM file to compile")
    parser.add_argument("-l", "--log_level", help="Logging level")
    parser.add_argument("-o", "--output", help="Path to output file")
    args = parser.parse_args()
    main(args.path, args.log_level, args.output)
