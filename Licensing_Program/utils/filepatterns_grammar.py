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
lg.add("UNUSED_SYMBOL", r"[$()+.?^{|}]")
lg.add("NONSYMBOL", r"[^$()*+./?\[\\\]^{|}]")

lexer = lg.build()

pg = rply.ParserGenerator(
    [
        "ASTERISK",
        "BACKSLASH",
        "BRACKET_CLOSE",
        "BRACKET_OPEN",
        "SLASH",
        "UNUSED_SYMBOL",
        "NONSYMBOL",
    ]
)


@pg.production("pattern : NONSYMBOL")
@pg.production("pattern : UNUSED_SYMBOL")
@pg.production("pattern : BRACKET_OPEN bracket_pattern BRACKET_CLOSE")
@pg.production("pattern : pattern pattern")
def _pattern(p):
    return "e"


@pg.production("bracket_pattern : ASTERISK")
@pg.production("bracket_pattern : BACKSLASH BACKSLASH")
@pg.production("bracket_pattern : BACKSLASH BRACKET_CLOSE")
@pg.production("bracket_pattern : BACKSLASH BRACKET_OPEN")
@pg.production("bracket_pattern : SLASH")
@pg.production("bracket_pattern : UNUSED_SYMBOL")
@pg.production("bracket_pattern : NONSYMBOL")
@pg.production("bracket_pattern : bracket_pattern bracket_pattern")
def _bracket_pattern(p):
    return "c"


parser = pg.build()
