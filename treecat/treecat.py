# coding=utf8

import collections
import functools
import logging
import math
import mimetypes
import os
import pathlib
import re
import string
import sys
import unicodedata


# TODO use own term
from colorama import Fore, Back, Style


from . import pretty
from . import term

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


def filter(path):
    if path.basename[0] == '.':
        return False
    return True


def get_string_width(s):
    s = term.ANSI.strip(s)
    s = s.replace('\t', 'T' * 6)
    return len(s)


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
    # TODO make this take args
    bad = set([
        # 'application/pdf',
    ])
    if mtype in bad:
        return False
    # if mtype.startswith('image'): return False
    if mtype.startswith('audio'): return False

    return True


def mtype_color(mtype):
    # TODO: figure out 🎬 📄 (prints double wide and messes up formatting)
    mtype = mtype.replace('video/', f'🎞️ /')
    mtype = mtype.replace('image/', '🖼️ /')
    mtype = mtype.replace('text/', '🗎 /')
    mtype = mtype.replace('application/', '🗗 /')
    return mtype


def meta(s):
    return Style.RESET_ALL + Style.BRIGHT + Fore.BLACK + s + Style.RESET_ALL


debug_padding = 1
def nl(n):
    s = '\n' \
        f'{term.ANSI.color_bg8(term.ANSI.COLOR8.RED)}' \
        f'{term.ANSI.color_fg8(term.ANSI.COLOR8.BLACK)}' \
        f'{n}' \
        f'{term.ANSI.graphics_reset()}'
    print(s, end='')


debug_padding = 0
def nl(n):
    print()


Dirstat = collections.namedtuple('Dir', ['n_dirs', 'n_files', 's_files'])

@functools.cache
def dir_stat(p):
    '''
    recursively sums up counts for a dir.
    WARNING: can be very expensive
    '''
    p = p.resolve()
    n_dirs = 0
    n_files = 0
    s_files = 0
    for d, dirs, files in os.walk(p):
        d = pathlib.Path(d)
        n_dirs += len(dirs)
        n_files += len(files)
        for f in files:
            try:
                s = (d / f).stat()
                s_files += s.st_size
            except KeyboardInterrupt:
                raise
            except (FileNotFoundError, OSError):
                pass
        for c in dirs:
            try:
                cd = (d / c).resolve(True)
                if not cd.is_relative_to(p):
                    # outside of current subdir
                    continue
                if d.samefile(cd):
                    # points back to itself
                    continue
                r2 = dir_stat(d / c)
                n_dirs += r2.n_dirs
                n_files += r2.n_files
                s_files += r2.s_files
            except (FileNotFoundError, OSError):
                pass
        break # don't actually use os.walk's recursion
    return Dirstat(n_dirs, n_files, s_files)


def tree_file(p, current, args, base=None, prefix_str='', child_prefix_str='', depth=0):
    color_chars = 14

    try:
        st = p.stat()
    except:
        st = None

    mtype, _encoding = mimetypes.guess_type(str(p))
    if mtype is None:
        mtype = 'unknown'
    sz = os.path.getsize(str(p))
    child_str = meta(f' [{mtype_color(mtype)}, {pretty.hsize(sz):>23}]')

    fg = []
    pad_width = 18
    if (not args.summary) and printable(mtype):
        fg = list(format_file(p, args, child_prefix_str, st))
    inline = len(fg) == 1
    inline = False # it's broken
    if inline:
        # TODO: break out if it doesn't fit in max_line_width
        l = fg.pop()
        lw = get_string_width(l)
        log.debug('single line file: %r', l)
        log.debug('        stripped: %r', term.ANSI.strip(l))
        pw = args.max_line_width - len(prefix_str) - len(str(current)) - len(child_str) - debug_padding
        # l = 'X' * aw
        pad_width -= max(lw, pw)
        pp = pw - lw
        log.debug(
            'prefix_str: %d '
            'name: %d '
            'line: %d '
            'line stripped: %d '
            'pre-line padding: %s',
            len(prefix_str),
            len(str(current)),
            len(l),
            lw,
            pp
        )
        # TODO: this doesn't look right
        print(' ' * pp, end='')
        print(l, end='')

    pad = args.max_line_width - len(prefix_str) - len(str(current)) - len(child_str) + color_chars + pad_width - debug_padding
    log.debug('pad: %s', pad)
    pad_s = pad * '┈'
    # pad_s = pad * ' '
    print(term.ANSI.graphics(term.ANSI.GRAPHICS.DIM) + pad_s + term.ANSI.graphics_reset(), end='')
    print(meta(child_str), end='')
    print()
    # if fg:
    #     print()
    for line in fg:
        print(line)
    # nl(1)


