# coding=utf8

import sys
import py.path
from colorama import Fore, Back, Style

from ._version import __version__, version


def filter(path):
    if path.basename[0] == '.':
        return False
    return True


def color(p):
    color = Fore.RED

    if p.islink():
        color = Style.BRIGHT + Fore.CYAN
    elif p.isfile():
        color = Style.BRIGHT + Fore.GREEN
    elif p.isdir():
        color = Fore.BLUE + Back.GREEN
    else:
        color = Style.BRIGHT + Fore.RED

    return color

def tree(path, args, base=None, prefix_str=None, child_prefix_str=None):
    p = py.path.local(path)

    if prefix_str is None:
        prefix_str = ''
    if child_prefix_str is None:
        child_prefix_str = ''

    if base:
        current_str = base.bestrelpath(p)
    else:
        current_str = str(p)

    print(prefix_str + color(p) + current_str + Style.RESET_ALL, end='')

    if base and p.islink():
        p2 = p.realpath()
        rel = base.bestrelpath(p2)

        print(' -> ' + color(p2) + rel + Style.RESET_ALL)

    elif p.isfile():
        if not args.summary:
            file(p, args, child_prefix_str)
        else:
            print()

    elif p.isdir():
        children = None
        try:
            children = p.listdir(sort=True, fil=filter)
        except Exception as e:
            print(' : ' + Back.RED + Style.BRIGHT + str(e.args) + Style.RESET_ALL)

        if children:
            print(flush=True)
            n = len(children)
            for i, child in enumerate(children):
                if i == n - 1:
                    h = '└── '
                    c = '    '
                else:
                    h = '├── '
                    c = '│   '

                tree(child, args,
                    base=p,
                    prefix_str=child_prefix_str + h,
                    child_prefix_str=child_prefix_str + c)

    else:
        print(flush=True)

def file(p, args, child_prefix_str):
    lines = None
    try:
        f = open(str(p), encoding='utf8', errors='surrogateescape')
        lines = f.readlines()
    except Exception as e:
        print(' : ' + Back.RED + Style.BRIGHT + str(e.args[1]) + Style.RESET_ALL)
    if lines is not None:
        if len(lines) > 1:
            print(flush=True)
            pre = child_prefix_str
        elif lines:
            print(end='', flush=True)
            pre = ' => '
            lines[0] = lines[0]\
                    .replace('\r', '␍')\
                    .replace('\n', '␊') + '\n'
        for line in lines[:args.max_lines]:
            print_str = pre + Style.DIM + Fore.WHITE + '█ ' + line + Style.RESET_ALL
            sys.stdout.buffer.write(print_str.encode('utf8', errors='ignore'))
        if args.max_lines:
            skipped = max(0, len(lines) - args.max_lines)
            if skipped:
                print(child_prefix_str + Fore.WHITE + '... {:d} lines truncated'.format(skipped) + Style.RESET_ALL)
        sys.stdout.buffer.flush()
        if not lines:
            print(' => ' + Style.DIM + Fore.BLACK + Back.WHITE + '␄' + Style.RESET_ALL, flush=True)
        else:
            print(end='', flush=True)
