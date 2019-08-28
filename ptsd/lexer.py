from . import constants

import ply.lex as lex


__all__ = ('Lexer', 'Literal', 'Identifier',)


class Literal(object):
  def __init__(self, value):
    self.value = value

  def __str__(self):
    return '"%s"' % self.value


class Identifier(object):
  def __init__(self, value):
    self.value = value


class Lexer(object):
  class Error(Exception): pass

  RESERVED = constants.NAMESPACES + constants.TYPES + constants.ACTIONS
  RESERVED_DISALLOW = constants.DISALLOW

  literals = [':', ';', ',', '{', '}', '(', ')', '=', '<', '>', '[', ']', '*']
  tokens = (
      'DUBCONSTANT',
      'INTCONSTANT',
      'IDENTIFIER',
      'ST_IDENTIFIER',
      'LITERAL'
  ) + tuple(rsv.upper() for rsv in RESERVED)

  t_ignore = ' \t\r'
  t_ignore_SILLYCOMM = r'\/\*\**\*\/'
  t_ignore_MULTICOMM = r'\/\*[^*]\/*([^*/]|[^*]\/|\*[^/])*\**\*\/'
  t_ignore_DOCTEXT = r'\/\*\*([^*/]|[^*]\/|\*[^/])*\**\*\/'
  t_ignore_COMMENT = r'\/\/[^\n]*'
  t_ignore_UNIXCOMMENT = r'\#[^\n]*'

  t_ST_IDENTIFIER = r'[a-zA-Z-](\.[a-zA-Z_0-9-]|[a-zA-Z_0-9-])*'

  def t_newline(self, t):
    r'\n+'
    t.lexer.lineno += len(t.value)

  def t_LITERAL(self, t):
    r'[\"\']([^\\\n]|(\\.))*?[\"\']'
    t.value = Literal(t.value[1:-1])  # strip off ""s
    return t

  def t_HEXCONSTANT(self, t):
    r'"0x"[0-9A-Fa-f]+'
    t.value = int(t.value, 16)
    t.type = 'INTCONSTANT'
    return t

  def t_DUBCONSTANT(self, t):
    r'-?\d+\.\d*(e-?\d+)?'
    t.value = float(t.value)
    return t

  def t_INTCONSTANT(self, t):
    r'[+-]?[0-9]+'
    t.value = int(t.value)
    return t

  def t_IDENTIFIER(self, t):
    r'[a-zA-Z_](\.[a-zA-Z_0-9]|[a-zA-Z_0-9])*'
    if t.value in self.RESERVED:
      t.type = t.value.upper()
    elif t.value in self.RESERVED_DISALLOW:
      raise self.Error('Found invalid reserved word: %s' % t.value)
    elif t.value in constants.BOOL:
      t.value = 1 if t.value == "true" else 0
      t.type = 'INTCONSTANT'
    else:
      t.value = Identifier(t.value)
    return t

  def t_error(self, t):
    raise self.Error('Failed to lex: %s' % t)

  def build(self, **kwargs):
    return lex.lex(module=self, **kwargs)
