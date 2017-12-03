# -----------------------------------------------------------------------------
# A program to evaluate an arithmetic expression and generate ARM specific assembly code
# Both operands are present in registers
# The program uses a lexer and parser available in package PLY to split into tokens and then implement grammar rules
# PLY is a python package that re-implements Lex and Yacc in python
# -----------------------------------------------------------------------------

import sys
import Queue
sys.path.insert(0, "../..")#add to search path

if sys.version_info[0] >= 3:#if python 3 or greater,use input instead of raw_input
    raw_input = input

#lexer code
    
#declaring the tokens for the lexer
tokens = (
    'NAME', 'NUMBER',
)

literals = ['=', '+', '-', '*', '/', '(', ')']#arithmetic operators

# defining the Tokens number and name

t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
#regular expression:first letter can be an underscore/uppercase/lowercase alphabet,second can be any of these and also a number,followed by anything else


def t_NUMBER(t):
    r'\d+'#using raw string notation,repetitions of digits will also match
    t.value = int(t.value)
    return t

t_ignore = " \t"#ignore tabspaces


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")#maintain a count of lines


def t_error(t):
    print("Illegal character '%s'" % t.value[0])#throws an error if any other character is encountered
    t.lexer.skip(1)

# Build the lexer
import ply.lex as lex
lex.lex()

# Parsing rules

#defining precedence of operators
precedence = (
    ('left', '+', '-'),
    ('left', '*', '/'),
    ('right', 'UMINUS'),
)

# dictionary of names
rg = {'r0' : 0, 'r1' : 0, 'r2' : 0, 'r3' : 0, 'r4' : 0, 'r5' : 0, 'r6' : 0, 'r7' : 0} # register set populated with values
names={}#dictionary that holds name,value pair
names2={}#dictionary that holds name,register
stack=[]
queue=Queue.Queue()
#internal variables
_mainr=[]#registers being used for storing calculation results
_l=''#current register

def get_free_rg():
    global _mainr
    global _l
    for i in range(8):
        r='r'+str(i)#register naming convention
        if((rg[r]==0) and (r not in _mainr) and (r!=_l)):
            return r#found a free register,return it
    # rg[queue.get()]=0
    # rg[queue.get()]=0
    # get_free_rg()
    queue.get()
    return queue.get()

# _mainr.append(get_free_rg())
# _l=_mainr.pop()

#function for code-generation for an assignment;translate a=value to MOV Rn,#value
def p_statement_assign(p):
    'statement : NAME "=" expression'#tokens in an assignment statement
    #print "p_statement_assign"
    names[p[1]] = p[3]#add name,expression to the dictionary
    r=get_free_rg()#look for a free register
    names2[p[1]] = r#add name,register to dictionary
    rg[r]=p[3]#store the value into the register
    print "MOV "+r+" #"+str(rg[r])


def p_statement_expr(p):
    'statement : expression'
    #print "p_statement_expr"
    print(p[1])

def p_expression_binop(p):#expression defined as a recursion on itself
    '''expression : expression '+' expression
                  | expression '-' expression
                  | expression '*' expression
                  | expression '/' expression'''
    #print "p_expression_binop"
    global _mainr
    global _l
    if(_l!=''):
        queue.put(_l)
        
    _mainr.append(get_free_rg())
    
    _l=_mainr.pop()
   
    queue.put(_l)
 
    if p[2] == '+':
        # p[0] = p[1] + p[3]
        if(p[1]==None):
            p[1]=_l
        if(p[3]==None):
            p[3]=_l
        if(p[0]==None):
            p[0]=_l
        rg[p[0]]=rg[p[1]]+rg[p[3]]
        print "ADD " + p[0] + " "+p[1] +" "+p[3]
    elif p[2] == '-':
        p[0] = p[1] - p[3]
    elif p[2] == '*':
        # p[0] = p[1] * p[3]
        if(p[1]==None):
            p[1]=_l
        if(p[3]==None):
            p[3]=_l
        if(p[0]==None):
            p[0]=_l
        rg[p[0]]=rg[p[1]]*rg[p[3]]
        print "MUL " + p[0] + " "+p[1] +" "+p[3]
    elif p[2] == '/':
        p[0] = p[1] / p[3]


def p_expression_uminus(p):
    "expression : '-' expression %prec UMINUS"
    p[0] = -p[2]


def p_expression_group(p):
    "expression : '(' expression ')'"
    #print "p_expression_group"
    global _mainr
    global _l
    # if(_l!=''):
    #     queue.put(_l)
    # _mainr.append(get_free_rg())
    # _l=_mainr.pop()
    # print _mainr
    # queue.put(_l)
    # if(_l!=''):
    #     stack.append(_l)
    # _mainr.append(get_free_rg())
    # _l=_mainr.pop()
    # stack.append(_l)
    p[0] = p[2]


def p_expression_number(p):#expression is the number itself
    "expression : NUMBER"
    #print "p_expression_number"
    p[0] = p[1]


def p_expression_name(p):#checks if value is stored in a register already;else invalid operation
    "expression : NAME"
    #print "p_expression_name"
    try:
        # p[0] = names[p[1]]
        p[0] = names2[p[1]]
    except LookupError:
        print("Undefined name '%s'" % p[1])
        p[0] = 0


def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")

#build the parser
import ply.yacc as yacc
yacc.yacc()

# while 1:
#     try:
#         s = raw_input('calc > ')
#     except EOFError:
#         break
#     if not s:
#         continue
#     yacc.parse(s)
#     print names
#     print names2
#     print stack
#     print rg

#open the input file and parse it line by line
with open("input.txt") as f:
    for line in f:
        yacc.parse(line)
        #print "register dump "
        #print rg
    print "register dump "
    print rg
