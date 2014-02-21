import sys

from ptsd import ast
from ptsd.loader import Loader


def transform_enum(enum):
  name = enum.name.value

  return '%s = Enum(%r, %r)' % (
     name,
     name,
     tuple(value.name.value for value in enum.values))


def transform_type(field_type):
  if isinstance(field_type, (ast.Byte, ast.I16, ast.I32, ast.I64)):
    return 'Integer'
  elif isinstance(field_type, ast.Double):
    return 'Float'
  elif isinstance(field_type, ast.Bool):
    return 'Boolean'
  # ast.Binary != String unfortunately
  elif isinstance(field_type, (ast.Binary, ast.String)):
    return 'String'
  elif isinstance(field_type, ast.Identifier):
    return field_type.value
  elif isinstance(field_type, ast.Map):
    return 'Map(%s, %s)' % (
        transform_type(field_type.key_type), transform_type(field_type.value_type))
  elif isinstance(field_type, ast.List):
    return 'List(%s)' % transform_type(field_type.value_type)
  elif isinstance(field_type, ast.Set):
    # TODO(wickman) Support pystachio set?
    return 'List(%s)' % transform_type(field_type.value_type)
  raise ValueError('Unsupported conversion type: %s (base:%s)' % (field_type, type(field_type)))


def transform_field(field, indent=0):
  line = ' ' * indent
  line += '%s = ' % field.name.value
  if not field.required and not field.const_value:
    line += transform_type(field.type)
  elif field.required and not field.const_value:
    line += 'Required(%s)' % transform_type(field.type)
  elif not field.required and field.const_value:
    line += 'Default(%s, %s)' % (
        transform_type(field.type), ast.Const.render_value(field.const_value))
  else:
    raise ValueError('Cannot have required field with default values.')
  return line



def transform_struct(struct):
  lines = []
  lines += ['class %s(Struct):' % struct.name.value]
  for field in struct.fields:
    lines.append(transform_field(field, indent=2))
  if len(struct.fields) == 0:
    lines.append('  pass')
  return '\n'.join(lines)


def transform(module):
  for node in module.values():
    print('\n')
    if not isinstance(node, ast.Node):
      continue
    if isinstance(node, ast.Enum):
      print transform_enum(node)
    elif isinstance(node, ast.Struct):
      print transform_struct(node)
    # TODO(constants)
    # TODO(typedefs)


def main(thrift_idl):
  loader = Loader(thrift_idl)

  for module in loader.modules.values():
    transform(module)


main(sys.argv[1])
