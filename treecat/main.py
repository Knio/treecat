# coding=utf8
'''
Tool for displaying files and directories as a tree.
'''

import argparse
import logging
import os
import sys

import colorama

import treecat


log = logging.getLogger('treecat.main')


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
  parser.add_argument('-W', '--max-line-width', type=int, default=-1)
  parser.add_argument('-D', '--no-files', action='store_true')
  parser.add_argument('-R', '--max-depth', type=int, default=-1)
  parser.add_argument('-B', '--as-binary', action='store_true', default=False)
  parser.add_argument('--no-color', action='store_true')
  parser.add_argument('--no-sums', dest='sums', action='store_false', default=True)
  parser.add_argument('--file', type=str)
  parser.add_argument('--debug', action='store_true')

  args = parser.parse_args()

  if args.debug:
    logging.basicConfig(level=logging.DEBUG)
    log.debug('Debug logging enabled')
    log.debug(args)


  # TODO add bool here for if user-set or not, so we can still use term size
  # for displaying metadata, but not crop long lines
  if args.max_line_width == -1: # -1 = auto, 0 = no limit
    args.max_line_width = 80
    try: args.max_line_width = os.get_terminal_size(0).columns
    except OSError: pass
    try: args.max_line_width = os.get_terminal_size(1).columns
    except OSError: pass

  colorama.init(strip=args.no_color)
  sys.stdout.reconfigure(encoding='utf8')

  try:
    if args.file:
      import pathlib
      f = pathlib.Path(args.file)
      st = f.stat()
      lines = treecat.file(f, child_prefix_str='', st=st, args=args)
      for line in lines:
        print(line, end='', flush=False)
      print(end='', flush=True)
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
  # except OSError as e:
  #   if e.errno == 22: # Invalid argument
  #     sys.stderr.close()
  #     return
  #   raise


if __name__ == '__main__':
  main()