def tree_dir(p, current, args, base=None, prefix_str='', child_prefix_str='', depth=0):
    color_chars = 14
    folder = '📂'
    # folder = '🗁 '

    children = None
    try:
        children = sorted(p.iterdir())
        n = len(children)
        if n == 0:
            x = ' ' * (45 + color_chars)
            child_str = f' [{folder} {x}{pretty.hsize(0)}]'
        elif n == 1 and children[0].is_dir():
            # just print parent as "foo/bar" and don't recurse
            # TODO: print the dir stats from the topmost nonsingle parent, not the leaf
            c = children[0]
            cc = c.relative_to(p)
            print('/', end='')
            print(color(p) + str(cc) + Style.RESET_ALL, end='')

            tree_dir(c, cc, args,
                base=p,
                prefix_str=prefix_str + str(current) + '/',
                child_prefix_str=child_prefix_str,
                depth=depth)
            # nl(4)
            return
            # child_str = f' [{folder}   1    child'

        else:
            child_str = f' [{folder} {len(children):3d} children'
        if n and args.sums:
            try:
                ds = dir_stat(p)
                child_str += f', {ds.n_dirs:6d} subdirs, {ds.n_files:6d} files, total size: {pretty.hsize(ds.s_files, False):>23s}]'
            except:
                import traceback
                traceback.print_exc()
                # ??
        elif n:
            # child_str += ' ' * (45 + color_chars - 1)
            child_str += ']'
            color_chars -= 15


        # right justify
        pad = args.max_line_width - len(prefix_str) - len(str(current)) - len(child_str) + color_chars - debug_padding
        print(' ' * pad, end='')
        print(meta(child_str), end='')
        nl(2)

    except IOError as e:
        print(f' : [1]{Back.RED}{Style.BRIGHT}{e.args[1]:s}{Style.RESET_ALL}', end='')

    lr = 1
    if children and (args.max_depth == -1 or depth <= args.max_depth):
        # print(flush=True)
        n = len(children)
        for i, child in enumerate(children):
            if i == n - 1:
                h = '└── '
                c = '    '
            else:
                h = '├── '
                c = '│   '

            lr = tree(child, args,
                base=p,
                prefix_str=child_prefix_str + h,
                child_prefix_str=child_prefix_str + c,
                depth=depth + 1)
            if lr == -1:
                # nl(3)
                lr = 1
    # # print(f'>>>[{p} {lr}]<<<',end='')
    # if lr == -1:
    #     # no children or last newline was skipped
    #     print(flush=True)


def tree(path, args, base=None, prefix_str='', child_prefix_str='', depth=0):
    '''
    assume we are on a fresh new line
    '''
    log.debug('tree(%s, <args>, %s, %r, %r, %s)', path, base, prefix_str, child_prefix_str, depth)

    p = pathlib.Path(path)
    if base:
        current = p.relative_to(base)
    else:
        current = p

    if p.is_file() and args.no_files:
        return -1

    # own name
    print(prefix_str + color(p) + str(current) + Style.RESET_ALL, end='')

    if base and p.is_symlink():
        # TODO print metadata ie [symlink] right justified
        try:
            p2 = p.resolve(strict=True)
            try:
                rel = p2.relative_to(base.resolve(strict=True))
            except ValueError:
                rel = p2
            print(' ⇨ ' + color(p2) + str(rel) + Style.RESET_ALL)
        except IOError as e:
            if e.errno == 2:
                # TODO: for [socket:234] files, lsof knows how to map to IPs
                # TODO for fdinfo files, ../<fd> mnt_id --> /proc/<pid>/mountinfo
                print(f' ⇨ {Style.BRIGHT}{Back.RED}{p.readlink()}{Style.RESET_ALL}')
            else:
                print(f' ⇨ [0]{Style.BRIGHT}{Back.RED}{e:r}{Style.RESET_ALL}')

    elif p.is_file():
        tree_file(p, current, args, base, prefix_str, child_prefix_str, depth)

    elif p.is_dir():
        tree_dir(p, current, args, base, prefix_str, child_prefix_str, depth)

    else:
        # what is this file??
        print(f'UNKNOWN: {p!r}')
        print(flush=True)



