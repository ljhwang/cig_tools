"""Module that exports AST types for the filepatterns parser.
"""

import rply.token


class UnitBox(rply.token.BaseBox):
    def __init__(self, token):
        self.token = token

    def getstr(self):
        return self.token.getstr()


class ListBox(rply.token.BaseBox):
    def __init__(self, *tokens):
        self.tokens = list(tokens)

    def __add__(self, listbox):
        self.tokens += listbox.tokens
        return self

    def getstr(self):
        return "".join(token.getstr() for token in self.tokens)


class EscapedSymbol(UnitBox):
    def getstr(self):
        return "\\" + self.token.getstr()


class BracketSet(ListBox):
    def getstr(self):
        return "[{}]".format("".join(token.getstr() for token in self.tokens))


class NoAtrskPart(ListBox):
    pass


class NonTrailAtrskPart(ListBox):
    pass


class TrailingAtrskPart(ListBox):
    def getstr(self, root_pattern=False):
        if root_pattern:
            pass
        else:
            pass


class PathPart(ListBox):
    pass
