"""Module for filepattern grammar. Exports `create_parser` function.
"""

import rply


def create_parser():
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

    @pg.production("pattern : path_pattern")
    @pg.production("pattern : root_pattern")
    def _pattern(p):
        return ("pattern", p)

    @pg.production("path_pattern : trailing_slash_pattern")
    @pg.production("path_pattern : nontrail_slash_pattern")
    def _path_pattern(p):
        return ("path_pattern", p)

    @pg.production("trailing_slash_pattern : SLASH")
    @pg.production("trailing_slash_pattern : path_part SLASH")
    @pg.production("trailing_slash_pattern : nontrail_slash_pattern SLASH")
    def _trailing_slash_pattern(p):
        return ("trailing_slash_pattern", p)

    @pg.production("nontrail_slash_pattern : trailing_slash_pattern path_part")
    def _nontrail_slash_pattern(p):
        return ("nontrail_slash_pattern", p)

    @pg.production("path_part : ASTERISK ASTERISK")
    @pg.production("path_part : root_pattern")
    def _path_part(p):
        return ("path_part", p)

    @pg.production("root_pattern : no_atrsk_part")
    @pg.production("root_pattern : trailing_atrsk_part")
    @pg.production("root_pattern : nontrail_atrsk_part")
    def _root_pattern(p):
        return ("root_pattern", p)

    @pg.production("trailing_atrsk_part : ASTERISK")
    @pg.production("trailing_atrsk_part : no_atrsk_part ASTERISK")
    @pg.production("trailing_atrsk_part : nontrail_atrsk_part ASTERISK")
    def _trailing_atrsk_part(p):
        return ("trailing_atrsk_part", p)

    @pg.production("nontrail_atrsk_part : trailing_atrsk_part no_atrsk_part")
    def _nontrail_atrsk_part(p):
        return ("nontrail_atrsk_part", p)

    @pg.production("no_atrsk_part : UNUSED_SYMBOL")
    @pg.production("no_atrsk_part : NONSYMBOL")
    @pg.production("no_atrsk_part : BRACKET_OPEN bracket_set BRACKET_CLOSE")
    @pg.production("no_atrsk_part : escaped_symbol")
    @pg.production("no_atrsk_part : no_atrsk_part no_atrsk_part")
    def _no_atrsk_part(p):
        return ("no_atrsk_part", p)

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
