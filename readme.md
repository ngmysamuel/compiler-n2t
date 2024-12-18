# Table of Contents
1. [Overview](#overview)

2. [Prerequisites](#prerequisites)

3. [How to run](#how-to-run)

4. [How to test](#how-to-test)

5. [Files](#files)

6. [Resources](#resources)

7. [Other useful links](#other-useful-links)

# Overview

As part of Nand2Tetris, this project takes high level code (known as JACK) and through a series of modules, parses it into binary. There are 3 main modules.
1. Assembler
    - Converts assembly code files (.asm) into binary.
2. Translator
    - Converts VM code files (.vm) into assembly
3.  Compiler
    - Converts JACK code files (.jack) into VM code
    - There also a module `compiler_xml` which parses JACK code into XML representing its sematics. You normally would not use this.

> Do note that the VM code, assembly, and binary generated only adheres to the language specifications defined in the Nand2Tetris course i.e. it does not actually on a easily available piece of hardware (e.g. x86) unless it adheres to the Nand2Tetris specification

# Prerequisites

1. Python

### Optional Prerequisites
1. Git (if intending to `git clone`)
2. See requirements.txt (if intending to build)

# How to run

1. `git clone https://github.com/ngmysamuel/compiler-n2t.git`
2. `cd compiler-n2t`
3. To run
    - Compiler: `py -m compiler_xml.JackAnalyzer -p path/to/jack/code -o <path/to/output/file>`
    - Translator: `py -m translator.VMTranslator path/to/vm`
    - Assembler: `py -m assembly.driver path/to/file.asm path/to/output.hack`

# How to test

Ensure you're in the root of the folder

1. Compiler
    - `py -m unittest test.compiler_xml.test_intgn`
2. Translator
    - `py -m unittest discover -s ./test/translator` or `py -m unittest test.translator.<test file name>`
3. Assembler
    - `py -m unittest discover -s ./test/assembler` or `py -m unittest test.assembler.<test file name>`

Note do not append the file extension to \<test file name\> 

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
> SWITCH statements
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
