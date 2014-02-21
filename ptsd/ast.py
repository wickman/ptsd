import itertools

from .lexer import (
    Literal,
    Identifier as LexerIdentifier
)


TAB_SPACES = 2
def untab(s):
  return s.replace('\t', ' '*TAB_SPACES)


class Node(object):
  def __init__(self, parser, offset=0):
    self._linespan = parser.linespan(offset)
    self._lexspan = parser.lexspan(offset)
    super(Node, self).__init__()

  def _walk(self):
    return []

  def walk(self):
    for child in self._walk():
      yield (self, child)
      for pair in child.walk():
        yield pair


class Identifier(Node):
  def __init__(self, parser, offset):
    assert isinstance(parser[offset], LexerIdentifier)
    self.value = parser[offset].value
    super(Identifier, self).__init__(parser, offset)

  def __str__(self):
    return self.value


class Thrift(Node):
  def __init__(self, parser):
    self.includes = [k for k in parser[1] if isinstance(k, Include)]
    self.namespaces = [k for k in parser[1] if isinstance(k, Namespace)]
    self.body = parser[2]

  def _walk(self):
    return itertools.chain(self.includes, self.namespaces, self.body)

  def __str__(self):
    return '%s%s%s%s%s' % (
        '\n'.join(map(str, self.includes)),
        '\n\n' if self.includes else '',
        '\n'.join(map(str, self.namespaces)),
        '\n\n' if self.namespaces else '',
        '\n\n'.join(map(str, self.body)))



class Namespace(Node):
  def __init__(self, parser):
    '''header : include
              | NAMESPACE IDENTIFIER IDENTIFIER
              | NAMESPACE '*' IDENTIFIER
              | CPP_NAMESPACE IDENTIFIER
              | CPP_INCLUDE LITERAL
              | PHP_NAMESPACE IDENTIFIER
              | PY_MODULE IDENTIFIER
              | PERL_PACKAGE IDENTIFIER
              | RUBY_NAMESPACE IDENTIFIER
              | SMALLTALK_CATEGORY ST_IDENTIFIER
              | SMALLTALK_PREFIX IDENTIFIER
              | JAVA_PACKAGE IDENTIFIER
              | COCOA_PREFIX IDENTIFIER
              | XSD_NAMESPACE LITERAL
              | CSHARP_NAMESPACE IDENTIFIER
              | DELPHI_NAMESPACE IDENTIFIER'''
    if parser[1] == 'namespace':
      self.old_style = False
      self.language_id = parser[2].value if isinstance(parser[2], LexerIdentifier) else parser[2]
      self.name = Identifier(parser, 3)
    else:
      self.old_style = True
      self.language_id = parser[1]
      self.name = Identifier(parser, 2) if isinstance(parser[1], LexerIdentifier) else parser[2]
    super(Namespace, self).__init__(parser)

  def __str__(self):
    return '%s%s %s' % ('' if self.old_style else 'namespace ', self.language_id, self.name)


class Include(Node):
  def __init__(self, parser):
    '''include : INCLUDE LITERAL'''
    self.path = parser[2]
    super(Include, self).__init__(parser)

  def __str__(self):
    return 'include %s' % self.path


class Annotated(object):
  def __init__(self):
    self.annotations = []
    super(Annotated, self).__init__()

  def add_annotations(self, annotations=None):
    self.annotations.extend(annotations or [])

  def annotations_str(self):
    return ' %s' % ' '.join(map(str, self.annotations)) if self.annotations else ''


class Typedef(Node, Annotated):
  def __init__(self, parser):
    '''typedef : TYPEDEF field_type IDENTIFIER type_annotations'''
    super(Typedef, self).__init__(parser)
    self.type = parser[2]
    self.name = Identifier(parser, 3)
    self.add_annotations(parser[4])

  def __str__(self):
    return 'typedef %s %s%s' % (
      self.type,
      self.name,
      self.annotations_str()
    )


