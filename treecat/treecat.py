# coding=utf8

import os
import sys
import py.path
try:
    import signal
    signal_alarm = signal.alarm
    def handler(signum, frame):
        raise TimeoutError
    signal.signal(signal.SIGALRM, handler)


except ImportError:
    signal_alarm = lambda:None

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


def hsize(x):
    if x == 0:
        return 'empty'
    n = 0
    while x > 9999:
        x /= 1024
        n += 1
    return '{:d} {}'.format(int(x), ['B', 'KiB', 'MiB', 'GiB', 'TiB'][n])


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
        try:
            p2 = p.realpath()
            rel = base.bestrelpath(p2)
            print(' -> ' + color(p2) + rel + Style.RESET_ALL)
        except Exception as e:
            print(' -> ' + Style.BRIGHT + Back.RED + str(e.args[1]) + Style.RESET_ALL)


    elif p.isfile():
        sz = os.path.getsize(str(p))
        print(Style.BRIGHT + Fore.BLACK + ' [{}]'.format(hsize(sz)) + Style.RESET_ALL, end='')
        if not args.summary:
            file(p, args, child_prefix_str)
        else:
            print()

    elif p.isdir():
        children = None
        try:
            children = p.listdir(sort=True, fil=filter)
            n = len(children)
            if n == 0:
                child_str = ' [empty]'
            elif n == 1: # TODO just print parent as "foo/bar" and don't recurse
                child_str = ' [1 child]'
            else:
                child_str = ' [{} children]'.format(len(children))
            print(Style.BRIGHT + Fore.BLACK + child_str + Style.RESET_ALL, end='')

        except Exception as e:
            print(' : ' + Back.RED + Style.BRIGHT + e.__doc__ + Style.RESET_ALL, end='')

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
            print()

    else:
        print(flush=True)

def file(p, args, child_prefix_str):
    lines = None
    try:
        f = open(str(p), encoding='utf8', errors='surrogateescape')
        signal_alarm(1)
        lines = f.readlines()
        signal_alarm(0)
    except TimeoutError as e:
        print(' : ' + Back.RED + Style.BRIGHT + 'ReadTimeout' + Style.RESET_ALL)
        return
    except Exception as e:
        print(' : ' + Back.RED + Style.BRIGHT + str(e.args[1]) + Style.RESET_ALL)
        return
    if len(lines) == 0:
        print(' => ' + Style.DIM + Fore.BLACK + Back.WHITE + '␄' + Style.RESET_ALL, flush=True)
        return
    if len(lines) == 1:
        print(end='', flush=True)
        line = ' => ' + lines[0]\
                .replace('\r', ' ␍')\
                .replace('\n', ' ␊') + ' ␃'
        print(line)
        return
    print(flush=True)
    pre = child_prefix_str
    for i, line in enumerate(lines[:args.max_lines]):
        print_str = pre + Fore.YELLOW + '{:2d}│ '.format(i + 1) + Fore.WHITE + line + Style.RESET_ALL
        sys.stdout.buffer.write(print_str.encode('utf8', errors='ignore'))
    if args.max_lines:
        skipped = max(0, len(lines) - args.max_lines)
        if skipped:
            print(child_prefix_str + Fore.WHITE + '... {:d} lines truncated'.format(skipped) + Style.RESET_ALL)
    # print()
    sys.stdout.buffer.flush()

