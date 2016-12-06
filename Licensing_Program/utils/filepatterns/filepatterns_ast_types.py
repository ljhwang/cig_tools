"""Module that exports AST types for the filepatterns parser.
"""

import rply.token


class UnitBox(rply.token.BaseBox):
    def __init__(self, token):
        self.token = token


class ListBox(rply.token.BaseBox):
    def __init__(self, *tokens):
        self.tokens = list(tokens)

    def __add__(self, listbox):
        self.tokens += listbox.tokens
        return self


class EscapedSymbol(UnitBox):
    def getstr(self):
        return "\\{}".format(token.getstr())


class BracketSet(ListBox):
    def getstr(self):
        return "[{}]".format("".join(token.getstr() for token in self.tokens))


class PathPart(ListBox):
    def getstr(self):
        return "".join(token.getstr() for token in self.tokens)
