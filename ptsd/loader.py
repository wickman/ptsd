import os

from .parser import Parser


class Loader(object):
  def __init__(self, filename):
    self.root = filename
    self.thrifts = {}
    self.parser = Parser()
    self.process(self.root)

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

