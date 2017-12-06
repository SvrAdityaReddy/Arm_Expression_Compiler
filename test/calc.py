# -----------------------------------------------------------------------------
# calc.py
#
# A simple calculator with variables.   This is from O'Reilly's
# "Lex and Yacc", p. 63.
# -----------------------------------------------------------------------------

import sys
import Queue
sys.path.insert(0, "../..")

if sys.version_info[0] >= 3:
    raw_input = input

tokens = (
    'NAME', 'NUMBER',
)

literals = ['=', '+', '-', '*', '/', '(', ')']

# Tokens

t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

t_ignore = " \t"


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
import ply.lex as lex
lex.lex()

# Parsing rules

precedence = (
    ('left', '+', '-'),
    ('left', '*', '/'),
    ('right', 'UMINUS'),
)

# dictionary of names
rg = {'r0' : 0, 'r1' : 0, 'r2' : 0, 'r3' : 0, 'r4' : 0, 'r5' : 0, 'r6' : 0, 'r7' : 0}
names={}
names2={}
stack=[]
queue=Queue.Queue()
_mainr=[]
_l=''

def get_free_rg():
    global _mainr
    global _l
    for i in range(8):
        r='r'+str(i)
        if((rg[r]==0) and (r not in _mainr) and (r!=_l)):
            return r
    # rg[queue.get()]=0
    # rg[queue.get()]=0
    # get_free_rg()
    queue.get()
    return queue.get()

# _mainr.append(get_free_rg())
# _l=_mainr.pop()

def p_statement_assign(p):
    'statement : NAME "=" expression'
    names[p[1]] = p[3]
    r=get_free_rg()
    names2[p[1]] = r
    rg[r]=p[3]
    print "MOV "+r+" #"+str(rg[r])


def p_statement_expr(p):
    'statement : expression'
    print(p[1])

def p_expression_binop(p):
    '''expression : expression '+' expression
                  | expression '-' expression
                  | expression '*' expression
                  | expression '/' expression'''
    global _mainr
    global _l
    if(_l!=''):
        queue.put(_l)
    _mainr.append(get_free_rg())
    _l=_mainr.pop()
    # print _mainr
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


def p_expression_number(p):
    "expression : NUMBER"
    p[0] = p[1]


def p_expression_name(p):
    "expression : NAME"
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

with open("../input/input.txt") as f:
    for line in f:
        yacc.parse(line)
    print rg
