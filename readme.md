# Table of Contents
1. [Assembler](#assembler)

2. [Prerequisites](#prerequisites)

3. [How to run](#how-to-run)

4. [How to test](#how-to-test)

5. [Files](#files)

6. [Resources](#resources)

7. [Other useful links](#other-useful-links)

# Assembler

As part of Nand2Tetris Week 6 project, this Assembler is able to convert assembly code files (.asm) into binary. 

> Do note that the assembly and binary only adheres to the language specifications defined in the Nand2Tetris course i.e. it cannot assemble other assembly flavours.

# Prerequisites

1. Python
2. Git (if intending to `git clone`)

# How to run

1. `git clone https://github.com/ngmysamuel/assembler-n2t.git`
2. `cd assembler-n2t`
3. `py -m assembly.driver path/to/file.asm path/to/output.hack`

py -m translator.VMTranslator C:\Users\samue\Documents\Nand2Tetris\06-08\08\SimpleFunction\SimpleFunction.vm

The assembler will convert the assembly code in \<some assembly\>.asm into binary which will reside in \<output\>.hack. For example, `py driver.py ./06/Pong.asm ./06/Pong.hack`


I did not name my driver file to be `__main__` as I am importing the package in my tests; hence you'll need to specify the file in step 3.

# How to test

1. `cd assembler-n2t`
2. `py -m unittest discover -s ./test/assembler` or `py -m unittest test.assembler.<test file name>`

Note \<test file name\> does not contain the file extension.

# Files

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

SymbolTable.py
> A wrapper around a dictionary
> Keeps track of memory/instruction locations (RAM/ROM) for symbols found in asm files
```

# Resources

[Computer Architecture](https://www.nand2tetris.org/_files/ugd/44046b_b2cad2eea33847869b86c541683551a7.pdf)

[Machine Language](https://www.nand2tetris.org/_files/ugd/44046b_d70026d8c1424487a451eaba3e372132.pdf)

[Assembler](https://www.nand2tetris.org/_files/ugd/44046b_89a8e226476741a3b7c5204575b8a0b2.pdf)

# Other useful links

[Jira Board - Assembler](https://app.plane.so/projects-of-samuel/projects/ce5644c6-58a1-42e6-9b62-bd986f45037b/issues/)
> Let me know if you would like access - I will need to add you to the workspace

[My personal site!](https://ngmysamuel.github.io/)
