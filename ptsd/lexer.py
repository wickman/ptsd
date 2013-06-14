from . import constants

import ply.lex as lex


__all__ = ('Lexer,')


class Lexer(object):
  class Error(Exception): pass

  RESERVED = constants.BOOL + constants.NAMESPACES + constants.TYPES + constants.ACTIONS
  RESERVED_DISALLOW = constants.DISALLOW

  literals = [':', ';', ',', '{', '}', '(', ')', '=', '<', '>', '[', ']']
  tokens = (
      'DUBCONSTANT',
      'INTCONSTANT',
      'HEXCONSTANT',
      'IDENTIFIER',
      'SILLYCOMM',
      'MULTICOMM',
      'DOCTEXT',
      'COMMENT',
      'UNIXCOMMENT',
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
  t_LITERAL = r'\"([^\\\n]|(\\.))*?\"'

  def t_newline(self, t):
    r'\n+'
    t.lexer.lineno += len(t.value)

  def t_HEXCONSTANT(self, t):
    r'"0x"[0-9A-Fa-f]+'
    t.value = int(t.value, 16)
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
    else:
      t.type = 'IDENTIFIER'
    return t

  def t_error(self, t):
    raise self.Error('Failed to lex: %s' % t)

  def build(self, **kwargs):
    return lex.lex(module=self, **kwargs)
