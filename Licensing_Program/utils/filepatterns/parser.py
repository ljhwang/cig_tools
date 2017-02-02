"""Module for filepattern grammar. Exports `create_parser` function.
"""

import rply

import filepatterns.ast_types as ast_types


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
        return ast_types.Pattern(p[0])

    @pg.production("path_pattern : trailing_slash_pattern")
    @pg.production("path_pattern : nontrail_slash_pattern")
    def _path_pattern(p):
        return ast_types.PathPattern(p[0])

    @pg.production("trailing_slash_pattern : SLASH")
    @pg.production("trailing_slash_pattern : path_part SLASH")
    @pg.production("trailing_slash_pattern : nontrail_slash_pattern SLASH")
    def _trailing_slash_pattern(p):
        if len(p) == 1:
            return ast_types.SlashToken()
        elif len(p) == 2:
            return ast_types.TrailingSlashPattern(
                [p[0], ast_types.SlashToken()]
            )

    @pg.production("nontrail_slash_pattern : trailing_slash_pattern path_part")
    def _nontrail_slash_pattern(p):
        return ast_types.NontrailSlashPattern(p)

    @pg.production("path_part : ASTERISK ASTERISK")
    @pg.production("path_part : root_pattern")
    def _path_part(p):
        if len(p) == 1:
            return ast_types.PathPart(p[0])
        elif len(p) == 2:
            return ast_types.WildPathToken()

    @pg.production("root_pattern : no_atrsk_part")
    @pg.production("root_pattern : trailing_atrsk_part")
    @pg.production("root_pattern : nontrail_atrsk_part")
    def _root_pattern(p):
        return ast_types.RootPattern(p[0])

    @pg.production("trailing_atrsk_part : ASTERISK")
    @pg.production("trailing_atrsk_part : no_atrsk_part ASTERISK")
    @pg.production("trailing_atrsk_part : nontrail_atrsk_part ASTERISK")
    def _trailing_atrsk_part(p):
        if len(p) == 1:
            return ast_types.AsteriskToken()
        elif len(p) == 2:
            return ast_types.AsteriskPart(
                [p[0], ast_types.AsteriskToken()]
            )

    @pg.production("nontrail_atrsk_part : trailing_atrsk_part no_atrsk_part")
    def _nontrail_atrsk_part(p):
        return ast_types.AsteriskPart(p)

    @pg.production("no_atrsk_part : no_atrsk_elem")
    @pg.production("no_atrsk_part : no_atrsk_part no_atrsk_elem")
    def _no_atrsk_part(p):
        return ast_types.NoAsteriskPart(p)

    @pg.production("no_atrsk_elem : UNUSED_SYMBOL")
    @pg.production("no_atrsk_elem : NONSYMBOL")
    @pg.production("no_atrsk_elem : escaped_symbol")
    @pg.production("no_atrsk_elem : BRACKET_OPEN bracket_set BRACKET_CLOSE")
    def _no_atrsk_elem(p):
        if len(p) == 1:
            return ast_types.NoAsteriskToken(p[0])
        elif len(p) == 3:
            return ast_types.NoAtrskBracketSet(p[1])

    @pg.production("bracket_set : bracket_elem")
    @pg.production("bracket_set : bracket_set bracket_elem")
    def _bracket_set(p):
        return ast_types.BracketSet(p)

    @pg.production("bracket_elem : ASTERISK")
    @pg.production("bracket_elem : UNUSED_SYMBOL")
    @pg.production("bracket_elem : NONSYMBOL")
    @pg.production("bracket_elem : escaped_symbol")
    def _bracket_elem(p):
        return ast_types.BracketElem(p[0])

    @pg.production("escaped_symbol : BACKSLASH ASTERISK")
    @pg.production("escaped_symbol : BACKSLASH BACKSLASH")
    @pg.production("escaped_symbol : BACKSLASH BRACKET_CLOSE")
    @pg.production("escaped_symbol : BACKSLASH BRACKET_OPEN")
    @pg.production("escaped_symbol : BACKSLASH SLASH")
    @pg.production("escaped_symbol : BACKSLASH UNUSED_SYMBOL")
    def _escaped_symbol(p):
        return ast_types.EscapedSymbolToken(p)

    return pg.build()
