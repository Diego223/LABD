from keys import *
from scannerFunctions import *

class YalProcessor:
    def __init__(self, yal_file):
        self.yal_file = yal_file
        self.lines = []
        self.rules = {}
        self.comments = []
        #{token/rule: return value}
        self.ruleTokens = {}
        self.tokenRules = []
        self.tokensExp = ''
        self.process_yal()
        self.get_tokens()
        self.gen_file()

    @staticmethod
    def extract_rule(line):
        tokens = line.split('=')
        rule_name = tokens[0].strip()[4:]
        rule_body = tokens[1].strip()
        return rule_name, rule_body

    @staticmethod
    def convert_to_regex(rule_body):
        regex_rule = ""
        i = 0
        while i < len(rule_body):
            if rule_body[i] == Lbrace:
                i += 1
                inside_brackets = ""
                while rule_body[i] != Rbrace:
                    inside_brackets += rule_body[i]
                    i += 1
                ranges = inside_brackets.split("''")
                operands = []  # Initialize an empty list to store operands
                for r in ranges:
                    if '-' in r and r.index('-') > 0 and r.index('-') < len(r) - 1:
                        start, end = r.split('-')
                        start = start.replace("'", "")  # Remove single quotes from start
                        end = end.replace("'", "")  # Remove single quotes from end
                        string = start + '-' + end   # Create a range string
                        operands.append(string)  # Add the range to the operands list
                    else:
                        r = r.replace("'", "")  # Remove single quotes from r
                        for x in r:
                            if x in [*operators, minus]:
                                r = f"'{x}'" 
                        operands.append(r)  # Add the character to the operands list 
                #join operands with l paren and right paren when they dont have 
                regex_rule += Lparen + alternative.join(operands ) + Rparen
            else:
                regex_rule += rule_body[i]
            i += 1
        return regex_rule

    def extract_lines(self):
        with open(self.yal_file, 'r') as f:
            lines = f.readlines()
        self.lines = lines

    def extract_comments(self):
        for line in self.lines:
            if startsWith(line, "'('*") and endsWith(line, "*')'"):
                self.comments.append(line)
            else: 
                regex = "'('* (A-Z)(a-z)+ ((a-z)+((, )| ))∗*')'"
                finds = findIn(line, regex)
                if len(finds)>0 and finds[0] not in self.comments:
                    self.comments.append(finds[0])

    def process_yal(self):
        self.extract_lines()
        self.extract_comments()
        for line in self.lines:
            if startsWith(line, "let"):
                line = line.replace("*", "∗")
                rule_name, rule_body = self.extract_rule(line)
                regex_rule = self.convert_to_regex(rule_body)
                self.rules[rule_name] = regex_rule
        # Replace rules in other rules
        for rule_name, regex_rule in self.rules.items():
            updated_rule = self.replace_rules(regex_rule)
            self.rules[rule_name] = updated_rule

    def replace_rules(self, regex_rule):
        sorted_rule_names = sorted(self.rules.keys(), key=len, reverse=True)
        for rule_name in sorted_rule_names:
            rule_body = self.rules[rule_name]
            if rule_name in regex_rule:
                if regex_rule.endswith(f"{rule_name}+") or (f"{rule_name}+" in regex_rule):
                    if rule_body.startswith(Lparen) and rule_body.endswith(Rparen):
                        regex_rule = regex_rule.replace(f"{rule_name}+", f'{rule_body}+')
                    else:
                        regex_rule = regex_rule.replace(f"{rule_name}+", f'({rule_body})+')
                else:
                    regex_rule = regex_rule.replace(rule_name, f'{rule_body}')
        return regex_rule

    def get_tokens(self):
        rulelines = []
        returns = {}
        #take only the lines from rule tokens to the end
        for i in range(len(self.lines)):
            if startsWith(self.lines[i], "rule tokens"):
                rulelines = self.lines[i+1:-2]
                break
        #first check for lines that dont have a return value
        norets = findMissing(rulelines, "'{' return (A-Z)+ '}'")
        for key, value in norets.items():
            value = 'NS'
            returns[key] = value
        #get the tokens and their expressions
        for line in rulelines:
            line = splitString(line, " ")
            #remove empty strings
            line = [x for x in line if x != '']
            if not matches(line[0], "'|'"):
                #remove line jump from end of line[0]
                if line[0][-1] == "\n":
                    line[0] = line[0][:-1]
                line = [line[0]]
                if len(line) == 1:
                    returns[0] = 'NS'
            else:
                line = line[:2]
                if '"' in line[1]:
                    line[1] = line[1].replace('"', "'")
            #extract expressions for tokens
            if len(line) > 1:
                self.tokenRules.append(line[1])
            elif len(line) == 1:
                self.tokenRules.append(line[0])
            self.tokensExp += ''.join(line)
        self.tokensExp = self.replace_rules(self.tokensExp)
        #get what each value returns
        returns.update(findAll(rulelines, "'{' return (A-Z)+ '}'"))
        for key, value in returns.items():
            value = splitString(value[0][0])
            for x in value:
                if matches(x, '(A-Z)+'):
                    returns[key] = x
        for i in range(len(self.tokenRules)):
            self.ruleTokens[self.replace_rules(self.tokenRules[i])] = returns[i]

    def gen_file(self):
        content = ''
        content += "from tokens import *\n\
from scannerFunctions import *\n\
from AFD import *\n\
from ExpressionTree import *\n\
from regularExpression import *\n\
\n\
"
        #add to content the rules as key = value
        for key, value in self.rules.items():
            content+= f"{key} = {value}\n"
        content += "\n"
        #add rule tokens expression
        content += f'tokensExp = "{self.tokensExp}"\n'
        print(content)
