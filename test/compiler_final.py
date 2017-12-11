# -----------------------------------------------------------------------------
# A program to evaluate an arithmetic expression and generate ARM specific assembly code
# Both operands are present in registers
# The program uses a lexer and parser available in package PLY to split into tokens and then implement grammar rules
# PLY is a python package that re-implements Lex and Yacc in python
# -----------------------------------------------------------------------------

import sys
import os
import Queue
from subprocess import Popen
from pprint import pprint

sys.path.insert(0, "../..")#add to search path

if sys.version_info[0] >= 3:#if python 3 or greater,use input instead of raw_input
    raw_input = input
    
asm_beg="\tAREA     appcode, CODE, READONLY\n\tEXPORT __main\n\tENTRY\n__main  FUNCTION\n"
asm_end="stop B stop\n\tENDFUNC\n\tEND"

#lexer code
    
#declaring the tokens for the lexer
tokens = (
    'NAME', 'NUMBER','LS','RS','IF','THEN','ELSE',
)

literals = ['=', '+', '-', '*', '<','>','/', '%','(', ')','?',':']#arithmetic operators

# defining the Tokens number and name

t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
#regular expression:first letter can be an underscore/uppercase/lowercase alphabet,second can be any of these and also a number,followed by anything else


def t_NUMBER(t):
    r'-?\d+'#using raw string notation,repetitions of digits will also match
    t.value = int(t.value)
    #print t
    return t

t_ignore = " \t"#ignore tabspaces

def t_LS(t):
    r'<<'
    return t

def t_RS(t):
    r'>>'
    return t

def t_IF(t):
    r'if'
    return t

def t_ELSE(t):
    r'else'
    return t

def t_THEN(t):
    r'then'
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")#maintain a count of lines


def t_error(t):
    print("Lexer:Illegal character '%s'" % t.value[0])#throws an error if any other character is encountered
    t.lexer.skip(1)

# Build the lexer
import ply.lex as lex
lex.lex()

# Parsing rules

#defining precedence of operators:lowest to highest
precedence = (
    ('left', '>', '<'),
    ('left', 'LS', 'RS'),
    ('left', '+', '-'),
    ('left', '*', '/','%'),
    
)

# dictionary of names
rg = {'r0' : -99, 'r1' : -99, 'r2' : -99, 'r3' : -99, 'r4' : -99, 'r5' : -99, 'r6' : -99, 'r7' : -99,'r8' : -99, 'r9' : -99, 'r10' : -99, 'r11' : -99, 'r12' : -99} # register set populated with values
names={}#dictionary that holds name,value pair
names2={}#dictionary that holds name,register
stack=[]#store operators <, > for use during generating MOV{LE,LT,GT,GE} instructions
queue=Queue.Queue()
#internal variables
_mainr=[]#registers being used for storing calculation results
_l=''#current register

no_of_regs=12

