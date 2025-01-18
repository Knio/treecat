# coding=utf8
'''
Tool for displaying files and directories as a tree.
'''

import argparse
import logging
import os
import pathlib
import sys

# TODO replace with treecat.term
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

  parser.add_argument('paths', nargs='*')
  parser.add_argument('--version', '-V', action='store_true', help='Print version info and exit')
  parser.add_argument('-s', '--summary', action='store_true', help='Show file names only, not contents')
  # TODO: -N for tail
  parser.add_argument('-L', '--max-lines', type=int, default=0, help='Show only first MAX_LINES lines of files (head)')
  parser.add_argument('-W', '--max-line-width', type=int, default=-1)
  parser.add_argument('-D', '--no-files', action='store_true', help='Show folders only, no files')
  # TODO: -xdev
  parser.add_argument('-R', '--max-depth', type=int, default=-1, help='Recurse only MAX_DEPTH levels deep into folders')
  parser.add_argument('-B', '--as-binary', action='store_true', default=False, help='Show all files as hex (binary)')
  parser.add_argument('--no-color', action='store_true', help='Do not use ANSI colors')
  parser.add_argument('--no-sums', dest='sums', action='store_false', default=True)
  parser.add_argument('--file', type=str, help='Show one file only (no structure/headers)')
  parser.add_argument('--debug', action='store_true')
  parser.add_argument('-S', '--sudo', action='store_true', help='Escalate using sudo before starting')
  parser.add_argument('--escalated', action='store_true', help=argparse.SUPPRESS)

  args = parser.parse_args()

  if args.sudo and not args.escalated:
    paths = get_import_paths(colorama)
    cmd = escalate(paths) + ['--escalated']
    os.execv('/usr/bin/sudo', cmd)

  if args.version:
    print(f'treecat version {treecat.version} © Tom Flanagan 2024')
    print(f'  installed to {pathlib.Path(__file__).parent}')
    print(f'  running on {sys.executable} version {sys.version}')
    return

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
    lines = None

    if args.paths == ['-']:
      class fp:
        def read_bytes(self):
          return sys.stdin.read().encode('utf8')

      lines = treecat.format_file(fp(), child_prefix_str='', st=None, args=args)

    if args.file:
      f = pathlib.Path(args.file)
      st = f.stat()
      lines = treecat.format_file(f, child_prefix_str='', st=st, args=args)

    if lines:
      for line in lines:
        print(line, flush=False)
      print(end='', flush=True)
      return

    if not args.paths:
      treecat.tree('.', args)

    for path in args.paths:
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





def get_import_paths(*modules):
  paths = set()
  for m in modules:
    paths.add(pathlib.Path(m.__file__).parent.parent)
  return list(map(str, paths))


def escalate(paths, *args):
  env = dict(
    PYTHONDONTWRITEBYTECODE='1',
    PYTHONPATH=':'.join(paths)
  )
  argv = pathlib.Path('/proc/self/cmdline').read_text().split('\0')[1:-1]

  cmd = [
    'sudo', '-E',
    *[f"'{k}={v}'" for k, v in env.items()],
    sys.executable, *argv, *args,
  ]
  return cmd




if __name__ == '__main__':
  main()

