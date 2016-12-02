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

    # TODO:
    #   BETTER NAMES

    @pg.production("pattern : path_pattern")
    @pg.production("pattern : root_pattern")
    def _pattern(p):
        return ("pattern", p)

    # path_pattern has a SLASH somewhere in pattern
    @pg.production("path_pattern : trailing_slash_pattern")
    @pg.production("path_pattern : nontrail_slash_pattern")
    def _path_pattern(p):
        return ("path_pattern", p)

    # trailing_slash_pattern has a slash at the end
    @pg.production("trailing_slash_pattern : SLASH")
    @pg.production("trailing_slash_pattern : path_part SLASH")
    @pg.production("trailing_slash_pattern : nontrail_slash_pattern SLASH")
    def _trailing_slash_pattern(p):
        return ("trailing_slash_pattern", p)

    @pg.production("root_pattern : ASTERISK")
    @pg.production("root_pattern : path_part_a")
    @pg.production("root_pattern : ASTERISK path_part_a")
    def _root_pattern(p):
        return ("root_pattern", p)

    @pg.production("nontrail_slash_pattern : trailing_slash_pattern path_part")
    def _nontrail_slash_pattern(p):
        return ("nontrail_slash_pattern", p)

    @pg.production("path_part : ASTERISK ASTERISK")
    @pg.production("path_part : root_pattern")
    def _path_part(p):
        return ("path_part", p)

    @pg.production("path_part_a : path_part_b")
    @pg.production("path_part_a : path_part_a ASTERISK")
    def _path_part_a(p):
        return ("path_part_a", p)

    @pg.production("path_part_b : UNUSED_SYMBOL")
    @pg.production("path_part_b : NONSYMBOL")
    @pg.production("path_part_b : BRACKET_OPEN bracket_set BRACKET_CLOSE")
    @pg.production("path_part_b : escaped_symbol")
    @pg.production("path_part_b : path_part_b path_part_b")
    def _path_part_b(p):
        return ("path_part_b", p)

    @pg.production("bracket_set : ASTERISK")
    @pg.production("bracket_set : UNUSED_SYMBOL")
    @pg.production("bracket_set : NONSYMBOL")
    @pg.production("bracket_set : escaped_symbol")
    @pg.production("bracket_set : bracket_set bracket_set")
    def _bracket_set(p):
        return ("bracket_set", p)

    @pg.production("escaped_symbol : BACKSLASH ASTERISK")
    @pg.production("escaped_symbol : BACKSLASH BACKSLASH")
    @pg.production("escaped_symbol : BACKSLASH BRACKET_CLOSE")
    @pg.production("escaped_symbol : BACKSLASH BRACKET_OPEN")
    @pg.production("escaped_symbol : BACKSLASH SLASH")
    @pg.production("escaped_symbol : BACKSLASH UNUSED_SYMBOL")
    def _escaped_symbol(p):
        return ("escaped_symbol", p)

    return pg.build()
