from Functions import *
from regularExpression import *
from ExpressionTree import *
from AFD import *

def matches(string, regex):
    regex = regularExpression(regex)
    regex.augmentRegex()
    tree = ExpressionTree(regex.postfix)
    dfa = AFD(tree = tree)
    return dfa.simulate(string)

def findAll(line, regex):
    regex = regularExpression(regex)
    regex.augmentRegex()
    tree = ExpressionTree(regex.postfix)
    dfa = AFD(tree = tree)
    return dfa.scanner(line)