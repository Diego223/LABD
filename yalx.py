from keys import *
from scannerFunctions import *


class YalProcessor:
    def __init__(self, yal_file):
        self.yal_file = yal_file
        self.rules = {}
        self.comments = []
        self.ruleTokens = {}
        self.ruleTokensExpression = ''
        self.ruleTokenstree = None
        self.lines = []
        self.process_yal()
        self.get_tokens()

    def extract_lines(self):
        with open(self.yal_file, 'r') as f:
            lines = f.readlines()
        self.lines = lines

    def extract_comments(self):
        for line in self.lines:
            if line.startswith('"(*"') and line.endswith('*")"'):
                self.comments.append(line)
            else: 
                regex = '"("* (A-Z)(a-z)+ ((a-z)+((, )| ))∗*")"'
                finds = findAll(line, regex)
                if finds[0] != None and finds[0] not in self.comments:
                    self.comments.append(finds[0])

    def process_yal(self):
        self.extract_lines()
        self.extract_comments()
        for line in self.lines:
            if line.startswith("let"):
                line = line.replace('*', '∗')
                rule_name, rule_body = self.extract_rule(line)
                regex_rule = self.to_regex(rule_body)
                self.rules[rule_name] = regex_rule
        for rule_name, regex_rule in self.rules.items():
            updated_rule = self.replace_rules(regex_rule)
            self.rules[rule_name] = updated_rule

    def replace_rules(self, regex_rule):
        sorted_rule_names = sorted(self.rules.keys(), key=len, reverse=True)
        for rule_name in sorted_rule_names:
            rule_body = self.rules[rule_name]
            if rule_name in regex_rule:
                if regex_rule.endswith(f"{rule_name}+") or (f"{rule_name}+" in regex_rule):
                    if rule_body.startswith("(") and rule_body.endswith(")"):
                        regex_rule = regex_rule.replace(f"{rule_name}+", f'{rule_body}+')
                    else:
                        regex_rule = regex_rule.replace(f"{rule_name}+", f'({rule_body})+')
                else:
                    regex_rule = regex_rule.replace(rule_name, f'{rule_body}')
        return regex_rule

    def get_tokens(self):
        rulelines = []
        for i in range(len(self.lines)):
            if self.lines[i].startswith("rule tokens"):
                rulelines = self.lines[i:]
                break
        for line in rulelines:
            if line.startswith('"('):
                continue
            else:
                linesplit = line.split("  ")
                print(linesplit)

    @staticmethod
    def extract_rule(line):
        tokens = line.split('=')
        rule_name = tokens[0].strip()[4:]
        rule_body = tokens[1].strip()
        return rule_name, rule_body

    @staticmethod
    def to_regex(rule_body):
        regex_rule = ""
        i = 0
        while i < len(rule_body):
            if rule_body[i] == "{":
                i += 1
                inside_brackets = ""
                while rule_body[i] != "}":
                    inside_brackets += rule_body[i]
                    i += 1
                ranges = inside_brackets.split("''")
                operands = []
                for r in ranges:
                    if '-' in r and r.index('-') > 0 and r.index('-') < len(r) - 1:
                        start, end = r.split('-')
                        start = start.replace("'", "")  
                        end = end.replace("'", "") 
                        string = Lparen + start + '-' + end + Rparen 
                        operands.append(string) 
                    else:
                        r = r.replace("'", "") 
                        for x in r:
                            if x in [*operators, minus]:
                                r = f"'{x}'" 
                        operands.append(r) 
                regex_rule +=  alternative.join(operands) 
            else:
                regex_rule += rule_body[i]
            i += 1
        return regex_rule