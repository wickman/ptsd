from __future__ import print_function

import os

from .parser import Parser


class Loader(object):
  def __init__(self, filename):
    self.root = filename
    self.thrifts = {}
    self.parser = Parser()
    self.process(self.root)
    self.check()

  def process(self, root):
    real_root = os.path.realpath(root)

    if real_root in self.thrifts:
      return

    print('Processing %s' % real_root)

    with open(real_root) as fp:
      parent = self.thrifts[real_root] = self.parser.parse(fp.read())

    for include in parent.includes:
      real_path = os.path.join(os.path.dirname(real_root), include.path.value)
      self.process(real_path)

  def check(self):
    modules = [os.path.basename(fn) for fn in self.thrifts]
    if len(modules) != len(set(modules)):
      print('warning: ambiguous modules.')

  def dump(self):
    for filename, thrift in self.thrifts.items():
      print('Dumping %s\n' % filename)
      print('%s\n\n' % thrift)
