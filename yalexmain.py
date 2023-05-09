from regularExpression import *
from ExpressionTree import *
from AFN import *
from AFD import *
from yalx import *
from par import *
from Grammar import *


def to_regex(rule_body):
        regex_rule = ""
        i = 0
        Lbrace = '['
        Rbrace = ']'

        while i < len(rule_body):
            if rule_body[i] == Lbrace:
                i += 1
                inside_brackets = ""
                while rule_body[i] != Rbrace:
                    inside_brackets += rule_body[i]
                    i += 1
                expression = inside_brackets.split("''")
                operands = [] 
                for exp in expression:
                    operands.append(exp)

                regex_rule += "(" + "|".join(operands) + ")"
            else:
                regex_rule += rule_body[i]

            i += 1

        return regex_rule



def separate_symbols(regex_rule):
    regex_rule = regex_rule.replace("('+|-')", "('+'|'-')")
    return regex_rule


def main():
    while True:
        option = input("INGRESA TU ARCHIVO YAL: ")
        patharchivo = f"slr-{option}.yal"
        yal = YalProcessor(patharchivo)
        
        print(yal.tokenRules)
        patharchivo = f"slr-{option}.yalp"
        par = yaparProcessor(patharchivo)
        gm = Grammar(par.productions)
        states, transitions = gm.constructlr0()
        printlr0(states, transitions)
        drawlr0(states, transitions)
        if option == 'exit':
            print('\n\nSaliste\n\n')
            break

if __name__ == "__main__":
    main()