def is_text(data):
    '''
    decide if some bytes are "text" or not.
    if they are, return them as a unicode string.
    if not, return None
    '''
    try:
        text = data.decode('utf8')
    except ValueError as e:
        return None

    categories = collections.defaultdict(int)
    for x in text:
        for c in unicodedata.category(x):
            categories[c] += 1
    log.debug(categories)
    total = len(text)
    if not total:
        return None
    printable = sum((
        categories['L'],
        categories['N'],
        categories['Z'],
        categories['C'],
    ))
    if (printable / total) > 0.6:
        return text
    if categories['C'] / total > 0.05:
        return False
    # TODO add more categories
    return text


def format_file(p, args, child_prefix_str, st):
    log.debug('file(%s, <args>, %r, <st>)', p, child_prefix_str)
    lines = None
    eof = None
    try:
        max_bytes = 0
        signal_alarm(1) # 1s timeout on reads
        if args.max_line_width and args.max_lines:
            max_bytes = args.max_lines * args.max_line_width
            data = p.open('rb').read(max_bytes)
            eof = len(data) < max_bytes
        else:
            # TODO better handling of large files
            data = p.read_bytes()
            eof = True
        signal_alarm(0)
    except (TimeoutError, IOError) as e:
        if isinstance(e, TimeoutError):
            msg = 'Read Timeout'
        else:
            msg = str(e.args[1])
        yield f'{child_prefix_str} 🡺  [2]{Back.RED}{Style.BRIGHT}{msg}{Style.RESET_ALL}'
        return

    if (not args.as_binary) and (text := is_text(data)):
        is_bin = False
        orig_text = text
        text = pretty.syntax_highlight(p, text)
        lines = text.splitlines(True)

    else:
        is_bin = True
        bytes = (args.max_line_width - len(child_prefix_str) - 16) // 4
        bytes = 4 * (bytes // 4)
        lines = list(pretty.xxd(data, bytes))

    log.debug(f'is_bin={is_bin}, len(lines)={len(lines)}')
    if len(lines) == 0:
        yield f'{child_prefix_str} 🡺  ⬔{Style.RESET_ALL}'
        return

    if False and len(lines) == 1: # broken
        line = lines[0]
        if is_bin:
            i, line = line
            yield ''.join((
                ' 🡺  ',
                pretty.bin_hex(data, 0), Style.RESET_ALL,
                Fore.YELLOW, ' │ ', Style.RESET_ALL,
                pretty.bin_str(data),
            ))
            return
        lw = len(child_prefix_str + line)
        if args.max_line_width and lw > args.max_line_width:
            l = len(line)
            line = line[:args.max_line_width]
            line = line + meta(' [{:d} chars]'.format(l))
            # TODO leave \r\n at the end (??)
            # TODO split this out to a function, and add colors
            line = line \
                .replace('\r', ' ␍')\
                .replace('\n', ' ␊')\
                .replace('\t', ' → ')\
                      + ' ⮽ '\
        # TODO add the arrow inside tree() instead?
        yield f' 🡺  {line}'
        return

    # many lines
    read_lines = len(lines)
    skipped = 0
    if args.max_lines:
        skipped = read_lines - args.max_lines
        lines = lines[:args.max_lines]
    if is_bin:
        digs = 1 + int(math.log2(lines[-1][0] + 1) / 8)
    else:
        digs = len(str(len(lines)))
    for i, line in enumerate(lines):
        if is_bin:
            i, line = line
            print_str = child_prefix_str + Fore.YELLOW + '{}│ '.format(i.to_bytes(digs, 'big').hex('.')) + Fore.WHITE + line + Style.RESET_ALL
            yield print_str
            continue

        lw = get_string_width(child_prefix_str + line)
        if args.max_line_width and lw > args.max_line_width:
            l = get_string_width(line)
            line = line[:args.max_line_width]
            while line[-1] in '\r\n':
                line = line[:-1]
            line = line + meta(f' [{l:d} chars]')

        # TODO do this better
        while line and line[-1] in '\r\n':
            line = line[:-1]

        print_str = child_prefix_str + Fore.YELLOW + f'{(i + 1):{digs}d}│ ' + Fore.WHITE + line + Style.RESET_ALL
        yield print_str

    if st:
        skipped_bytes = st.st_size - len(data)
        log.debug(f'skipped_bytes: {skipped_bytes}, skipped: {skipped}')
        if (not eof) and (skipped_bytes > 0):
            yield child_prefix_str + meta(f'... [{st.st_size:d} bytes total]\n')
    elif skipped:
        yield child_prefix_str + meta(f'... [{read_lines} lines total]\n')
