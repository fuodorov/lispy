# Parser constants
TOKENIZER_REGEX = r'''\s*(,@|[('`,)]|"(?:[\\].|[^\\"])*"|;.*|[^\s('"`,;)]*)(.*)'''
LPAREN = '('
RPAREN = ')'
TRUE_LITERAL = '#t'
FALSE_LITERAL = '#f'
STRING_QUOTE = '"'
COMMENT_CHAR = ';'

# REPL constants
PROMPT = 'lispy> '
VERSION_STRING = "Lispy version 2.0\n"

# Quote characters
QUOTE_CHAR = "'"
QUASIQUOTE_CHAR = "`"
UNQUOTE_CHAR = ","
UNQUOTE_SPLICING_CHAR = ",@"

# Parser configuration
READ_CHUNK_SIZE = 1
COMPLEX_IMAG_CHAR_SCHEME = 'i'
COMPLEX_IMAG_CHAR_PYTHON = 'j'
FILE_WRITE_MODE = 'w'