class Enum(Node, Annotated):
  def __init__(self, parser):
    '''enum : ENUM IDENTIFIER start_enum_counter '{' enum_def_list '}' type_annotations'''
    super(Enum, self).__init__(parser)
    self.name = Identifier(parser, 2)
    self.values = parser[5]
    self.add_annotations(parser[7])

  def _walk(self):
    return itertools.chain(self.values, self.annotations)

  def __str__(self):
    return untab('enum %s {\n\t%s\n}%s' % (
        self.name,
        '\n\t'.join(map(str, self.values)),
        self.annotations_str()))


class EnumDef(Node, Annotated):
  def __init__(self, parser, tag_number):
    '''enum_def : IDENTIFIER '=' INTCONSTANT type_annotations comma_or_semicolon_optional
                | IDENTIFIER type_annotations comma_or_semicolon_optional'''
    super(EnumDef, self).__init__(parser)
    self.name = Identifier(parser, 1)
    self.tag = tag_number
    self.add_annotations(parser[4] if parser[2] == '=' else parser[2])

  def __str__(self):
    return '%s = %s%s' % (self.name, self.tag, self.annotations_str())


class Senum(Node, Annotated):
  def __init__(self, parser):
    '''senum : SENUM IDENTIFIER '{' senum_def_list '}' type_annotations'''
    super(Senum, self).__init__(parser)
    self.name = Identifier(parser, 2)
    self.values = parser[4]
    self.add_annotations(parser[6])


class Const(Node):
  @classmethod
  def render_value(cls, value, indent=0):
    if isinstance(value, list):
      return '[%s]' % ', '.join(map(cls.render_value, value))
    elif isinstance(value, dict):
      return '{%s}' % ', '.join('%s: %s' % (cls.render_value(k), cls.render_value(v)) for k, v in value.items())
    else:
      return str(value)

  def __init__(self, parser):
    '''const : CONST field_type IDENTIFIER '=' const_value comma_or_semicolon_optional'''
    super(Const, self).__init__(parser)
    self.type = parser[2]
    self.name = Identifier(parser, 3)
    self.value = parser[5]

  def __str__(self):
    return untab('const %s %s = %s' % (
        self.type,
        self.name,
        self.render_value(self.value)))


class Struct(Node, Annotated):
  def __init__(self, parser):
    '''struct : struct_head IDENTIFIER xsd_all '{' field_list '}' type_annotations'''
    super(Struct, self).__init__(parser)
    self.union = parser[1] == 'union'
    self.name = Identifier(parser, 2)
    self.xsd_all = parser[3]
    self.fields = parser[5]
    self.add_annotations(parser[7])

  def _walk(self):
    return itertools.chain(self.fields, self.annotations)

  def __str__(self):
    return untab('%s %s {\n\t%s\n}%s' % (
        'union' if self.union else 'struct',
        self.name,
        '\n\t'.join(map(str, self.fields)),
        self.annotations_str()))


class Exception_(Node, Annotated):
  def __init__(self, parser):
    '''exception : EXCEPTION IDENTIFIER '{' field_list '}' type_annotations'''
    super(Exception_, self).__init__(parser)
    self.name = Identifier(parser, 2)
    self.fields = parser[4]
    self.add_annotations(parser[6])

  def _walk(self):
    return itertools.chain(self.fields, self.annotations)

  def __str__(self):
    return untab('exception %s {\n\t%s\n}%s' % (
        self.name,
        '\n\t'.join(map(str, self.fields)),
        self.annotations_str()))


class Service(Node, Annotated):
  def __init__(self, parser):
    '''service : SERVICE IDENTIFIER extends '{' flag_args function_list unflag_args '}' type_annotations'''
    super(Service, self).__init__(parser)
    self.name = Identifier(parser, 2)
    self.extends = parser[3]
    self.functions = parser[6]
    self.add_annotations(parser[9])

  def _walk(self):
    return itertools.chain(self.functions, self.annotations)

  def __str__(self):
    return untab('service %s%s {\n\t%s\n}%s' % (
        self.name,
        ' extends %s' % self.extends if self.extends else '',
        '\n\t'.join(map(str, self.functions)),
        self.annotations_str()))


