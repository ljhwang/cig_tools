"""Module that exports AST types for the filepatterns parser.
"""

import enum

import rply.token


@enum.unique
class PatternType(enum.Enum):
    root = 1
    part = 2

@enum.unique
class SlashType(enum.Enum):
    trailing = 1
    nontrail = 2


### Tokens ### Tokens ### Tokens ### v

class Token(rply.token.BaseBox):
    def __init__(self):
        pass

    def regex(self, **kwargs):
        raise NotImplementedError("Token regex call on {}".format(self))


class SlashToken(Token):
    def regex(self, **kwargs):
        return "/"


class WildPathToken(Token):
    def regex(self, **kwargs):
        return ".*"


class AsteriskToken(Token):
    def regex(self, **kwargs):
        return "[^/]*"


class NoAsteriskToken(Token):
    def __init__(self, token):
        self.token = token

    def regex(self, **kwargs):
        if isinstance(self.token, EscapedSymbolToken):
            return self.token.regex(**kwargs)
        else:
            return self.token.getstr()


class EscapedSymbolToken(Token):
    def __init__(self, tokens):
        self.tokens = tokens

    def regex(self, **kwargs):
        return "".join(token.getstr() for token in self.tokens)

### Tokens ### Tokens ### Tokens ### ^


### Patterns ### Patterns ### Patterns ### v

class Pattern(rply.token.BaseBox):
    pattern_type = None

    def __init__(self, ast):
        self.ast = ast

    def regex(self, pattern_type=None, **kwargs):
        if pattern_type is None:
            ret = ""
            if self.pattern_type == PatternType.root:
                ret = ".*"
            elif self.pattern_type == PatternType.part:
                ret = ""

            return ret + self.ast.regex(
                pattern_type=self.pattern_type, **kwargs
            )
        else:
            return self.ast.regex(
                pattern_type=pattern_type, **kwargs
            )


class PathPattern(Pattern):
    pattern_type = PatternType.part


class RootPattern(Pattern):
    pattern_type = PatternType.root

### Patterns ### Patterns ### Patterns ### ^


### SlashPatterns ### SlashPatterns ### SlashPatterns ### v

class SlashPattern(rply.token.BaseBox):
    slash_type = None

    def __init__(self, ast_seq):
        if isinstance(ast_seq[0], SlashPattern):
            self.ast_seq = ast_seq[0].ast_seq + [ast_seq[1]]
        else:
            self.ast_seq = ast_seq

    def regex(self, **kwargs):
        if self.slash_type == SlashType.trailing:
            return "".join(
                ast.regex(**kwargs)
                for ast in self.ast_seq
            ) + WildPathToken().regex()

        elif self.slash_type == SlashType.nontrail:
            return "".join(
                ast.regex(**kwargs)
                for ast in self.ast_seq
            )


class TrailingSlashPattern(SlashPattern):
    slash_type = SlashType.trailing


class NontrailSlashPattern(SlashPattern):
    slash_type = SlashType.nontrail

### SlashPatterns ### SlashPatterns ### SlashPatterns ### ^


### PathPart ### PathPart ### PathPart ### v

class PathPart(rply.token.BaseBox):
    def __init__(self, ast):
        self.ast = ast

    def regex(self, **kwargs):
        return self.ast.regex(**kwargs)

### PathPart ### PathPart ### PathPart ### ^


### AsteriskPart ### AsteriskPart ### AsteriskPart ### v

class AsteriskPart(rply.token.BaseBox):
    def __init__(self, ast_seq):
        if isinstance(ast_seq[0], AsteriskPart):
            self.ast_seq = ast_seq[0].ast_seq + [ast_seq[1]]
        else:
            self.ast_seq = ast_seq

    def regex(self, **kwargs):
        return "".join(
            ast.regex(**kwargs)
            for ast in self.ast_seq
        )

### AsteriskPart ### AsteriskPart ### AsteriskPart ### ^


### NoAsteriskPart ### NoAsteriskPart ### NoAsteriskPart ### v

class NoAsteriskPart(rply.token.BaseBox):
    def __init__(self, ast_seq):
        if isinstance(ast_seq[0], NoAsteriskPart):
            self.ast_seq = ast_seq[0].ast_seq + [ast_seq[1]]
        else:
            self.ast_seq = ast_seq

    def regex(self, **kwargs):
        return "".join(
            ast.regex(**kwargs)
            for ast in self.ast_seq
        )

### NoAsteriskPart ### NoAsteriskPart ### NoAsteriskPart ### ^


### NoAtrskBracketSet ### NoAtrskBracketSet ### NoAtrskBracketSet ### v

class NoAtrskBracketSet(rply.token.BaseBox):
    def __init__(self, ast):
        self.ast = ast

    def regex(self, **kwargs):
        return self.ast.regex(**kwargs)

### NoAtrskBracketSet ### NoAtrskBracketSet ### NoAtrskBracketSet ### ^


### BracketSet ### BracketSet ### BracketSet ### v

class BracketSet(rply.token.BaseBox):
    def __init__(self, ast_seq):
        if isinstance(ast_seq[0], BracketSet):
            self.ast_seq = ast_seq[0].ast_seq + [ast_seq[1]]
        else:
            self.ast_seq = ast_seq

    def regex(self, **kwargs):
        return "[" + "".join(
            ast.regex(**kwargs)
            for ast in self.ast_seq
        ) + "]"

### BracketSet ### BracketSet ### BracketSet ### ^


### BracketElem ### BracketElem ### BracketElem ### v

class BracketElem(rply.token.BaseBox):
    def __init__(self, ast):
        self.ast = ast

    def regex(self, **kwargs):
        if isinstance(self.ast, EscapedSymbolToken):
            return self.ast.regex(**kwargs)
        else:
            return self.ast.getstr()

### BracketElem ### BracketElem ### BracketElem ### ^

