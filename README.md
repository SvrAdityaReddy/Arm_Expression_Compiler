# Arm_Expression_Compiler

[![Snap Status](https://build.snapcraft.io/badge/SvrAdityaReddy/Arm_Expression_Compiler.svg)](https://build.snapcraft.io/user/SvrAdityaReddy/Arm_Expression_Compiler)

[![Get it from the Snap Store](https://snapcraft.io/static/images/badges/en/snap-store-white.svg)](https://snapcraft.io/aec-arm)

# Problem Statement
To read expressions and statements from a text file and generate ARM assembly instructions
that can be run directly on Keil uVision IDE. The assembly instructions are specific to a generic
ARM Cotrex M4 device/board.

# Abstract
Expressions from the input source are read. Lexical analysis is performed on the expressions to
obtain the appropriate tokens. Thereafter, parsing is done using pre-defined grammar rules to
generate the specific assembly instructions. These instructions are written to a .s file and can be
simulated/debugged on uVision.

# Tools used
Type | Name
----------|--------
Langauge | Python
Package | PLY
Lexer | Lex
Parser | Yacc

# Implementation
PLY stands for Python Lex and Yacc. It is a Python version of Lex and Yacc that has the same
functionality as Lex and Yacc but has a different interface with ample support for debugging.
Simply put, it provides an easy way to write a compiler.

# Lexing
Tokens are defined either using regular expressions or functions in the code for the lexer. The
lexer splits up the input file into these tokens.

![image](https://user-images.githubusercontent.com/19650574/33804565-cd560862-ddcd-11e7-9cac-482fa99e4b9b.png)

### Example

```{python}:

t_NAME = r’[a-zA-Z_][a-zA-Z0-9_]*’
def t_NUMBER(t):
r’\d+’ t.
value = int(t.value)
return t

```

# Parsing
Grammar rules are defined within functions. Tokens are imported from the lexer. PLY uses LR
parsing aka Shift Reduce parsing. Results propagate up through the grammar in a bottom up
fashion.

![image](https://user-images.githubusercontent.com/19650574/33804571-07f063d2-ddce-11e7-8672-390301d3afbd.png)

### Example
```{python}:

assign : NAME EQUALS expr
expr :NUMBER
def p_expr(p):
'''expr : expr PLUS expr | expr MINUS expr '''

```

# Code Generation
Assembly instructions specific to ARM Cortex M4 are generated and written to an assembly file

![image](https://user-images.githubusercontent.com/19650574/33804597-46257048-ddce-11e7-8553-5bde40174f65.png)

# Sample Input File

```
a=8
b=3
c=4
d=2
e=1
g=a+b-c*d/a%e
a>b?f=5:f=3
if a<b then f=5 else g=3
a>>d
c<<e
h=a%b

```
# Output File Generated

```
AREA     appcode, CODE, READONLY
	EXPORT __main
	ENTRY
__main  FUNCTION
	MOV r0 ,#8
	MOV r1 ,#3
	MOV r2 ,#4
	MOV r3 ,#2
	MOV r4 ,#1
	ADD r5 ,r0 ,r1
	MUL r6, r2, r3
	SDIV r7, r6, r0
	SDIV r8, r7, r4
	MLS r8, r8, r4, r7
	SUB r9 ,r5 ,r8
	MOV r10 ,#11
	CMP r0, r1
	MOVGT r11 ,#5
	MOVLE r11 ,#3
	CMP r0, r1
	MOVLT r11 ,#5
	MOVGE r10 ,#3
	LSR r12, r0, r3
	LSL r5, r2, r4
	SDIV r6, r0, r1
	MLS r6, r6, r1, r0
	MOV r7 ,#2
stop B stop
	ENDFUNC
	END

```

# Debug Dump

For testing purpose we are also replicating those r12 registers of arm cortex M4 and maintaining a dictionary of variable, value pairs and dictionary of variable, register pairs for both debugging and reclaiming of registers for further usage if required. <br>

Debug dump for the above test file is as follow.

```
register dump 
{'r12': 2, 'r10': 3, 'r11': 5, 'r4': 1, 'r5': 8, 'r6': 2, 'r7': 2, 'r0': 8, 'r1': 3, 'r2': 4, 'r3': 2, 'r8': 0, 'r9': 0}


dictionary of variable,value pairs
{'a': 8, 'b': 3, 'c': 4, 'd': 2, 'e': 1, 'f': 5, 'g': 3, 'h': 2}

 dictionary of variable,register mappings
{'a': 'r0',
 'b': 'r1',
 'c': 'r2',
 'd': 'r3',
 'e': 'r4',
 'f': 'r11',
 'g': 'r10',
 'h': 'r7'}

```

# Snap

Now this is available as a snap package at [here](https://snapcraft.io/aec-arm/) <br>

![image](https://user-images.githubusercontent.com/19650574/34045423-d4000262-e1ce-11e7-9884-96a9b24165fb.png)

### Snap Installation

```sh

$ sudo snap install aec-arm

```

### Snap Usage Instructions

```sh

$ aec-arm <input_file.txt>

```
An output file will be generated with name as autogen.s in the current working directory which can be run on keil simulator on successful execution.

# Team

Deepika Raj (https://github.com/depikaraj) <br>
Prashanthi Kadambi (https://github.com/amateurcoder10) <br>
Seelapureddy Venkata Rama Aditya Reddy (https://github.com/SvrAdityaReddy) <br>

# References
[1] [Writing Parsers and Compilers with PLY by David Beazley](https://speakerdeck.com/dabeaz/writing-compilers-in-python-with-ply)<br>
[2] [Python Lex-Yacc](https://github.com/dabeaz/ply/)<br>
[3] [Create your first snap](https://tutorials.ubuntu.com/tutorial/create-your-first-snap)<br>
[4] [The python plugin](https://docs.snapcraft.io/reference/plugins/python)<br>
[5] [Python Apps the Right Way: entry points and scripts](https://chriswarrick.com/blog/2014/09/15/python-apps-the-right-way-entry_points-and-scripts/)<br>
[6] [Interfaces reference](https://docs.snapcraft.io/reference/interfaces)
