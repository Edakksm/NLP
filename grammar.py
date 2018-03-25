"""
COMS W4705 - Natural Language Processing - Spring 2018
Homework 2 - Parsing with Context Free Grammars 
Daniel Bauer
"""

import sys
from collections import defaultdict
from math import fsum

class Pcfg(object): 
    """
    Represent a probabilistic context free grammar. 
    """

    def __init__(self, grammar_file): 
        self.rhs_to_rules = defaultdict(list)
        self.lhs_to_rules = defaultdict(list)
        self.startsymbol = None 
        self.read_rules(grammar_file)      
 
    def read_rules(self,grammar_file):
        
        for line in grammar_file: 
            line = line.strip()
            if line and not line.startswith("#"):
                if "->" in line: 
                    rule = self.parse_rule(line.strip())
                    lhs, rhs, prob = rule
                    self.rhs_to_rules[rhs].append(rule)
                    self.lhs_to_rules[lhs].append(rule)
                else: 
                    startsymbol, prob = line.rsplit(";")
                    self.startsymbol = startsymbol.strip()
                    
     
    def parse_rule(self,rule_s):
        lhs, other = rule_s.split("->")
        lhs = lhs.strip()
        rhs_s, prob_s = other.rsplit(";",1) 
        prob = float(prob_s)
        rhs = tuple(rhs_s.strip().split())
        return (lhs, rhs, prob)

    def verify_grammar(self):
        """
        Return True if the grammar is a valid PCFG in CNF.
        Otherwise return False. 
        """
        for keys in self.lhs_to_rules.keys():
            itemset = self.lhs_to_rules[keys]
            item_prob = []
            for item in itemset:
                lhs = item[0]
                rhs = item[1]
                if not(len(rhs) == 1 or len(rhs) == 2):
                    return False
                    break
                if(len(rhs) == 2):
                    if not (rhs[0].isupper() and rhs[1].isupper()):
                        return  False
                        break
                elif(len(rhs) == 1):
                    if not(rhs[0].islower()):
                        return False
                        break
                item_prob.append(item[2])

            if round(fsum(item_prob),1) != 1.0:
                 return False
                 break
            return True


if __name__ == "__main__":
    with open('atis3.pcfg','r') as grammar_file:
        grammar = Pcfg(grammar_file)
        status = grammar.verify_grammar()
        print(status)

