# coding=utf8

import argparse
import sys

import colorama

from .treecat import tree

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', nargs='*')
    parser.add_argument('-s', '--summary', action='store_true')
    parser.add_argument('-L', '--max-lines', type=int)
    parser.add_argument('-W', '--max-line', type=int)
    parser.add_argument('-D', '--no-files', action='store_true')
    parser.add_argument('-R', '--depth', type=int, default=0)
    parser.add_argument('--no-color', action='store_true')


    args = parser.parse_args()
    # print(args)
    # raise Exception
    # sys.stdout.reconfigure(encoding='utf-8')

    colorama.init(strip=args.no_color)

    try:
        if not args.path:
            tree('.', args)

        for path in args.path:
            tree(path, args)

    except KeyboardInterrupt:
        sys.stderr.close()
        return
    except IOError as e:
        if e.errno == 32: # Broken pipe
            sys.stderr.close()
            return
        raise


if __name__ == '__main__':
    main()

