"""
"""

import rply

# regex symbols
# unused symbols: \ . ? $ ^ ( ) { } + |
# used symbols: [ ] * **
# path symbol: /

lg = rply.LexerGenerator()

lg.add("ASTERISK", r"\*")
lg.add("BACKSLASH", r"\\")
lg.add("BRACKET_CLOSE", r"\]")
lg.add("BRACKET_OPEN", r"\[")
lg.add("SLASH", r"/")

lg.add("UNUSED_SYMBOL", r"[}{^$?)(.|+]")

lg.add("NONSYMBOLS", r"[^*\\}{\]\[^$?)(.|+/]+")

lexer = lg.build()

pg = rply.ParserGenerator([
    "ASTERISK",
    "BACKSLASH",
    "BRACKET_CLOSE",
    "BRACKET_OPEN",
    "SLASH",

    "UNUSED_SYMBOL",
    "NONSYMBOLS",
])

@pg.production("bracket_set : non_escape BRACKET_OPEN match_set BRACKET_CLOSE")

@pg.production("escaped_symbol : BACKSLASH UNUSED_SYMBOL")
def _escaped_symbol(p):
    return p[0].getstr() + p[1].getstr()

parser = pg.build()