def get_free_rg():
    global _mainr
    global _l
    for i in range(no_of_regs+1):
        r='r'+str(i)#register naming convention
        if((rg[r]==-99) and (r not in _mainr) and (r!=_l)):
            #print "free register" + r
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
    
    if (p[1] in names):#re-assigning
        if(isinstance(p[3], int)):#number
            if(((p[3]>(pow(2,31)-1))|(p[3]<(-pow(2,31))))&p[3]!=0):#out of range
                print "Assignment error:number out of range.Registers are 32 bit"
            else:#in range,number
                if (len(stack)!=0):
                    op=stack.pop()
                    if(op=='<' and len(stack)==0):
                        names[p[1]] = p[3]
                        rg[names2[p[1]]]=p[3]
                        instr="MOVGE "+names2[p[1]]+" ,#"+str(rg[names2[p[1]]])
                        print instr
                        file_asm.write("\t"+instr+"\n")
                        return
                    if(op=='<' and len(stack)==1):
                        names[p[1]] = p[3]
                        rg[names2[p[1]]]=p[3]
                        instr="MOVLT "+names2[p[1]]+" ,#"+str(rg[names2[p[1]]])
                        print instr
                        file_asm.write("\t"+instr+"\n")
                        return
                    if(op=='>' and len(stack)==0):
                        names[p[1]] = p[3]
                        rg[names2[p[1]]]=p[3]
                        instr="MOVLE "+names2[p[1]]+" ,#"+str(rg[names2[p[1]]])
                        print instr
                        file_asm.write("\t"+instr+"\n")
                        return
                    if(op=='>' and len(stack)==1):
                        names[p[1]] = p[3]
                        rg[names2[p[1]]]=p[3]
                        instr="MOVGT "+names2[p[1]]+" ,#"+str(rg[names2[p[1]]])
                        print instr
                        file_asm.write("\t"+instr+"\n")
                        return
                else:
                    names[p[1]] = p[3]
                    rg[names2[p[1]]]=p[3]#store the value into the register
        else:#register
            names[p[1]] = rg[p[3]]
            rg[names2[p[1]]]=rg[p[3]]#store the value into the register
        # print p[3]
        instr="MOV "+names2[p[1]]+" ,#"+str(rg[names2[p[1]]])
        print instr
        file_asm.write("\t"+instr+"\n")
        return
    
    # print p[3]
    else:#new variable
        #print names
        #print p[3]
        if(isinstance(p[3], int)):#p[3] is a number
	    #print "int"
            if(((p[3]>(pow(2,31)-1))|(p[3]<(-pow(2,31))))&p[3]!=0):#out of range
                print "Assignment error:number out of range.Registers are 32 bit"
            else:#in range,number
                if (len(stack)!=0):
                    op=stack.pop()
                    if(op=='<' and len(stack)==0):
                        names[p[1]] = p[3]#add name,expression to the dictionary
                        r=get_free_rg()#look for a free register
                        names2[p[1]] = r#add name,register to dictionary
                        rg[r]=p[3]
                        instr="MOVGE "+names2[p[1]]+" ,#"+str(rg[names2[p[1]]])
                        print instr
                        file_asm.write("\t"+instr+"\n")
                        return
                    if(op=='<' and len(stack)==1):
                        names[p[1]] = p[3]#add name,expression to the dictionary
                        r=get_free_rg()#look for a free register
                        names2[p[1]] = r#add name,register to dictionary
                        rg[r]=p[3]
                        instr="MOVLT "+names2[p[1]]+" ,#"+str(rg[names2[p[1]]])
                        print instr
                        file_asm.write("\t"+instr+"\n")
                        return
                    if(op=='>' and len(stack)==0):
                        names[p[1]] = p[3]#add name,expression to the dictionary
                        r=get_free_rg()#look for a free register
                        names2[p[1]] = r#add name,register to dictionary
                        rg[r]=p[3]
                        instr="MOVLE "+names2[p[1]]+" ,#"+str(rg[names2[p[1]]])
                        print instr
                        file_asm.write("\t"+instr+"\n")
                        return
                    if(op=='>' and len(stack)==1):
                        names[p[1]] = p[3]#add name,expression to the dictionary
                        r=get_free_rg()#look for a free register
                        names2[p[1]] = r#add name,register to dictionary
                        rg[r]=p[3]
                        instr="MOVGT "+names2[p[1]]+" ,#"+str(rg[names2[p[1]]])
                        print instr
                        file_asm.write("\t"+instr+"\n")
                        return
                else:
                    names[p[1]] = p[3]#add name,expression to the dictionary
                    r=get_free_rg()#look for a free register
                    names2[p[1]] = r#add name,register to dictionary
                    rg[r]=p[3]#store the value into the register
                
        else:
                if (len(stack)!=0):
                    op=stack.pop()
                    if(op=='<' and len(stack)==0):
                        names[p[1]] = rg[p[3]]#add name,expression to the dictionary
                        r=get_free_rg()#look for a free register
                        names2[p[1]] = r#add name,register to dictionary
                        rg[r]=rg[p[3]]
                        instr="MOVGE "+names2[p[1]]+" ,#"+str(rg[names2[p[1]]])
                        print instr
                        file_asm.write("\t"+instr+"\n")
                        return
                    if(op=='<' and len(stack)==1):
                        names[p[1]] = rg[p[3]]#add name,expression to the dictionary
                        r=get_free_rg()#look for a free register
                        names2[p[1]] = r#add name,register to dictionary
                        rg[r]=rg[p[3]]
                        instr="MOVLT "+names2[p[1]]+" ,#"+str(rg[names2[p[1]]])
                        print instr
                        file_asm.write("\t"+instr+"\n")
                        return
                    if(op=='>' and len(stack)==0):
                        names[p[1]] = rg[p[3]]#add name,expression to the dictionary
                        r=get_free_rg()#look for a free register
                        names2[p[1]] = r#add name,register to dictionary
                        rg[r]=rg[p[3]]
                        instr="MOVLE "+names2[p[1]]+" ,#"+str(rg[names2[p[1]]])
                        print instr
                        file_asm.write("\t"+instr+"\n")
                        return
                    if(op=='>' and len(stack)==1):
                        names[p[1]] = rg[p[3]]#add name,expression to the dictionary
                        r=get_free_rg()#look for a free register
                        names2[p[1]] = r#add name,register to dictionary
                        rg[r]=rg[p[3]]
                        instr="MOVGT "+names2[p[1]]+" ,#"+str(rg[names2[p[1]]])
                        print instr
                        file_asm.write("\t"+instr+"\n")
                        return
                else:
                    names[p[1]] = rg[p[3]]#add name,expression to the dictionary
                    r=get_free_rg()#look for a free register
                    names2[p[1]] = r#add name,register to dictionary
                    rg[r]=rg[p[3]]#store the value into the register
        instr="MOV "+r+" ,#"+str(rg[r])
        print instr
        file_asm.write("\t"+instr+"\n")
    
        


