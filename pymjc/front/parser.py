import pymjc.front.ast as Ast
from pymjc.front.lexer import MJLexer
from sly import Parser

from pymjc.log import MJLogger

class MJParser(Parser):

    def __init__(self):
        self.syntax_error = False
        self.src_file_name = "UnknownSRCFile"
        super().__init__
        
    precedence = (('nonassoc', LESS, AND),
                  ('left', PLUS, MINUS),        
                  ('left', TIMES),
                  ('right', NOT)
                 )
                 
    tokens = MJLexer.tokens

    syntax_error = False

    debugfile = 'parser.out'


    ###################################
	#Program and Class Declarations   #
    ###################################    
    @_('MainClass ClassDeclarationStar')
    def Goal(self, p):
        return Ast.Program(p[0], p[1])
    
    @_('CLASS Identifier LEFTBRACE PUBLIC STATIC VOID MAIN LEFTPARENT STRING LEFTSQRBRACKET RIGHTSQRBRACKET Identifier RIGHTPARENT LEFTBRACE Statement RIGHTBRACE RIGHTBRACE')
    def MainClass(self, p):
        return Ast.MainClass(p[1], p[11], p[14])

    @_('Empty')
    def ClassDeclarationStar(self, p):
        return p

    @_('ClassDeclaration ClassDeclarationStar')
    def ClassDeclarationStar(self, p):
        p[1] = Ast.ClassDeclList()
        return p[1].add_element(p[0])

    @_('CLASS Identifier SuperOpt LEFTBRACE VarDeclarationStar MethodDeclarationStar RIGHTBRACE')
    def ClassDeclaration(self, p):
        return Ast.ClassDeclExtends(p[1], p[2], p[4], p[5])

    @_('Empty')
    def SuperOpt(self, p):
        return p
    
    @_('EXTENDS Identifier')
    def SuperOpt(self, p):
        return p[1]

    @_('Empty')
    def VarDeclarationStar(self, p):
        return p

    @_('VarDeclarationStar VarDeclaration')
    def VarDeclarationStar(self, p):
        p[0] = Ast.VarDeclList()
        p[0].add_element(p[1])
        return p[0]

    @_('Type Identifier SEMICOLON')
    def VarDeclaration(self, p):
        return Ast.VarDecl(p[0], p[1])

    @_('Empty')
    def MethodDeclarationStar(self, p):
        return p

    @_('MethodDeclarationStar MethodDeclaration')
    def MethodDeclarationStar(self, p):
        p[0] = Ast.MethodDeclList()
        p[0].add_element(p[1])
        return p[0]

    @_('PUBLIC Type Identifier LEFTPARENT FormalParamListOpt RIGHTPARENT LEFTBRACE VarDeclarationStar StatementStar RETURN Expression SEMICOLON RIGHTBRACE')
    def MethodDeclaration(self, p):
        return Ast.MethodDecl(p[1], p[2], p[4], p[7], p[8], p[10])

    @_('Empty')
    def FormalParamListOpt(self, p):
        return p
        
    @_('FormalParamStar')
    def FormalParamListOpt(self, p):            
        return p[0]

    @_('FormalParam')
    def FormalParamStar(self, p):
        return Ast.FormalList()

    @_('FormalParamStar COMMA FormalParam')
    def FormalParamStar(self, p):
        p[0].add_element(p[2])
        return p[0]

    @_('Type Identifier')
    def FormalParam(self, p):
        return Ast.VarDecl(p[0], p[1])
        
    ###################################
    #Type Declarations                #
    ###################################

    @_('INT')
    def Type(self, p):
        return Ast.IntegerType()

    @_('INT LEFTSQRBRACKET RIGHTSQRBRACKET')
    def Type(self, p):
        return Ast.IntArrayType()

    @_('BOOLEAN')
    def Type(self, p):
        return Ast.BooleanType()

    @_('Identifier')
    def Type(self, p):
        return Ast.IdentifierType(p[0])

    ###################################
    #Statements Declarations          #
    ###################################

    @_('Empty')
    def StatementStar(self, p):
        return p

    @_('Statement StatementStar')
    def StatementStar(self, p):
        p[1] = Ast.StatementList()
        return p[1].add_element(p[0])

    @_('LEFTBRACE StatementStar RIGHTBRACE')
    def Statement(self, p):
        return Ast.Block(p[1])

    @_('IF LEFTPARENT Expression RIGHTPARENT Statement ELSE Statement')
    def Statement(self, p):
        return Ast.If(p[2], p[4], p[6])

    @_('WHILE LEFTPARENT Expression RIGHTPARENT Statement')
    def Statement(self, p):
        return Ast.While(p[2], p[4])

    @_('PRINT LEFTPARENT Expression RIGHTPARENT SEMICOLON')
    def Statement(self, p):
        return Ast.Print(p[2])

    @_('Identifier EQUALS Expression SEMICOLON')
    def Statement(self, p):
        return Ast.Assign(p[0], p[2])

    @_('Identifier LEFTSQRBRACKET Expression RIGHTSQRBRACKET EQUALS Expression SEMICOLON')
    def Statement(self, p):
        return Ast.ArrayAssign(p[0], p[2], p[5])

    ###################################
    #Expression Declarations          #
    ###################################

    @_('Expression AND Expression')
    def Expression(self, p):
        return Ast.And(p[0], [2])

    @_('Expression LESS Expression')
    def Expression(self, p):
        return Ast.LessThan(p[0], p[2])

    @_('Expression PLUS Expression')
    def Expression(self, p):
        return Ast.Plus(p[0], p[2])

    @_('Expression MINUS Expression')
    def Expression(self, p):
        return Ast.Minus(p[0], p[2])

    @_('Expression TIMES Expression')
    def Expression(self, p):
        return Ast.Times(p[0], p[2])

    @_('Expression LEFTSQRBRACKET Expression RIGHTSQRBRACKET')
    def Expression(self, p):
        return Ast.ArrayLookup(p[0], p[2])

    @_('Expression DOT LENGTH')
    def Expression(self, p):
        return Ast.ArrayLength(p[0])

    @_('Expression DOT Identifier LEFTPARENT ExpressionListOpt RIGHTPARENT')
    def Expression(self, p):
        return Ast.Call(p[0], p[2], p[4])

    @_('Empty')
    def ExpressionListOpt(self, p):
        return p

    @_('ExpressionListStar')
    def ExpressionListOpt(self, p):
        return p[0]

    @_('Expression')
    def ExpressionListStar(self, p):
        return Ast.ExpList()

    @_('ExpressionListStar COMMA Expression')
    def ExpressionListStar(self, p):
        p[0].add_element(p[2])
        return p[0]

    @_('THIS')
    def Expression(self, p):
        return Ast.This()

    @_('NEW INT LEFTSQRBRACKET Expression RIGHTSQRBRACKET')
    def Expression(self, p):
        return Ast.NewArray(p[3])

    @_('NEW Identifier LEFTPARENT RIGHTPARENT')
    def Expression(self, p):
        return Ast.NewObject(p[1])

    @_('NOT Expression')
    def Expression(self, p):
        return Ast.Not(p[1])

    @_('LEFTPARENT Expression RIGHTPARENT')
    def Expression(self, p):
        return p[1]

    @_('Identifier')
    def Expression(self, p):
        return p[0]

    @_('Literal')
    def Expression(self, p):
        return p[0]

    ###################################
    #Basic Declarations               #
    ###################################
    @_('ID')
    def Identifier(self, p):
        return Ast.Identifier(p[0])

    @_('')
    def Empty(self, p):
        return p


    ##################################
    #Literals Declarations           #
    ##################################
    @_('BooleanLiteral')
    def Literal(self, p):
        return p[0]

    @_('IntLiteral')
    def Literal(self, p):
        return p[0]

    @_('TRUE')
    def BooleanLiteral(self, p):
        return Ast.TrueExp()

    @_('FALSE')
    def BooleanLiteral(self, p):
        return Ast.FalseExp()

    @_('NUM')
    def IntLiteral(self, p):
        return Ast.IntegerLiteral(int(p[0]))

    def error(self, p):
        MJLogger.parser_log(self.src_file_name, p.lineno, p.value[0])
        self.syntax_error = True