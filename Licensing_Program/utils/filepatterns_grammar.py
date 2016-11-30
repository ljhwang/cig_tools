"""
"""

import rply


def _create_lexer():
    """
    """
    lg = rply.LexerGenerator()

    lg.add("ASTERISK", r"\*")
    lg.add("BACKSLASH", r"\\")
    lg.add("BRACKET_CLOSE", r"\]")
    lg.add("BRACKET_OPEN", r"\[")
    lg.add("SLASH", r"/")
    lg.add("UNUSED_SYMBOL", r"[$()+.?^{|}]")
    lg.add("NONSYMBOL", r"[^$()*+./?\[\\\]^{|}]")

    return lg.build()


def _create_parser():
    """
    """
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
    @pg.production("pattern : escaped_symbol")
    @pg.production("pattern : BRACKET_OPEN bracket_pattern BRACKET_CLOSE")
    @pg.production("pattern : pattern pattern")
    def _pattern(p):
        return p

    @pg.production("bracket_pattern : ASTERISK")
    @pg.production("bracket_pattern : SLASH")
    @pg.production("bracket_pattern : UNUSED_SYMBOL")
    @pg.production("bracket_pattern : NONSYMBOL")
    @pg.production("bracket_pattern : escaped_symbol")
    @pg.production("bracket_pattern : bracket_pattern bracket_pattern")
    def _bracket_pattern(p):
        return p

    @pg.production("escaped_symbol : BACKSLASH ASTERISK")
    @pg.production("escaped_symbol : BACKSLASH BACKSLASH")
    @pg.production("escaped_symbol : BACKSLASH BRACKET_CLOSE")
    @pg.production("escaped_symbol : BACKSLASH BRACKET_OPEN")
    @pg.production("escaped_symbol : BACKSLASH SLASH")
    @pg.production("escaped_symbol : BACKSLASH UNUSED_SYMBOL")
    def _escaped_symbol(p):
        return p

    return pg.build()
