# coding=utf8
'''
Tool for displaying files and directories as a tree
'''

import argparse
import sys

from . import treecat

__doc__ += f'''
version {treecat.version}
'''


def main():
  parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    description=__doc__)

  parser.add_argument('path', nargs='*')
  parser.add_argument('-s', '--summary', action='store_true')
  parser.add_argument('-L', '--max-lines', type=int)
  parser.add_argument('-W', '--max-line', type=int)
  parser.add_argument('-D', '--max-depth', type=int, default=-1)

  args = parser.parse_args()

  sys.stdout.reconfigure(encoding='utf8')

  try:
    if not args.path:
      treecat.tree('.', args)

    for path in args.path:
      treecat.tree(path, args)

  except KeyboardInterrupt:
    sys.stderr.close()
    return
  except IOError as e:
    if e.errno == 32: # Broken pipe
      sys.stderr.close()
      return
    if e.errno == 22: # Invalid argument
      sys.stderr.close()
      return
    raise
  except OSError as e:
    if e.errno == 22: # Invalid argument
      sys.stderr.close()
      return
    raise


if __name__ == '__main__':
  main()

