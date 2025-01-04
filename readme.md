# Table of Contents
1. [Overview](#overview)

2. [Prerequisites](#prerequisites)

3. [How to run](#how-to-run)

4. [How to test](#how-to-test)

5. [Continuous Integration](#continuous-integration)

6. [Files](#files)

7. [Resources](#resources)

8. [Other useful links](#other-useful-links)

# Overview

As part of Nand2Tetris, this project takes high level code (known as JACK) and through a series of modules, parses it into binary. There are 3 main modules.
1. Assembler
    - Converts assembly code files (.asm) into binary.
2. Translator
    - Converts VM code files (.vm) into assembly
3.  Compiler
    - Converts JACK code files (.jack) into VM code
    - There also a module `compiler_xml` which parses JACK code into XML representing its sematics. You normally would not use this.

> Do note that the VM code, assembly, and binary generated only adheres to the language specifications defined in the Nand2Tetris course i.e. it does not actually work on an easily available piece of hardware (e.g. x86) unless it adheres to the Nand2Tetris specification

# Prerequisites

1. Python

### Optional Prerequisites (if intending to build)
1. Git
2. See `pyproject.toml`

# How to run

There are 2 ways.

### 1. Build your own

1. Clone the source code
    - `git clone https://github.com/ngmysamuel/compiler-n2t.git`
2. Ensure you are in the root of the project directory
    - `cd compiler-n2t`
3. Install dependencies (very minimal)
    - `poetry install`
    - You might need to install `pipx` and `poetry` separately first
    - If you do not wish to use poetry, you just need to manage dependencies yourself. Open `pyproject.toml` and install the packages there.
4. Activate the environment
    - `poetry shell`
    - Alternatively, pre-pend `poetry run` to all the commands in step 5 below
5. To run
    - Compiler: `py -m compiler_xml.JackAnalyzer -p path/to/jack/files -o path/to/vm/files`
    - Translator: `py -m translator.VMTranslator path/to/vm/files path/to/asm/files`
    - Assembler: `py -m assembly.driver path/to/asm/files path/to/hack/files`
    - End to end: `py -m end_to_end.end_to_end -p path/to/jack/files`

### 2. Download a release (for Unix)

Download a release from the GitHub repository [here](https://github.com/ngmysamuel/compiler-n2t/releases). This release builds the `end_to_end` module.

> Do note that the binary and assembly the `end_to_end` module generates will not produce the expected results as the OS is not yet included.

# How to test

### Unit Testing
Ensure you're in the project root and the environment activated.

1. Compiler
    - `py -m unittest test.compiler_xml.test_intgn`
2. Translator
    - `py -m unittest discover -s ./test/translator` or `py -m unittest test.translator.<test file name>`
3. Assembler
    - `py -m unittest discover -s ./test/assembler` or `py -m unittest test.assembler.<test file name>`
4. All
    - `python -m test.run_all_tests`

Note: do not append the file extension to \<test file name\>

### System Testing

1. Visit https://nand2tetris.github.io/web-ide/
2. Run the module you wish to use (see [How to run](#how-to-run))
3. Take the output files and upload it to site
    - Compiler - upload the generated VM files into the "VM Emulator"
    - Translator - upload the generated ASM files into the "CPU Emulator"
    - Assembler - upload the generated HACK files into the "CPU Emulator"

The Pong program (in 11/Pong) would be the most interesting program to test.

# Continuous Integration

Every `push` spins a CI that tests the code. You can view the test results in the job summary page.

Every `merge` into `Main` will build a binary and create a new release which you can find [here](https://github.com/ngmysamuel/compiler-n2t/releases). Test results will also be published in the pull request.

# Files

### Assembler
```
Assembler.py
> Drives the process

Parser.py
> Parses the assembly
> Converts assembly into their component parts for Code.py to more easily convert
> e.g. @ITRS is parsed into @272

Code.py
> Converts the string mnemonics into binary
> Made of SWITCH statements
> Assembles assembly in binary code

SymbolTable.py
> A wrapper around a dictionary
> Keeps track of memory/instruction locations (RAM/ROM) for symbols found in asm files
```
### Translator
```
VMTranslator.py
> Drives the process

Parser.py
> Cleans up the VM code e.g. removal of comments, white space
> Supplies the next line of cleaned assembly code
> Codifies the semantics
> File rotation occurs here - to translate whole directories

Codewriter.py
> A heavy file
> Based on the sematics provided, writes the necessary assembly into the file
> Implementation of function calling and returning protocol
> Translates VM into assembly
```

### Compiler
```
enumerations/
> Collection of enumerations that's used by the various scripts

init_logging.py
> Helper file
> Sets up and initializes the logger

JackAnalyzer.py
> Drives the process
> File rotation occurs here - to translate whole directories
> 3 parameters
    > -p - this represents the path to the input file i.e. the JACK file. It might be a directory containing JACK files as well. It will compile all the JACK files available 
    > -l - this represents the log level. Defaults to `debug` level. Use `i` for info level
    > -o - this represents the path to the output file. If you're compiling a directory, this must be a directory.

vm_writer.py
> A class to encapsulate the logic of writing VM instructions into a file

symbol_table.py
> A dictionary
> Represents the variables declared in the JACK file, be it class or function level

jack_tokenizer.py
> Codifies the sematics of the JACK language
> Breaks the language into individual tokens
> Ensures each token the compilation engine receives is clean (e.g. not a comment, white space)

compilation_engine.py
> The star of the module
> Each method represents a section of the JACK language
> Potentially recursive as expressions contains terms which in turn may contain yet more expressions
> Compiles JACK into VM
```


# Resources

[Computer Architecture](https://www.nand2tetris.org/_files/ugd/44046b_b2cad2eea33847869b86c541683551a7.pdf)

[Machine Language](https://www.nand2tetris.org/_files/ugd/44046b_d70026d8c1424487a451eaba3e372132.pdf)

[Assembler](https://www.nand2tetris.org/_files/ugd/44046b_89a8e226476741a3b7c5204575b8a0b2.pdf)

# Other useful links

[Jira Board - Compiler](https://app.plane.so/projects-of-samuel/projects/ce5644c6-58a1-42e6-9b62-bd986f45037b/issues/)


[My personal site](https://ngmysamuel.github.io/)
