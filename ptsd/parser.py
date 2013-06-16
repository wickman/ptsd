from .ast import (
    TypeAnnotation,

    # Container types
    Set,
    Map,
    List,

    # Basic types
    String,
    Binary,
    Slist,
    Bool,
    Byte,
    I16,
    I32,
    I64,
    Double,

    # Everything else
    Field,
    Function,
    Identifier,
    Service,
    Exception_,
    Struct,
    Const,
    Senum,
    Enum,
    EnumDef,
    Typedef,
    Include,
    Namespace,
    Thrift
)
from .lexer import (
    Lexer,
    Identifier as LexerIdentifier
)

import ply.yacc as yacc


class Parser(object):
  class Error(Exception): pass

  tokens = Lexer.tokens
  start = 'thrift'

  BASIC_TYPES = {
    'binary': Binary,
    'bool': Bool,
    'byte': Byte,
    'double': Double,
    'i16': I16,
    'i32': I32,
    'i64': I64,
    'slist': Slist,
    'string': String,
  }

  @classmethod
  def default_action(cls, p, name=None):
    p[0] = ' '.join(map(str, filter(None, p[1:])))
    if name:
      p[0] = '%s(%s)' % (name, p[0])

  @classmethod
  def default_list_action(cls, p):
    if len(p) == 3:
      p[0] = (p[1] if p[1] else []) + [p[2]]
    else:
      p[0] = []

  def p_empty(self, p):
    '''empty : '''
    pass

  def p_thrift(self, p):
    '''thrift : header_list definition_list'''
    p[0] = Thrift(p)

  def p_header_list(self, p):
    '''header_list : header_list header
                   | empty'''
    self.default_list_action(p)

  def p_header(self, p):
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
    if len(p) == 2:
      p[0] = p[1]
    else:
      p[0] = Namespace(p)

  def p_include(self, p):
    '''include : INCLUDE LITERAL'''
    p[0] = Include(p)

  def p_definition_list(self, p):
    '''definition_list : definition_list definition
                       | empty'''
    self.default_list_action(p)

  def p_definition(self, p):
    '''definition : const
                  | type_definition
                  | service'''
    p[0] = p[1]

  def p_type_definition(self, p):
    '''type_definition : typedef
                       | enum
                       | senum
                       | struct
                       | exception'''
    p[0] = p[1]

  def p_typedef(self, p):
    '''typedef : TYPEDEF field_type IDENTIFIER type_annotations'''
    p[0] = Typedef(p)

  def p_comma_or_semicolon_optional(self, p):
    '''comma_or_semicolon_optional : ','
                                   | ';'
                                   | empty'''
    self.default_action(p)

  def p_start_enum_counter(self, p):
    '''start_enum_counter : empty'''
    self._enum_counter = -1

  def p_enum(self, p):
    '''enum : ENUM IDENTIFIER start_enum_counter '{' enum_def_list '}' type_annotations'''
    p[0] = Enum(p)

  def p_enum_def_list(self, p):
    '''enum_def_list : enum_def_list enum_def
                     | empty'''
    self.default_list_action(p)

  def p_enum_def(self, p):
    '''enum_def : IDENTIFIER '=' INTCONSTANT type_annotations comma_or_semicolon_optional
                | IDENTIFIER type_annotations comma_or_semicolon_optional'''
    if p[2] == '=':
      self._enum_counter = p[3]
    else:
      self._enum_counter += 1
    p[0] = EnumDef(p, self._enum_counter)

  def p_senum(self, p):
    '''senum : SENUM IDENTIFIER '{' senum_def_list '}' type_annotations'''
    p[0] = Senum(p)

  def p_senum_def_list(self, p):
    '''senum_def_list : senum_def
                      | empty'''
    self.default_list_action(p)

  def p_senum_def(self, p):
    '''senum_def : LITERAL comma_or_semicolon_optional'''
    p[0] = p[1]

  def p_const(self, p):
    '''const : CONST field_type IDENTIFIER '=' const_value comma_or_semicolon_optional'''
    p[0] = Const(p)

  def p_const_value(self, p):
    '''const_value : INTCONSTANT
                   | DUBCONSTANT
                   | LITERAL
                   | IDENTIFIER
                   | const_list
                   | const_map'''
    if isinstance(p[1], LexerIdentifier):
      p[1] = Identifier(p, 1)
    p[0] = p[1]

  def p_const_list(self, p):
    """const_list : '[' const_list_contents ']'"""
    p[0] = p[2]

  def p_const_list_contents(self, p):
    '''const_list_contents : const_list_contents const_value comma_or_semicolon_optional
                           | empty'''
    p[0] = p[1] or []
    if len(p) > 2:
      p[0].append(p[2])

  def p_const_map(self, p):
    """const_map : '{' const_map_contents '}'"""
    p[0] = p[2]

  def p_const_map_contents(self, p):
    '''const_map_contents : const_map_contents const_value ':' const_value comma_or_semicolon_optional
                          | empty'''
    # TODO(wickman) if this implies hashable lists/maps we should probably store lists as tuples
    # and maps as a tuple of tuples.
    p[0] = p[1] or {}
    if len(p) > 4:
      p[0][p[2]] = p[4]

  def p_struct_head(self, p):
    '''struct_head : STRUCT
                   | UNION'''
    p[0] = p[1]

  def p_struct(self, p):
    '''struct : struct_head IDENTIFIER xsd_all '{' field_list '}' type_annotations'''
    p[0] = Struct(p)

  def p_xsd_all(self, p):
    '''xsd_all : XSD_ALL
               | empty'''
    p[0] = p[1] == 'xsd_all'

  def p_xsd_optional(self, p):
    '''xsd_optional : XSD_OPTIONAL
                    | empty'''
    p[0] = p[1] == 'xsd_optional'

  def p_xsd_nillable(self, p):
    '''xsd_nillable : XSD_NILLABLE
                    | empty'''
    p[0] = p[1] == 'xsd_nillable'

  def p_xsd_attributes(self, p):
    '''xsd_attributes : XSD_ATTRS '{' field_list '}'
                      | empty'''
    p[0] = p[3] if p[1] else []

  def p_exception(self, p):
    '''exception : EXCEPTION IDENTIFIER '{' field_list '}' type_annotations'''
    p[0] = Exception_(p)

  def p_service(self, p):
    '''service : SERVICE IDENTIFIER extends '{' flag_args function_list unflag_args '}' type_annotations'''
    p[0] = Service(p)

  def p_flag_args(self, p):
    '''flag_args : empty'''
    pass

  def p_unflag_args(self, p):
    '''unflag_args : empty'''
    pass

  def p_extends(self, p):
    '''extends : EXTENDS IDENTIFIER
               | empty'''
    p[0] = p[2] if p[1] else None

  def p_function_list(self, p):
    '''function_list : function_list function
                     | empty'''
    self.default_list_action(p)

  def p_function(self, p):
    '''function : oneway function_type IDENTIFIER '(' field_list ')' throws type_annotations comma_or_semicolon_optional'''
    p[0] = Function(p)

  def p_oneway(self, p):
    '''oneway : ONEWAY
              | empty'''
    p[0] = p[1] == 'oneway'

  def p_throws(self, p):
    '''throws : THROWS '(' field_list ')'
              | empty'''
    p[0] = p[3] if p[1] else []

  def p_field_list(self, p):
    '''field_list : field_list field
                  | empty'''
    self.default_list_action(p)

  def p_field(self, p):
    '''field : field_identifier field_requiredness field_type IDENTIFIER field_value xsd_optional xsd_nillable xsd_attributes type_annotations comma_or_semicolon_optional'''
    p[0] = Field(p)

  def p_field_identifier(self, p):
    '''field_identifier : INTCONSTANT ':'
                        | empty'''
    p[0] = p[1]

  def p_field_requiredness(self, p):
    '''field_requiredness : REQUIRED
                          | OPTIONAL
                          | empty'''
    p[0] = p[1] == 'required'

  def p_field_value(self, p):
    '''field_value : '=' const_value
                   | empty'''
    p[0] = p[2] if p[1] else None

  def p_function_type(self, p):
    '''function_type : field_type
                     | VOID'''
    p[0] = p[1]

  def p_field_type(self, p):
    '''field_type : IDENTIFIER
                  | base_type
                  | container_type'''
    if isinstance(p[1], LexerIdentifier):
      p[1] = Identifier(p, 1)
    p[0] = p[1]

  def p_base_type(self, p):
    '''base_type : simple_base_type type_annotations'''
    p[0] = p[1]
    p[0].add_annotations(p[2])

  def p_simple_base_type(self, p):
    '''simple_base_type : STRING
                        | BINARY
                        | SLIST
                        | BOOL
                        | BYTE
                        | I16
                        | I32
                        | I64
                        | DOUBLE'''
    p[0] = self.BASIC_TYPES[p[1]](p)

  def p_container_type(self, p):
    '''container_type : simple_container_type type_annotations'''
    p[0] = p[1]
    p[0].add_annotations(p[2])

  def p_simple_container_type(self, p):
    '''simple_container_type : map_type
                             | set_type
                             | list_type'''
    p[0] = p[1]

  def p_map_type(self, p):
    """map_type : MAP cpp_type '<' field_type ',' field_type '>'"""
    p[0] = Map(p)

  def p_set_type(self, p):
    """set_type : SET cpp_type '<' field_type '>'"""
    p[0] = Set(p)

  def p_list_type(self, p):
    """list_type : LIST '<' field_type '>' cpp_type"""
    p[0] = List(p)

  def p_cpp_type(self, p):
    '''cpp_type : CPP_TYPE LITERAL
                | empty'''
    p[0] = p[2] if p[1] else None

  def p_type_annotations(self, p):
    '''type_annotations : '(' type_annotation_list ')'
                        | empty'''
    p[0] = p[2] if p[1] else []

  def p_type_annotation_list(self, p):
    '''type_annotation_list : type_annotation_list type_annotation
                            | empty'''
    self.default_list_action(p)

  def p_type_annotation(self, p):
    '''type_annotation : IDENTIFIER '=' LITERAL comma_or_semicolon_optional'''
    p[0] = TypeAnnotation(p)

  def p_error(self, p):
    raise self.Error('Parse error: %s' % p)

  def __init__(self):
    self._lex = Lexer().build()
    self._yacc = yacc.yacc(module=self, write_tables=False, debug=False)

  def parse(self, data):
    return self._yacc.parse(data, lexer=self._lex, tracking=True)
