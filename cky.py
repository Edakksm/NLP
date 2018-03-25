"""
COMS W4705 - Natural Language Processing - Spring 2018
Homework 2 - Parsing with Context Free Grammars 
Daniel Bauer
"""
import math
import sys
from collections import defaultdict
import itertools
from grammar import Pcfg
import numpy as np

### Use the following two functions to check the format of your data structures in part 3 ###
def check_table_format(table):
    """
    Return true if the backpointer table object is formatted correctly.
    Otherwise return False and print an error.
    """
    if not isinstance(table, dict):
        sys.stderr.write("Backpointer table is not a dict.\n")
        return False
    for split in table:
        if not isinstance(split, tuple) and len(split) ==2 and \
          isinstance(split[0], int)  and isinstance(split[1], int):
            sys.stderr.write("Keys of the backpointer table must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of backpointer table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str):
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            bps = table[split][nt]
            if isinstance(bps, str): # Leaf nodes may be strings
                continue
            if not isinstance(bps, tuple):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Incorrect type: {}\n".format(bps))
                return False
            if len(bps) != 2:
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Found more than two backpointers: {}\n".format(bps))
                return false
            for bp in bps:
                if not isinstance(bp, tuple) or len(bp)!=3:
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has length != 3.\n".format(bp))
                    return False
                if not (isinstance(bp[0], str) and isinstance(bp[1], int) and isinstance(bp[2], int)):
                    print(bp)
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has incorrect type.\n".format(bp))
                    return False
    return True

def check_probs_format(table):
    """
    Return true if the probability table object is formatted correctly.
    Otherwise return False and print an error.
    """
    if not isinstance(table, dict):
        sys.stderr.write("Probability table is not a dict.\n")
        return False
    for split in table:
        if not isinstance(split, tuple) and len(split) ==2 and isinstance(split[0], int) and isinstance(split[1], int):
            sys.stderr.write("Keys of the probability must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of probability table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str):
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            prob = table[split][nt]
            if not isinstance(prob, float):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a float.{}\n".format(prob))
                return False
            if prob > 0:
                sys.stderr.write("Log probability may not be > 0.{}\n".format(prob))
                return False
    return True



class CkyParser(object):
    """
    A CKY parser.
    """

    def __init__(self, grammar):
        """
        Initialize a new parser instance from a grammar.
        """
        self.grammar = grammar

    def is_in_language(self,tokens):
        """
        Membership checking. Parse the input tokens and return True if
        the sentence is in the language described by the grammar. Otherwise
        return False
        """
        tree, probs = self.parse_with_backpointers(tokens)

        if grammar.startsymbol in tree[(0, len(tokens))]:
            return True
        else:
            return False

    def parse_with_backpointers(self, tokens):
        """
        Parse the input tokens and return a parse table and a probability table.
        """
        # TODO, part 3
        table = defaultdict(defaultdict)
        backpointers = defaultdict()
        rhs_rules = self.grammar.rhs_to_rules
        number_of_tokens = len(tokens)

        probs = defaultdict(defaultdict)
        problist = defaultdict()

        # Fill the diagonals
        for j in range(1, number_of_tokens + 1):
            rules = rhs_rules[(tokens[j - 1],)]
            for rule in rules:
                backpointers[rule[0]] = rule[1][0]
                problist[rule[0]] = np.log(rule[2])
            table[(j - 1, j)] = backpointers
            probs[(j - 1, j)] = problist
            backpointers = defaultdict()
            problist = defaultdict()
        i = 0
        lhsProb = 1.0
        rhsProb = 1.0
        totalProb = 1.0
        currProb = 1.0
        for p in range(2, number_of_tokens + 1):
            for j in range(p, number_of_tokens + 1):
                i = j - p
                for k in range(i + 1, j):
                    val1 = table.get((i,k))
                    val2 = table.get((k,j))
                    if val1 is not None and val2 is not None and len(val1) > 0 and len(val2) > 0:
                        val1 = val1.keys()
                        val2 = val2.keys()
                        result = []
                        for val_1 in val1:
                            for val_2 in val2:
                                result.append((val_1, val_2))
                        for res in result:
                             child_rules = rhs_rules[res]
                             for c_rule in child_rules:
                                 pointer = ((c_rule[1][0], i, k), (c_rule[1][1], k, j))
                                 lhs = c_rule[0]
                                 lhsProb = probs[(i,k)][c_rule[1][0]]
                                 rhsProb = probs[(k,j)][c_rule[1][1]]
                                 currProb = c_rule[2]
                                 totalProb = lhsProb + np.log(currProb) + rhsProb
                                 nodeProb = problist.get(lhs)
                                 if(nodeProb is None):
                                     problist[lhs] = totalProb
                                     backpointers[lhs] = pointer
                                 if(nodeProb is not None and totalProb > nodeProb):
                                    problist[lhs] = totalProb
                                    backpointers[lhs] = pointer
                if len(backpointers) > 0:
                   table[(i,j)] = backpointers
                   probs[(i,j)] = problist
                   backpointers = defaultdict()
                   problist = defaultdict()
                else:
                    table[(i,j)] = defaultdict()
        return table, probs



def get_tree(table, i, j, nt):
    """
    Return the parse-tree rooted in non-terminal nt and covering span i,j.
    """
    if isinstance(table[(i, j)][nt], str):
        return(nt, table[(i,j)][nt])

    else:
        lchild = table[(i, j)][nt][0]
        rchild = table[(i, j)][nt][1]
        return (nt, get_tree(table,lchild[1], lchild[2], lchild[0]), get_tree(table, rchild[1], rchild[2], rchild[0]))

if __name__ == "__main__":

    with open('atis3.pcfg','r') as grammar_file:
        grammar = Pcfg(grammar_file)
        parser = CkyParser(grammar)
        toks = ['flights', 'from', 'miami', 'to', 'cleveland', '.']
        print(parser.is_in_language(toks))
        table, probs = parser.parse_with_backpointers(toks)
        assert check_table_format(table)
        assert check_probs_format(probs)
      #  print(table)
        tree = get_tree(table, 0, len(toks), grammar.startsymbol)
        print(tree)
        
