# coding=utf8

import argparse

from .treecat import tree

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', nargs='?', default='')

    args = parser.parse_args()

    tree(args.path, args)
