import pprint
import time

from .lexer import Lexer

import ply.yacc as yacc


class Parser(object):
  class Error(Exception): pass

  tokens = Lexer.tokens
  start = 'program'

  @classmethod
  def default_action(cls, p, name=None):
    p[0] = ' '.join(map(str, filter(None, p[1:])))
    if name:
      p[0] = '%s(%s)' % (name, p[0])

  @classmethod
  def default_list_action(cls, p):
    if len(p) == 3:
      p[0] = (p[1] if p[1] else []) + [p[2]]

  def p_empty(self, p):
    '''empty : '''
    pass

  def p_program(self, p):
    '''program : header_list definition_list'''
    p[0] = (p[1], p[2])

  def p_capture_doc_text(self, p):
    '''capture_doc_text : empty'''
    pass

  def p_destroy_doc_text(self, p):
    '''destroy_doc_text : empty'''
    pass

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
    self.default_action(p, 'header')

  def p_include(self, p):
    '''include : INCLUDE LITERAL'''
    self.default_action(p, 'include')

  def p_definition_list(self, p):
    '''definition_list : definition_list definition
                       | empty'''
    self.default_list_action(p)

  def p_definition(self, p):
    '''definition : const
                  | type_definition
                  | service'''
    self.default_action(p, 'definition')

  def p_type_definition(self, p):
    '''type_definition : typedef
                       | enum
                       | senum
                       | struct
                       | exception'''
    self.default_action(p, 'type_definition')

  def p_typedef(self, p):
    '''typedef : TYPEDEF field_type IDENTIFIER type_annotations'''
    self.default_action(p)

  def p_comma_or_semicolon_optional(self, p):
    '''comma_or_semicolon_optional : ','
                                   | ';'
                                   | empty'''
    self.default_action(p)

  def p_enum(self, p):
    '''enum : ENUM IDENTIFIER '{' enum_def_list '}' type_annotations'''
    self.default_action(p)

  def p_enum_def_list(self, p):
    '''enum_def_list : enum_def_list enum_def
                     | empty'''
    self.default_list_action(p)

  def p_enum_def(self, p):
    '''enum_def : capture_doc_text IDENTIFIER '=' INTCONSTANT type_annotations comma_or_semicolon_optional
                | capture_doc_text IDENTIFIER type_annotations comma_or_semicolon_optional'''
    self.default_action(p, 'enum_def')

  def p_senum(self, p):
    '''senum : SENUM IDENTIFIER '{' senum_def_list '}' type_annotations'''
    self.default_action(p, 'senum')

  def p_senum_def_list(self, p):
    '''senum_def_list : senum_def
                      | empty'''
    self.default_list_action(p)

  def p_senum_def(self, p):
    '''senum_def : LITERAL comma_or_semicolon_optional'''
    self.default_action(p, 'senum_def')

  def p_const(self, p):
    '''const : CONST field_type IDENTIFIER '=' const_value comma_or_semicolon_optional'''
    self.default_action(p)

  def p_const_value(self, p):
    '''const_value : INTCONSTANT
                   | DUBCONSTANT
                   | LITERAL
                   | IDENTIFIER
                   | const_list
                   | const_map'''
    self.default_action(p)

  def p_const_list(self, p):
    """const_list : '[' const_list_contents ']'"""
    self.default_action(p)

  def p_const_list_contents(self, p):
    '''const_list_contents : const_list_contents const_value comma_or_semicolon_optional
                           | empty'''
    if len(p) == 4:
      p[0] = (p[1] if p[1] else []) + [p[2]]

  def p_const_map(self, p):
    """const_map : '{' const_map_contents '}'"""
    self.default_action(p)

  def p_const_map_contents(self, p):
    '''const_map_contents : const_map_contents const_value ':' const_value comma_or_semicolon_optional
                          | empty'''
    if len(p) == 6:
      p[0] = (p[1] if p[1] else []) + [(p[3], p[5])]

  def p_struct_head(self, p):
    '''struct_head : STRUCT
                   | UNION'''
    self.default_action(p)

  def p_struct(self, p):
    '''struct : struct_head IDENTIFIER xsd_all '{' field_list '}' type_annotations'''
    self.default_action(p)

  def p_xsd_all(self, p):
    '''xsd_all : XSD_ALL
               | empty'''
    self.default_action(p)

  def p_xsd_optional(self, p):
    '''xsd_optional : XSD_OPTIONAL
                    | empty'''
    self.default_action(p)

  def p_xsd_nillable(self, p):
    '''xsd_nillable : XSD_NILLABLE
                    | empty'''
    self.default_action(p)

  def p_xsd_attributes(self, p):
    '''xsd_attributes : XSD_ATTRS '{' field_list '}'
                      | empty'''
    self.default_action(p)

  def p_exception(self, p):
    '''exception : EXCEPTION IDENTIFIER '{' field_list '}' type_annotations'''
    self.default_action(p)

  def p_service(self, p):
    '''service : SERVICE IDENTIFIER extends '{' flag_args function_list unflag_args '}' type_annotations'''
    self.default_action(p)

  def p_flag_args(self, p):
    '''flag_args : empty'''
    pass

  def p_unflag_args(self, p):
    '''unflag_args : empty'''
    pass

  def p_extends(self, p):
    '''extends : EXTENDS IDENTIFIER
               | empty'''
    self.default_action(p)

  def p_function_list(self, p):
    '''function_list : function_list function
                     | empty'''
    self.default_list_action(p)

  def p_function(self, p):
    '''function : capture_doc_text oneway function_type IDENTIFIER '(' field_list ')' throws type_annotations comma_or_semicolon_optional'''
    self.default_action(p, 'function')

  def p_oneway(self, p):
    '''oneway : ONEWAY
              | empty'''
    self.default_action(p, 'oneway')

  def p_throws(self, p):
    '''throws : THROWS '(' field_list ')'
              | empty'''
    self.default_action(p)

  def p_field_list(self, p):
    '''field_list : field_list field
                  | empty'''
    self.default_list_action(p)

  def p_field(self, p):
    '''field : capture_doc_text field_identifier field_requiredness field_type IDENTIFIER field_value xsd_optional xsd_nillable xsd_attributes type_annotations comma_or_semicolon_optional'''
    self.default_action(p)

  def p_field_identifier(self, p):
    '''field_identifier : INTCONSTANT ':'
                        | empty'''
    self.default_action(p)

  def p_field_requiredness(self, p):
    '''field_requiredness : REQUIRED
                          | OPTIONAL
                          | empty'''
    self.default_action(p)

  def p_field_value(self, p):
    '''field_value : '=' const_value
                   | empty'''
    self.default_action(p)

  def p_function_type(self, p):
    '''function_type : field_type
                     | VOID'''
    self.default_action(p)

  def p_field_type(self, p):
    '''field_type : IDENTIFIER
                  | base_type
                  | container_type'''
    self.default_action(p)

  def p_base_type(self, p):
    '''base_type : simple_base_type type_annotations'''
    self.default_action(p)

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
    self.default_action(p)

  def p_container_type(self, p):
    '''container_type : simple_container_type type_annotations'''
    self.default_action(p)

  def p_simple_container_type(self, p):
    '''simple_container_type : map_type
                             | set_type
                             | list_type'''
    self.default_action(p)

  def p_map_type(self, p):
    """map_type : MAP cpp_type '<' field_type ',' field_type '>'"""
    self.default_action(p)

  def p_set_type(self, p):
    """set_type : SET cpp_type '<' field_type '>'"""
    self.default_action(p)

  def p_list_type(self, p):
    """list_type : LIST '<' field_type '>' cpp_type"""
    self.default_action(p)

  def p_cpp_type(self, p):
    '''cpp_type : CPP_TYPE LITERAL
                | empty'''
    self.default_action(p)

  def p_type_annotations(self, p):
    '''type_annotations : '(' type_annotation_list ')'
                        | empty'''
    self.default_action(p)

  def p_type_annotation_list(self, p):
    '''type_annotation_list : type_annotation_list type_annotation
                            | empty'''
    self.default_list_action(p)

  def p_type_annotation(self, p):
    '''type_annotation : IDENTIFIER '=' LITERAL comma_or_semicolon_optional'''
    self.default_action(p)

  def p_error(self, p):
    raise self.Error('Parse error: %s' % p)

  def __init__(self):
    self._lex = Lexer().build()
    self._yacc = yacc.yacc(module=self)

  def parse(self, data):
    return self._yacc.parse(data, lexer=self._lex)
