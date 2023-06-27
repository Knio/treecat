# coding=utf8
'''
Tool for displaying files and directories as a tree.
'''

import argparse
import os
import sys

import colorama

import treecat

__doc__ += f'''
version {treecat.version}
'''


def main():
  parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    description=__doc__)

  parser.add_argument('path', nargs='*')
  parser.add_argument('-s', '--summary', action='store_true')
  parser.add_argument('-L', '--max-lines', type=int, default=0)
  parser.add_argument('-W', '--max-line-width', type=int, default=0)
  parser.add_argument('-D', '--no-files', action='store_true')
  parser.add_argument('-R', '--max-depth', type=int, default=-1)
  parser.add_argument('-B', '--as-binary', action='store_true', default=False)
  parser.add_argument('--no-color', action='store_true')
  parser.add_argument('--file', type=str)

  args = parser.parse_args()

  # TODO add bool here for if user-set or not, so we can still use term size
  # for displaying metadata, but not crop long lines
  if args.max_line_width == -1: # -1 = auto, 0 = no limit
    try: args.max_line_width = os.get_terminal_size(0).columns
    except OSError: pass
    try: args.max_line_width = os.get_terminal_size(1).columns
    except OSError: pass
  if args.max_line_width == -1:
    args.max_line_width = 80

  colorama.init(strip=args.no_color)
  sys.stdout.reconfigure(encoding='utf8')

  try:
    if args.file:
      import pathlib
      print(args.file)
      treecat.file(pathlib.Path(args.file), child_prefix_str='', st=None, args=args)
      return

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