def p_statement_expr(p):
    'statement : expression'
    #print "p_statement_expr"
    #print(p[1])

def p_expression_binop(p):#expression defined as a recursion on itself
    '''expression : expression '+' expression
                  | expression '-' expression
                  | expression '*' expression
                  | expression '/' expression
                  | expression '%' expression
                  | expression LS expression
                  | expression RS expression
                  | expression '<' expression
 		  | expression '>' expression'''
    #print "p_expression_binop"
    global _mainr
    global _l
    if(_l!=''):
        queue.put(_l)
    if((p[2]=='<') | (p[2]=='>')):
        pass
    else:
        _mainr.append(get_free_rg())
    
        _l=_mainr.pop()
   
        queue.put(_l)


    #print _l

    if ((p[1] == "error") | (p[3]=="error")):
    	print("Binop:Cannot perform operation\t ;Undefined variable name")
    	return
 

    if(p[1]==None):#if one operand is missing,use the register fromt the previous operation
        p[1]=_l
    if(p[3]==None):
        p[3]=_l
    if(p[0]==None):
        p[0]=_l
            

    if p[2] == '+':#addition
        # p[0] = p[1] + p[3]
        # print p[0], p[1], p[3]
        rg[p[0]]=rg[p[1]]+rg[p[3]]
     
        instr="ADD " + p[0] + " ,"+p[1] +" ,"+p[3]
        print instr
        file_asm.write("\t"+instr+"\n")
        
    elif p[2] == '-':#subtraction
        
        rg[p[0]]=rg[p[1]]-rg[p[3]]
        instr= "SUB " + p[0] + " ,"+p[1] +" ,"+p[3]
        print instr
        file_asm.write("\t"+instr+"\n")
        
    elif p[2] == '*':#multiplication
        # p[0] = p[1] * p[3]
    
        rg[p[0]]=rg[p[1]]*rg[p[3]]
        instr= "MUL " + p[0] + ", "+p[1] +", "+p[3]
        print instr
        file_asm.write("\t"+instr+"\n")
        
    elif p[2] == '/':
        #p[0] = p[1] / p[3]
        # print p[0], p[1], p[2]
        # print rg
        try:
            rg[p[0]]=rg[p[1]]/rg[p[3]]
            instr= "SDIV " + p[0] + ", "+p[1] +", "+p[3]
            print instr
            file_asm.write("\t"+instr+"\n")
        except ZeroDivisionError:
            print "division by zero error"
            print "register dump "
            print rg
            os.remove("autogen.s")
            print "asm file not generated"
            exit(ZeroDivisionError)
        # if(rg[p[3]]==0):
        #    print "division by zero error"
        #    print "register dump "
        #    print rg
           
        # else:
        #    rg[p[0]]=rg[p[1]]/rg[p[3]]
        #    instr= "SDIV " + p[0] + ", "+p[1] +", "+p[3]
        #    print instr
        #    file_asm.write("\t"+instr+"\n")

    elif p[2] == '%':
    	#p[0] = p[1] % p[3]
        if(rg[p[3]]==0):
           print "modulus by zero is not defined"
       
        else:
        	rg[p[0]]=rg[p[1]]%rg[p[3]]
        	instr1= "SDIV " + p[0] + ", "+p[1] +", "+p[3]
        	instr2= "MLS " + p[0] +","+ p[0] + ", "+p[3] +", "+p[1]
        	print instr1
        	print instr2

        	file_asm.write("\t"+instr1+"\n")
        	file_asm.write("\t"+instr2+"\n")
                
    elif p[2] == '>>':#Bitwise Right Shift or Divide by 2
        # p[0] = p[1] >> p[3]
    	#print "RS"
        if(rg[p[3]]<0):
            print "negative shift count not permitted"
        elif(rg[p[3]]>32):
            print "32 bit registers:shift by a value less than 32"
        else:
            rg[p[0]]=rg[p[1]]>>rg[p[3]]
            instr= "LSR " + p[0] + ", "+p[1] +", "+p[3]
            print instr
            file_asm.write("\t"+instr+"\n")  

    elif p[2] == '<<':#Bitwise Left Shift or Multiply by 2
        # p[0] = p[1] << p[3]
        if(rg[p[3]]<0):
            print "negative shift count not permitted"
        elif(rg[p[3]]>32):
            print "32 bit registers:shift by a value less than 32"
        else:
            rg[p[0]]=rg[p[1]]<<rg[p[3]]
            instr= "LSL " + p[0] + ", "+p[1] +", "+p[3]
            print instr
            file_asm.write("\t"+instr+"\n")
    elif p[2] == '>':#Greater than 
        # p[0] = p[1] > p[3]
    	#print "RS"
        rg[p[0]]=int(rg[p[1]]>rg[p[3]])
        instr1= "CMP " +p[1] +", "+p[3]
        stack.append('>')
        stack.append('>')
        # if(rg[p[1]]>rg[p[3]]):	
        #     instr2= "MOVGT " + p[0]+ ", #1"
        # else:
        #     instr2= "MOVLE " + p[0]+ ", #0"
	
        print instr1
        # print instr2
        file_asm.write("\t"+instr1+"\n") 
        # file_asm.write("\t"+instr2+"\n") 

    elif p[2] == '<':#Lesser than
        # p[0] = p[1] < p[3]
    	#print "RS"
        rg[p[0]]=int(rg[p[1]]<rg[p[3]])
        instr1= "CMP " +p[1] +", "+p[3]
        stack.append('<')
        stack.append('<')
        # if(rg[p[1]]<rg[p[3]]):	
        #     instr2= "MOVLT " + p[0]+ ", #1"
        # else:
        #     instr2= "MOVGE " + p[0]+ ", #0"
	
        print instr1
        # print instr2
        file_asm.write("\t"+instr1+"\n") 
        # file_asm.write("\t"+instr2+"\n") 

