class Node(object):
  def __init__(self, parser):
    self._linespan = parser.linespan(0)
    self._lexspan = parser.lexspan(0)
    super(Node, self).__init__()


class Program(Node):
  def __init__(self, parser):
    self.headers = parser[1]
    self.body = parser[2]


class LanguageDirective(Node):
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
      self.language_id = parser[2]
      self.name = parser[3]
    else:
      self.language_id = parser[1]
      self.name = parser[2]
    super(LanguageDirective, self).__init__(parser)


class Include(Node):
  def __init__(self, parser):
    '''include : INCLUDE LITERAL'''
    self.path = parser[2]
    super(Include, self).__init__(parser)


class Typedef(Node):
  def __init__(self, parser):
    '''typedef : TYPEDEF field_type IDENTIFIER type_annotations'''
    self.type = parser[2]
    self.name = parser[3]
    self.annotations = parser[4]
    super(Typedef, self).__init__(parser)


class Enum(Node):
  def __init__(self, parser):
    '''enum : ENUM IDENTIFIER '{' enum_def_list '}' type_annotations'''
    self.name = parser[2]
    self.values = parser[4]
    self.annotations = parser[6]
    super(Enum, self).__init__(parser)


class EnumDef(Node):
  def __init__(self, parser):
    '''enum_def : IDENTIFIER '=' INTCONSTANT type_annotations comma_or_semicolon_optional
                | IDENTIFIER type_annotations comma_or_semicolon_optional'''
    self.name = parser[1]
    if parser[2] == '=':
      self.tag = parser[3]
      self.annotations = parser[4]
    else:
      self.annotations = parser[2]
    super(EnumDef, self).__init__(parser)


class Senum(Node):
  def __init__(self, parser):
    '''senum : SENUM IDENTIFIER '{' senum_def_list '}' type_annotations'''
    self.name = parser[2]
    self.values = parser[4]
    self.annotations = parser[6]
    super(Senum, self).__init__(parser)


class Const(Node):
  def __init__(self, parser):
    '''const : CONST field_type IDENTIFIER '=' const_value comma_or_semicolon_optional'''
    self.type = parser[2]
    self.name = parser[3]
    self.value = parser[5]
    super(Const, self).__init__(parser)


class Struct(Node):
  def __init__(self, parser):
    '''struct : struct_head IDENTIFIER xsd_all '{' field_list '}' type_annotations'''
    self.union = parser[1] == 'union'
    self.name = parser[2]
    self.xsd_all = parser[3]
    self.fields = parser[5]
    self.annotations = parser[7]
    super(Struct, self).__init__(parser)


class Exception_(Node):
  def __init__(self, parser):
    '''exception : EXCEPTION IDENTIFIER '{' field_list '}' type_annotations'''
    self.name = parser[2]
    self.fields = parser[4]
    self.annotations = parser[6]
    super(Exception_, self).__init__(parser)


class Service(Node):
  def __init__(self, parser):
    '''service : SERVICE IDENTIFIER extends '{' flag_args function_list unflag_args '}' type_annotations'''
    self.name = parser[2]
    self.extends = parser[3]
    self.functions = parser[6]
    self.annotations = parser[9]
    super(Service, self).__init__(parser)


class Function(Node):
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
    self.oneway = parser[1]
    self.type = parser[2]
    self.name = parser[3]
    self.arguments = parser[5]
    self.throws = parser[7]
    self.annotations = parser[8]
    super(Function, self).__init__(parser)


class Field(Node):
  def __init__(self, parser):
    '''field : field_identifier field_requiredness field_type IDENTIFIER field_value xsd_optional
               xsd_nillable xsd_attributes type_annotations comma_or_semicolon_optional'''
    self.identifier = parser[1]
    self.required = parser[2]
    self.type = parser[3]
    self.name = parser[4]
    self.xsd_optional = parser[5]
    self.xsd_nillable = parser[6]
    self.xsd_attributes = parser[7]
    self.annotations = parser[8]
    super(Field, self).__init__(parser)


class Type(object):
  def __init__(self, annotations=None):
    self.annotations = annotations or []
    super(Type, self).__init__()

  def add_annotations(self, annotations=None):
    self.annotations.extend(annotations or [])

  def __str__(self):
    return self.__class__.__name__.lower()


class TypeAnnotation(Node):
  def __init__(self, parser):
    """type_annotation : IDENTIFIER '=' LITERAL comma_or_semicolon_optional"""
    self.name = parser[1]
    self.value = parser[3]
    super(TypeAnnotation, self).__init__(parser)


# Base types
class String(Node, Type):
  def __init__(self, parser):
    super(String, self).__init__(parser)


class Binary(Node, Type):
  def __init__(self, parser):
    super(Binary, self).__init__(parser)


class Slist(Node, Type):
  def __init__(self, parser):
    super(Slist, self).__init__(parser)


class Bool(Node, Type):
  def __init__(self, parser):
    super(Bool, self).__init__(parser)


class Byte(Node, Type):
  def __init__(self, parser):
    super(Byte, self).__init__(parser)


class I16(Node, Type):
  def __init__(self, parser):
    super(I16, self).__init__(parser)


class I32(Node, Type):
  def __init__(self, parser):
    super(I32, self).__init__(parser)


class I64(Node, Type):
  def __init__(self, parser):
    super(I64, self).__init__(parser)


class Double(Node, Type):
  def __init__(self, parser):
    super(Double, self).__init__(parser)


# Container types
class Map(Node, Type):
  def __init__(self, parser):
    """MAP cpp_type '<' field_type ',' field_type '>'"""
    self.cpp_type = parser[2]
    self.key_type = parser[4]
    self.value_type = parser[6]
    super(Map, self).__init__(parser)

  def __str__(self):
    return 'map<%s,%s>' % (self.key_type, self.value_type)


class Set(Node, Type):
  def __init__(self, parser):
    """SET cpp_type '<' field_type '>'"""
    self.cpp_type = parser[2]
    self.value_type = parser[4]
    super(Set, self).__init__(parser)

  def __str__(self):
    return 'set<%s>' % (self.value_type)


class List(Node, Type):
  def __init__(self, parser):
    """LIST '<' field_type '>'"""
    self.value_type = parser[3]
    super(List, self).__init__(parser)

  def __str__(self):
    return 'list<%s>' % (self.value_type)
