from collections import defaultdict
from graphviz import Digraph

class Grammar:
    def __init__(self, rules):
        self.rules = [tuple(rule.split("->")) for rule in rules]
        self.non_terminals = set(nt for nt, _ in self.rules)
        self.terminals = set(t for _, prod in self.rules for t in prod.split()) - self.non_terminals

    def productions(self, non_terminal):
        return [prod for nt, prod in self.rules if nt == non_terminal]

    def closure(self, item_set):
        closure_set = set(item_set)
        while True:
            new_items = set()
            for nt, prod, dot_pos in closure_set:
                if dot_pos < len(prod.split()):
                    next_symbol = prod.split()[dot_pos]
                    if next_symbol in self.non_terminals:
                        for new_prod in self.productions(next_symbol):
                            new_items.add((next_symbol, new_prod, 0))
            if new_items.issubset(closure_set):
                break
            closure_set |= new_items
        return closure_set

    def goto(self, item_set, symbol):
        new_item_set = set()
        for nt, prod, dot_pos in item_set:
            if dot_pos < len(prod.split()) and prod.split()[dot_pos] == symbol:
                new_item_set.add((nt, prod, dot_pos + 1))
        return self.closure(new_item_set)

    def first(self):
        first_sets = {nt: set() for nt in self.non_terminals}
        change = True
        while change:
            change = False
            for nt, prod in self.rules:
                first = prod.split()[0]
                if first in self.terminals:
                    if first not in first_sets[nt]:
                        first_sets[nt].add(first)
                        change = True
                elif first in self.non_terminals:
                    for f in first_sets[first]:
                        if f not in first_sets[nt]:
                            first_sets[nt].add(f)
                            change = True
        return first_sets

    def follow(self, start_symbol):
        follow_sets = {nt: set() for nt in self.non_terminals}
        follow_sets[start_symbol].add('$')
        change = True
        while change:
            change = False
            for nt, prod in self.rules:
                prod_symbols = prod.split()
                for i, symbol in enumerate(prod_symbols):
                    if symbol in self.non_terminals:
                        if i < len(prod_symbols) - 1:
                            next_symbol = prod_symbols[i + 1]
                            if next_symbol in self.terminals:
                                if next_symbol not in follow_sets[symbol]:
                                    follow_sets[symbol].add(next_symbol)
                                    change = True
                            elif next_symbol in self.non_terminals:
                                for f in self.compute_first_sets()[next_symbol]:
                                    if f not in follow_sets[symbol]:
                                        follow_sets[symbol].add(f)
                                        change = True
                        if i == len(prod_symbols) - 1 or (i < len(prod_symbols) - 1 and prod_symbols[i + 1] in self.non_terminals):
                            for f in follow_sets[nt]:
                                if f not in follow_sets[symbol]:
                                    follow_sets[symbol].add(f)
                                    change = True
        return follow_sets
    
    def constructlr0(self):
        start_symbol = self.rules[0][0]
        start_item = (start_symbol, self.rules[0][1], 0)
        initial_state = self.closure({start_item})
        states = [initial_state]
        transitions = defaultdict(dict)
        unprocessed = [initial_state]
        while unprocessed:
            state = unprocessed.pop()
            for symbol in self.terminals | self.non_terminals:
                next_state = self.goto(state, symbol)
                if next_state and next_state not in states:
                    states.append(next_state)
                    unprocessed.append(next_state)
                if next_state:
                    transitions[frozenset(state)][symbol] = frozenset(next_state)
        return states, transitions

def drawlr0(states, transitions):
    dot = Digraph(format='pdf', engine='dot')
    # Add nodes
    for i, state in enumerate(states):
        state_label = f"ESTADOS {i}\n"
        state_label += "\n".join([f"{nt} -> {prod[:dot_pos]}.{prod[dot_pos:]}" for nt, prod, dot_pos in state])
        dot.node(str(i), label=state_label)
    # Add edges
    for state in states:
        for symbol, next_state in transitions[frozenset(state)].items():
            dot.edge(str(states.index(state)), str(states.index(next_state)), label=symbol)
    dot.render(f'GRAFICAS/LR0', view=True)

# Helper function to print the states and transitions of the LR(0) DFA
def printlr0(states, transitions):
    print("LR(0) ESTADOS DEL AFD:")
    for i, state in enumerate(states):
        print(f"ESTADO {i}:")
        for item in state:
            print("  ", *item)
        print()

    print("LR(0) TRANSISIONES DEL AFD:")
    for state in states:
        for symbol, next_state in transitions[frozenset(state)].items():
            print(f"({states.index(state)}, {symbol}) -> {states.index(next_state)}")
    print()