def p_expression_ternop(p):#expression defined as a recursion on itself
    '''statement : expression '?' statement ':' statement
                 | IF expression THEN statement ELSE statement'''
                    #NAME '<' NAME '?' NAME '=' NUMBER ':' NAME '=' NUMBER
    # p[0]          p[1]        p[3]   p[5]    p[7]         p[9]    p[11]
    
    #print "p_expression_ternop"
    
    global _mainr
    global _l
    # if(_l!=''):
    #     queue.put(_l)
        
    # _mainr.append(get_free_rg())
    
    # _l=_mainr.pop()
   
    # queue.put(_l)


#     #print _l

#     if ((p[1] == "error") | (p[3]=="error") | (p[5]=="error")| (p[9]=="error")):
#     	print("Ternop:Cannot perform operation\t ;Undefined variable name")
#     	return
 
    
    
#     if(p[0]==None):
#         p[0]=_l
#     p[1]=names2[p[1]]
#     p[3]=names2[p[3]]
#     #print p[1]
#     #print p[3]
    
#     if p[2] == '>':#Greater than 
#         # p[0] = p[1] > p[3]
#     	#print "RS"
#         rg[p[0]]=int(rg[p[1]]>rg[p[3]])
#         instr1= "CMP " +p[1] +", "+p[3]
#         if(rg[p[1]]>rg[p[3]]):	
#             rg[names2[p[5]]]=p[7]#store the value into the register
#             instr2="MOVGE "+names2[p[5]]+" ,#"+str(rg[names2[p[5]]])    
            
