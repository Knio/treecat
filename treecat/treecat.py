# coding=utf8

import collections
import functools
import mimetypes
import os
import pathlib
import string
import sys
import unicodedata
import logging

log = logging.getLogger('treecat')

try:
    import signal
    signal_alarm = signal.alarm
    def handler(signum, frame):
        raise TimeoutError
    signal.signal(signal.SIGALRM, handler)

except AttributeError:
    # Alarm signal not supported on windows
    signal_alarm = lambda x:None

try:
    functools.cache
except AttributeError:
    functools.cache = lambda x:x


from colorama import Fore, Back, Style, init as colorama_init

# TODO move to main
# print(sys.stdout)
# raise Foo
# sys.stdout.reconfigure(encoding='utf-8')
colorama_init(strip=False) # Allow colors when not a TTY ( | less)

from ._version import __version__, version


def filter(path):
    if path.basename[0] == '.':
        return False
    return True


def color(p):
    color = Fore.RED
    if p.is_symlink():
        color = Style.BRIGHT + Fore.CYAN
    elif p.is_file():
        color = Style.BRIGHT + Fore.GREEN
    elif p.is_dir():
        color = Fore.BLUE + Back.GREEN
    else:
        color = Style.BRIGHT + Fore.RED
    return color


def printable(mtype):
    bad = set([
        'application/pdf',
    ])
    if mtype in bad:
        return False
    if mtype.startswith('image'): return False
    if mtype.startswith('audio'): return False

    return True


def hsize(x):
    if x == 0:
        return 'empty'
    n = 0
    while x > 9999:
        x /= 1024
        n += 1
    return '{:d} {}'.format(int(x),
        ['B', 'KiB', 'MiB', 'GiB', 'TiB'][n])


def meta(s):
    return Style.RESET_ALL + Style.BRIGHT + Fore.BLACK + s + Style.RESET_ALL



Dirstat = collections.namedtuple('Dir', ['n_dirs', 'n_files', 's_files'])

@functools.cache
def dir_stat(p):
    n_dirs = 0
    n_files = 0
    s_files = 0
    for d, dirs, files in os.walk(p):
        d = pathlib.Path(d)
        n_dirs += len(dirs)
        n_files += len(files)
        for f in files:
            s = (d / f).stat()
            s_files += s.st_size
        for c in dirs:
            r2 = dir_stat(d / c)
            n_dirs += r2.n_dirs
            n_files += r2.n_files
            s_files += r2.s_files
        break # don't actually use os.walk's recursion
    return Dirstat(n_dirs, n_files, s_files)


def tree(path, args, base=None, prefix_str=None, child_prefix_str=None, depth=1):
    p = pathlib.Path(path)

    if prefix_str is None:
        prefix_str = ''
    if child_prefix_str is None:
        child_prefix_str = ''

    if base:
        current = p.relative_to(base)
    else:
        current = p

    # todo collapse a/b/c
    print(prefix_str + color(p) + str(current) + Style.RESET_ALL, end='')

    if base and p.is_symlink():
        try:
            p2 = p.resolve(strict=True)
            try:
                rel = p2.relative_to(base.resolve(strict=True))
            except ValueError:
                rel = p2
            print(' -> ' + color(p2) + str(rel) + Style.RESET_ALL)
        except IOError as e:
            print(' -> ' + Style.BRIGHT + Back.RED + str(e.args[1]) + Style.RESET_ALL)

    elif p.is_file():
        mtype, encoding = mimetypes.guess_type(str(p))
        if mtype is None:
            mtype = 'unknown'
        sz = os.path.getsize(str(p))
        print(meta(' [{}, {}]'.format(mtype, hsize(sz))), end='')
        if not args.summary and printable(mtype):
            file(p, args, child_prefix_str)
        else:
            print()

    elif p.is_dir():
        children = None
        try:
            children = sorted(p.iterdir())
            n = len(children)
            if n == 0:
                child_str = ' [empty dir]'
            elif n == 1:
                # TODO just print parent as "foo/bar" and don't recurse
                child_str = ' [  1   child,  '
            else:
                child_str = f' [{len(children):3d} children, '
            ds = dir_stat(p)
            if n:
                child_str += f'{ds.n_dirs:6d} subdirs, {ds.n_files:6d} files, {hsize(ds.s_files)+" total size":>20s}]'
            print(' ' * (24 - len(str(current))), end='')
            print(meta(child_str), end='', flush=True)

        except IOError as e:
            print(' : ' + Back.RED + Style.BRIGHT + e.__doc__ + Style.RESET_ALL, end='')

        if children and (args.max_depth == -1 or depth <= args.max_depth):
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
                    child_prefix_str=child_prefix_str + c,
                    depth=depth + 1)
        else:
            print()

    else:
        print(flush=True)


