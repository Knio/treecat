# coding=utf8

import argparse

from .treecat import tree

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', nargs='*')
    parser.add_argument('-s', '--summary', action='store_true')
    parser.add_argument('-L', '--max-lines', type=int)

    args = parser.parse_args()

    if not args.path:
        tree('.', args)

    for path in args.path:
        tree(path, args)


if __name__ == '__main__':
    main()