#             print instr1
#             print instr2
#             file_asm.write("\t"+instr1+"\n") 
#             file_asm.write("\t"+instr2+"\n")
#             rg[names2[p[9]]]=p[11]#store the value into the register
#             instr2="MOVLT "+names2[p[9]]+" ,#"+str(rg[names2[p[9]]])
#             print instr2
#             file_asm.write("\t"+instr2+"\n")
#         else:

#             rg[names2[p[9]]]=p[11]#store the value into the register
#             instr2="MOVLT "+names2[p[9]]+" ,#"+str(rg[names2[p[9]]])   
            
#             print instr1
#             print instr2
#             file_asm.write("\t"+instr1+"\n") 
#             file_asm.write("\t"+instr2+"\n")   
#             rg[names2[p[5]]]=p[7]#store the value into the register
#             instr2="MOVGE "+names2[p[5]]+" ,#"+str(rg[names2[p[5]]])
#             print instr2
#             file_asm.write("\t"+instr2+"\n")

            
#     if p[2] == '<':#Lesser than 
#         # p[0] = p[1] > p[3]
#     	#print "RS"
#         rg[p[0]]=int(rg[p[1]]>rg[p[3]])
#         instr1= "CMP " +p[1] +", "+p[3]
#         if(rg[p[1]]<rg[p[3]]):
#             rg[names2[p[5]]]=p[7]#store the value into the register
#             instr2="MOVLT "+names2[p[5]]+" ,#"+str(rg[names2[p[5]]])   
            
#             print instr1
#             print instr2
#             file_asm.write("\t"+instr1+"\n") 
#             file_asm.write("\t"+instr2+"\n")
#             rg[names2[p[9]]]=p[11]#store the value into the register
#             instr2="MOVGE "+names2[p[9]]+" ,#"+str(rg[names2[p[9]]])
#             print instr2 
#             file_asm.write("\t"+instr2+"\n")    
#         else:
#             rg[names2[p[9]]]=p[11]#store the value into the register
#             instr2="MOVGE "+names2[p[9]]+" ,#"+str(rg[names2[p[9]]])    
            
#             print instr1
#             print instr2
#             file_asm.write("\t"+instr1+"\n") 
#             file_asm.write("\t"+instr2+"\n")
#             rg[names2[p[5]]]=p[7]#store the value into the register
#             instr2="MOVLT "+names2[p[5]]+" ,#"+str(rg[names2[p[5]]])
#             print instr2
#             file_asm.write("\t"+instr2+"\n")   



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
    except (LookupError,TypeError,KeyError):
        print("Undefined name '%s'" % p[1])
        p[0] = "error"


def p_error(p):
    if p:
        print("Parser:Syntax error at '%s'" % p.value)
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


file_asm = open("autogen.s",'w')
file_asm.write(asm_beg)

build_flag=1#set to 1 to enable automatic buidling

#open the input file and parse it line by line
with open("../input/input.txt") as f:
    for line in f:
        yacc.parse(line)
        #print "register dump "
        #print rg
    print "\ndebug output:\n"
    print "register dump "
    print rg
    print "\n"
    print "dictionary of variable,value pairs"
    pprint (names)
    print "\n dictionary of variable,register mappings"
    pprint (names2)
    
file_asm.write(asm_end)
file_asm.close()

if(build_flag):
    print "\nBuild flag set! Automatically buidling project with auto-generated asm file"
    p = Popen("build.bat", cwd=r"C:\Users\Prashanthi S.K\Desktop\arm\compiler\Arm_Expression_Compiler")
    stdout, stderr = p.communicate()
    print "\nPrinting build log"
    build_log = open("log.txt")
    for line in build_log:
        print line,