BIN_AL = set(string.ascii_letters + string.digits)
@functools.cache
def bin_style(x):
    c = chr(x)
    if c in BIN_AL:
        return Fore.CYAN, c
    if x == 0:
        return Style.DIM, '\u2400'
    if x == 255:
        return Fore.GREEN, c
    if not c.isprintable():
        return Style.BRIGHT + Fore.YELLOW, '\uFFFD'
    return '', c


def bin_str(data):
    s = []
    cur_style = None
    for x in data:
        style, c = bin_style(x)
        if style != cur_style:
            s.append(Style.RESET_ALL)
            s.append(style)
            cur_style = style
        s.append(c)
    return ''.join(s)


def bin_hex(data, width):
    s = []
    cur_style = None
    for x in data:
        style, c = bin_style(x)
        t = ''
        if style != cur_style:
            t = Style.RESET_ALL + style
            cur_style = style
        s.append(f'{t}{x:02x}')
    s.extend(['  '] * (width - len(s)))
    return ' '.join(s)


def xxd(data, width=None):
    if width is None:
        width = 32
    for i in range(0, len(data), width):
        span = data[i:i + width]
        line = ' {} {}│{} {}\n'.format(
            bin_hex(span, width),
            Style.RESET_ALL + Fore.YELLOW,
            Style.RESET_ALL,
            bin_str(span),
            Style.RESET_ALL,
        )
        yield i, line


def file(p, args, child_prefix_str):

    lines = None
    is_bin = False
    try:
        signal_alarm(1)
        # 1s timeout on reads
        data = open(p, 'rb').read()
        signal_alarm(0)
        try:
            text = data.decode('utf8')
            categories = collections.defaultdict(int)
            for x in text:
                for c in unicodedata.category(x):
                    categories[c] += 1
            log.debug(categories)
            lines = text.splitlines(True)
        except ValueError as e:
            log.debug('Assuming binary data. %r', e)
            lines = list(xxd(data, args.max_line))
            is_bin = True
    except TimeoutError as e:
        print(' : ' + Back.RED + Style.BRIGHT + 'ReadTimeout' + Style.RESET_ALL)
        return
    except IOError as e:
        print(' : ' + Back.RED + Style.BRIGHT + str(e.args[1]) + Style.RESET_ALL)
        return
    # except Exception as e:
    #     print(' : ' + Back.RED + Style.BRIGHT + str(e) + Style.RESET_ALL)
    #     return
    if len(lines) == 0:
        print(' => ' + Style.DIM + Fore.BLACK + Back.WHITE + '␄' + Style.RESET_ALL, flush=True)
        return
    if len(lines) == 1:
        print(end='', flush=True)
        line = lines[0]
        if is_bin:
            i, line = line
            print_str = ''.join((
                ' => ',
                bin_hex(data, 0), Style.RESET_ALL,
                Fore.YELLOW, ' │ ', Style.RESET_ALL,
                bin_str(data),
            ))
            print(print_str)
            return
        if args.max_line and len(child_prefix_str + line) > args.max_line:
            l = len(line)
            line = line[:args.max_line]
            line = line + meta(' [{:d} chars]'.format(l))
            # TODO leave \r\n at the end
        line = line \
                .replace('\r', ' ␍')\
                .replace('\n', ' ␊') + ' ␃'
        line = ' => ' + line
        print(line)
        return
    print(flush=True)
    for i, line in enumerate(lines[:args.max_lines]):
        if is_bin:
            i, line = line
            print_str = child_prefix_str + Fore.YELLOW + '{}│ '.format(i.to_bytes(4, 'big').hex('.')) + Fore.WHITE + line + Style.RESET_ALL
            sys.stdout.buffer.write(print_str.encode('utf8', errors='ignore'))
            continue

        if args.max_line and len(child_prefix_str + line) > args.max_line:
            l = len(line)
            line = line[:args.max_line]
            while line[-1] in '\r\n':
                line = line[:-1]
            line = line + meta(' [{:d} chars]'.format(l)) + '\r\n'

        print_str = child_prefix_str + Fore.YELLOW + '{:2d}│ '.format(i + 1) + Fore.WHITE + line + Style.RESET_ALL
        sys.stdout.buffer.write(print_str.encode('utf8', errors='ignore'))

    skipped = max(0, len(lines) - args.max_lines) if args.max_lines else 0
    if skipped:
        print(child_prefix_str + meta('... [{:d} lines]'.format(len(lines))))
    elif not '\n' in line[-2:]:
        print()
    print(end='', flush=True)
    sys.stdout.buffer.flush()
