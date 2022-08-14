# coding=utf8

import argparse
import sys

from .treecat import tree

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', nargs='*')
    parser.add_argument('-s', '--summary', action='store_true')
    parser.add_argument('-L', '--max-lines', type=int)
    parser.add_argument('-W', '--max-line', type=int)

    args = parser.parse_args()

    # sys.stdout.reconfigure(encoding='utf8')

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
    except OSError as e:
        if e.errno == 22: # Invalid argument
            sys.stderr.close()
            return
        raise


if __name__ == '__main__':
    main()

