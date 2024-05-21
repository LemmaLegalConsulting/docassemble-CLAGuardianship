import os
import sys
from setuptools import setup, find_packages
from fnmatch import fnmatchcase
from distutils.util import convert_path

standard_exclude = ('*.pyc', '*~', '.*', '*.bak', '*.swp*')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build', './dist', 'EGG-INFO', '*.egg-info')

__all__ = ['filter_letters']

def find_package_data(where='.', package='', exclude=standard_exclude, exclude_directories=standard_exclude_directories):
    out = {}
    stack = [(convert_path(where), '', package)]
    while stack:
        where, prefix, package = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                if os.path.isfile(os.path.join(fn, '__init__.py')):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + '.' + name
                        stack.append((fn, '', new_package))
                else:
                    stack.append((fn, prefix + name + '/', package))
            else:
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix+name)
    return out

def filter_letters(letter_strings):
  """Used to take a list of letters like ["A","ABC","AB"] and filter out any duplicate letters."""
  # There is probably a cute one liner, but this is easy to follow and
  # probably same speed
  unique_letters = set()
  if isinstance(letter_strings, str):
    letter_strings = [letter_strings]
  for string in letter_strings:
    if string: # Catch possible None values
      for letter in string:
        unique_letters.add(letter)
  try:
    retval = ''.join(sorted(unique_letters))
  except:
    retval = ''
  return retval

setup(name='docassemble.CLAGuardianship',
      version='1.1.1',
      description=('CLA Guardianship Interviews'),
      long_description='# docassemble.CLAGuardianship\n\n## Author\n\nCourt Forms Online\n\n',
      long_description_content_type='text/markdown',
      author='Court Forms Online',
      author_email='',
      license='The MIT License',
      url='https://courtformsonline.org',
      packages=find_packages(),
      namespace_packages=['docassemble'],
      install_requires=['docassemble.AssemblyLine'],
      zip_safe=False,
      package_data=find_package_data(where='docassemble/CLAGuardianship/', package='docassemble.CLAGuardianship'),
     )
