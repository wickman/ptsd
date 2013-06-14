from setuptools import setup, find_packages

version = '0.0.0'


setup(
  name                 = 'ptsd',
  version              = version,
  description          = 'python thrift simple/dumb',
  url                  = 'http://github.com/wickman/ptsd',
  author               = 'Brian Wickman',
  author_email         = 'wickman@gmail.com',
  packages             = find_packages(),
  py_modules           = ['ptsd'],
  zip_safe             = True,
  install_requires     = ['ply'],
  scripts              = ['bin/ptsd'],
)
