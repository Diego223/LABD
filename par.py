from scannerFunctions import *
from Functions import *
from keys import *
import pickle

class yaparProcessor:
    def __init__(self, file_path) :
        self.file_path = file_path
        self.lines = []
        self.comments = []
        self.rules = []
        self.productions = []
        self.ignores = []
        with open('read.bin', 'rb') as file:
            self.tokens = pickle.load(file)
        with open('llaves.bin', 'rb') as file:
            self.tokenRules = pickle.load(file)
            self.tokensExp = pickle.load(file)
        self.processParser()

    def processParser(self):
        self.extractLines()
        self.extractComments()
        self.extractTokens()
        self.extractProductions()

    def extractLines(self):
        #remove lines that are only \n
        with open(self.file_path, 'r') as file:
            for line in file:
                if line != '\n':
                    self.lines.append(line)

    def extractComments(self):
        finds = findAll(self.lines, '/* (^a)∗ */')
        print(finds)
        lastline = 0
        for key, value in finds.items():
            for i in range(len(value)):
                self.comments.append(value[i][0])
                lastline = key
        self.lines = self.lines[lastline+1:]

    def extractTokens(self):
        index = 0
        errors = False
        separator = False
        for i in range(len(self.lines)):
            if matches(self.lines[i], '%%\n'):
                index = i
                separator = True
                break
        if not separator:
            raise Exception("No HAY SEPARADORES DE PRODUCCIONES  '%%' ENCONTRADOS")
        tokenlines = self.lines[:index]
        finds = findAll(tokenlines, '(A-Z)+')
        for key, value in finds.items():
            for i in range(len(value)):
                if startsWith(value[i][0], 'GNORE'):
                    self.ignores.append(value[i][0].split(" ")[1])
                elif(value[i][0] in self.tokenRules.values()):
                    self.rules.append(value[i][0])
                else:
                    print("Error: ", value[i][0], " NOT VALID")
                    errors = True
        if errors:
            raise Exception("LLAVES INCORRECTAS")

    def extractProductions(self):
        index = 0
        inProd = False
        production = ''
        prodHead = ''
        #Find the lines where productions start
        for i in range(len(self.lines)):
            if matches(self.lines[i], '%%\n'):
                index = i
                break
        productions = self.lines[index+1:]
        #process productions
        for x in productions:
            x = x.strip()
            #We find the head of the production
            if matches(x, '(a-z)+:') and not inProd:
                inProd = True
                x = x.replace(':', '->')
                production += x
                prodHead = x
            elif matches(x, '(a-z):') and inProd:
                raise Exception(f"PRUDCCION INVALIDA ECONTRADO {x} ")
            #if there is an or we keep the head but reset the prodction
            elif inProd and startsWith(x, "'|'"):
                self.productions.append(production)
                production = ''
                production += prodHead
                beginning = findIn(x, "(a-z)|(A-Z)")
                beginning = beginning[0][2]
                production += x[beginning:]
            elif matches(x, ';') and inProd:
                inProd = False
                self.productions.append(production)
                production = ''
                prodHead = ''
            elif matches(x, ';') and not inProd:
                raise Exception(f"produccion INVALIDA {x}")
            elif inProd:
                production += x