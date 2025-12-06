"""
Constants used throughout the Lispy interpreter.
"""
LPAREN = '('
RPAREN = ')'
QUOTE_CHAR = "'"
QUASIQUOTE_CHAR = "`"
UNQUOTE_CHAR = ","
UNQUOTE_SPLICING_CHAR = ",@"
STRING_QUOTE = '"'
COMMENT_CHAR = ';'

TRUE_LITERAL = '#t'
FALSE_LITERAL = '#f'

READ_CHUNK_SIZE = 1
COMPLEX_IMAG_CHAR_SCHEME = 'i'
COMPLEX_IMAG_CHAR_PYTHON = 'j'
FILE_WRITE_MODE = 'w'

# Special characters that delimit atoms
_SPECIAL_CHARS = "".join([
    LPAREN, RPAREN, QUOTE_CHAR, QUASIQUOTE_CHAR, UNQUOTE_CHAR, STRING_QUOTE, COMMENT_CHAR
])

TOKENIZER_REGEX = r''.join([
    r'\s*',
    r'(',
    r'{unquote_splicing}|'.format(unquote_splicing=UNQUOTE_SPLICING_CHAR),
    r"[{special_single}]|".format(special_single=LPAREN + QUOTE_CHAR + QUASIQUOTE_CHAR + UNQUOTE_CHAR + RPAREN),
    r'{quote}(?:[\\].|[^\\{quote}])*{quote}|'.format(quote=STRING_QUOTE),
    r'{comment}.*|'.format(comment=COMMENT_CHAR),
    r'''[^\s{special_chars}]*'''.format(special_chars=_SPECIAL_CHARS),
    r')',
    r'(.*)',
])
