"""Module for filepattern grammar. Exports `create_lexer` function.
"""

import rply


def create_lexer():
    """Return `rply` lexer for filepatterns.
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