class Function(Node, Annotated):
  def __init__(self, parser):
    '''function : oneway
                  function_type
                  IDENTIFIER
                  '('
                  field_list
                  ')'
                  throws
                  type_annotations
                  comma_or_semicolon_optional'''
    super(Function, self).__init__(parser)
    self.oneway = parser[1]
    self.type = parser[2]
    self.name = Identifier(parser, 3)
    self.arguments = parser[5]
    self.throws = parser[7]
    self.add_annotations(parser[8])

  def _walk(self):
    return itertools.chain(self.arguments, self.annotations)

  def __str__(self):
    return '%s%s %s(%s)%s%s' % (
        'oneway ' if self.oneway else '',
        self.type,
        self.name,
        ', '.join(map(str, self.arguments)),
        (' throws (%s)' % ' '.join(map(str, self.throws))) if self.throws else '',
        self.annotations_str())


class Field(Node, Annotated):
  def __init__(self, parser):
    '''field : field_identifier field_requiredness field_type IDENTIFIER field_value xsd_optional
               xsd_nillable xsd_attributes type_annotations comma_or_semicolon_optional'''
    super(Field, self).__init__(parser)
    self.tag = parser[1]
    self.required = parser[2]
    self.type = parser[3]
    self.name = Identifier(parser, 4)
    self.const_value = parser[5]
    self.xsd_optional = parser[6]
    self.xsd_nillable = parser[7]
    self.xsd_attributes = parser[8]
    self.add_annotations(parser[9])

  def _walk(self):
    return self.annotations

  def __str__(self):
    return '%d: %s%s %s%s%s' % (
        self.tag,
        'required ' if self.required else '',
        self.type,
        self.name,
        ' = %s ' % Const.render_value(self.const_value) if self.const_value else '',
        self.annotations_str())


class TypeAnnotation(Node):
  def __init__(self, parser):
    """type_annotation : IDENTIFIER '=' LITERAL comma_or_semicolon_optional"""
    super(TypeAnnotation, self).__init__(parser)
    self.name = Identifier(parser, 1)
    self.value = parser[3]

  def __str__(self):
    return '%s=%s' % (self.name, self.value)


# Base types
class BaseType(object):
  def __str__(self):
    return self.__class__.__name__.lower()


class String(Node, Annotated, BaseType):
  def __init__(self, parser):
    super(String, self).__init__(parser)


class Binary(Node, Annotated, BaseType):
  def __init__(self, parser):
    super(Binary, self).__init__(parser)


class Slist(Node, Annotated, BaseType):
  def __init__(self, parser):
    super(Slist, self).__init__(parser)


class Bool(Node, Annotated, BaseType):
  def __init__(self, parser):
    super(Bool, self).__init__(parser)


class Byte(Node, Annotated, BaseType):
  def __init__(self, parser):
    super(Byte, self).__init__(parser)


class I16(Node, Annotated, BaseType):
  def __init__(self, parser):
    super(I16, self).__init__(parser)


class I32(Node, Annotated, BaseType):
  def __init__(self, parser):
    super(I32, self).__init__(parser)


class I64(Node, Annotated, BaseType):
  def __init__(self, parser):
    super(I64, self).__init__(parser)


class Double(Node, Annotated, BaseType):
  def __init__(self, parser):
    super(Double, self).__init__(parser)


# Container types
class Map(Node, Annotated):
  def __init__(self, parser):
    """MAP cpp_type '<' field_type ',' field_type '>'"""
    self.cpp_type = parser[2]
    self.key_type = parser[4]
    self.value_type = parser[6]
    super(Map, self).__init__(parser)

  def __str__(self):
    return 'map<%s, %s>' % (self.key_type, self.value_type)


class Set(Node, Annotated):
  def __init__(self, parser):
    """SET cpp_type '<' field_type '>'"""
    self.cpp_type = parser[2]
    self.value_type = parser[4]
    super(Set, self).__init__(parser)

  def __str__(self):
    return 'set<%s>' % (self.value_type)


class List(Node, Annotated):
  def __init__(self, parser):
    """LIST '<' field_type '>'"""
    self.value_type = parser[3]
    super(List, self).__init__(parser)

  def __str__(self):
    return 'list<%s>' % (self.value_type)
