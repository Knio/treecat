# coding=utf8

import collections
import functools
import logging
import math
import mimetypes
import os
import pathlib
import string
import sys
import unicodedata

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

try:
    functools.cache
except AttributeError:
    functools.cache = lambda x:x


from colorama import Fore, Back, Style

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
    # TODO make this take args
    bad = set([
        # 'application/pdf',
    ])
    if mtype in bad:
        return False
    # if mtype.startswith('image'): return False
    if mtype.startswith('audio'): return False

    return True


def hsize(x, empty=True):
    if x == 0 and empty:
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


def tree(path, args, base=None, prefix_str=None, child_prefix_str=None, depth=0):
    if prefix_str is None:
        prefix_str = ''
    if child_prefix_str is None:
        child_prefix_str = ''

    p = pathlib.Path(path)
    if base:
        current = p.relative_to(base)
    else:
        current = p

    try:
        st = p.stat()
    except (PermissionError, IOError, OSError) as e:
        print(
            prefix_str +
            Fore.RED + str(current) + Style.RESET_ALL +
            " : " +
            Style.BRIGHT + Back.RED + str(e.args[1]) +
            Style.RESET_ALL, flush=True)
        return

    if p.is_file() and args.no_files:
        return

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
        child_str = meta(' [{}, {:>12}]'.format(mtype, hsize(sz)))
        pad = args.max_line_width - len(prefix_str) - len(str(current)) - len(child_str) - 1
        print(pad * ' ', end='')
        print(meta(child_str), end='')
        if not args.summary and printable(mtype):
            file(p, args, child_prefix_str, st)
        else:
            print(flush=True)

    elif p.is_dir():
        children = None
        try:
            children = sorted(p.iterdir())
            n = len(children)
            if n == 0:
                child_str = ' [📂, empty]'
            elif n == 1: # TODO just print parent as "foo/bar" and don't recurse
                child_str = ' [📂,   1    child, '
            else:
                child_str = f' [📂, {len(children):3d} children, '
            ds = dir_stat(p)
            if n:
                child_str += f'{ds.n_dirs:6d} subdirs, {ds.n_files:6d} files, {hsize(ds.s_files, False)+" total size":>20s}]'

            # right justify
            pad = args.max_line_width - len(prefix_str) - len(str(current)) - len(child_str) - 1
            print(' ' * pad, end='')
            print(meta(child_str), end='', flush=True)

        except IOError as e:
            print(' : ' + Back.RED + Style.BRIGHT + str(e.args[1]) + Style.RESET_ALL, end='')

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


BIN_AL = list(string.ascii_letters + string.digits)
@functools.cache
def bin_style(x):
    c = chr(x)
    if not c.isprintable():
        c = '\uFFFD'
    if x == 0:
        r = term.ANSI.COLOR256.GREY + 2
        return term.ANSI.color_bg256(r) + Fore.BLACK, '\u2400'
    if x == 255:
        return Back.RED, c
    if x == 0x20:
        bg = term.rgb_from_hsv(80, 1, .5)
        return term.ANSI.color_bg256(bg), c
    if 0 < x < 0x20:
        i = 60 - x * 3
        fg = term.rgb_from_hsv(i, .8, 1)
        bg = term.rgb_from_hsv(60, 1, .2)
        return term.ANSI.color_bg256(bg) + term.ANSI.color_fg256(fg), c
    if 0x20 < x < 0x30:
        i = 210 + x * 1.2
        fg = term.rgb_from_hsv(i, .8, 1)
        return term.ANSI.color_fg256(fg), c
    if 0x39 < x < 0x41:
        i = 260 + x * 1.2
        fg = term.rgb_from_hsv(i, .8, 1)
        return term.ANSI.color_fg256(fg), c
    if 0x5a < x < 0x61:
        i = 260 + x * 1.2
        fg = term.rgb_from_hsv(i, .8, 1)
        return term.ANSI.color_fg256(fg), c
    if 0x7a < x < 0x7f:
        i = 260 + x * 1.2
        fg = term.rgb_from_hsv(i, .8, 1)
        return term.ANSI.color_fg256(fg), c
    if 0x7f < x:
        i = 260 + x * 1.2
        bg = term.rgb_from_hsv(310, .5, .2)
        fg = term.rgb_from_hsv(i, .8, 1)
        return term.ANSI.color_bg256(bg) + term.ANSI.color_fg256(fg), c
    try:
        i = BIN_AL.index(c)
        r = term.rgb_from_hsv(80 + i * 2, 1, 1)
        return term.ANSI.color_fg256(r), c
    except ValueError: pass
    if not c.isprintable():
        return Style.BRIGHT + Fore.YELLOW, '\uFFFD'
    return '', c


def bin_str(data):
    s = []
    for x in data:
        style, c = bin_style(x)
        s.append(f'{style}{c}{Style.RESET_ALL}')
    return ''.join(s)


def bin_hex(data, width):
    s = []
    last_style = ''
    for x in data:
        style, c = bin_style(x)
        p = ' '
        if last_style != style:
            last_style = style
            p = f'{Style.RESET_ALL} {style}'
        s.append(f'{p}{x:02x}')
    s.append(Style.RESET_ALL)
    s.extend(['   '] * (width - len(s) + 1))
    return ''.join(s)


def xxd(data, width):
    if width < 0:
        width = 32
    for i in range(0, len(data), width):
        span = data[i:i + width]
        line = ' {} {}│{} {}{}\n'.format(
            bin_hex(span, width),
            Style.RESET_ALL + Fore.YELLOW,
            Style.RESET_ALL,
            bin_str(span),
            Style.RESET_ALL,
        )
        yield i, line


def is_text(data):
    try:
        text = data.decode('utf8')
    except ValueError as e:
        return None

    categories = collections.defaultdict(int)
    for x in text:
        for c in unicodedata.category(x):
            categories[c] += 1
    # TODO use this
    log.debug(categories)
    return text


def syntax_highlight(p, text):
    try:
        import pygments
        import pygments.lexers
        import pygments.formatters
        import pygments.styles
    except ImportError:
        return text
    try:
        mtype, encoding = mimetypes.guess_type(str(p))
        lexer1, lexer2, lexer3 = None, None, None
        try:   lexer1 = pygments.lexers.get_lexer_for_mimetype(mtype)
        except pygments.util.ClassNotFound: pass
        try:   lexer2 = pygments.lexers.get_lexer_for_filename(str(p))
        except pygments.util.ClassNotFound: pass
        try:   lexer3 = pygments.lexers.guess_lexer(text)
        except pygments.util.ClassNotFound: pass
        lexer = lexer1 or lexer2 or lexer3
        if not lexer:
            return text
        style = pygments.styles.get_style_by_name('solarized-dark')
        text = pygments.highlight(
            text,
            (lexer1 or lexer2 or lexer3),
            # TODO this does not work on u14-screen-mobaxterm
            # pygments.formatters.TerminalTrueColorFormatter(style=style))
            pygments.formatters.Terminal256Formatter(style=style))
    except Exception as e:
        print(e, file=sys.stderr)
    return text


def file(p, args, child_prefix_str, st):
    lines = None
    try:
        max_bytes = 0
        signal_alarm(1) # 1s timeout on reads
        if args.max_line_width and args.max_lines:
            max_bytes = args.max_lines * args.max_line_width
            data = p.open('rb').read(max_bytes)
        else:
            data = p.read_bytes()
        signal_alarm(0)
    except (TimeoutError, IOError) as e:
        if isinstance(e, TimeoutError):
            msg = 'Read Timeout'
        else:
            msg = str(e.args[1])
        print(f' : {Back.RED}{Style.BRIGHT}{msg}{Style.RESET_ALL}')
        return

    if (not args.as_binary) and (text := is_text(data)):
        is_bin = False
        orig_text = text
        text = syntax_highlight(p, text)
        lines = text.splitlines(True)

    else:
        is_bin = True
        lines = list(xxd(data, (args.max_line_width - len(child_prefix_str) - 16) // 4))

    if len(lines) == 0:
        print(' => ' + '⬔' + Style.RESET_ALL, flush=True)
        line = ''
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
        lw = len(child_prefix_str + line)
        if args.max_line_width and lw > args.max_line_width:
            l = len(line)
            line = line[:args.max_line_width]
            line = line + meta(' [{:d} chars]'.format(l))
            # TODO leave \r\n at the end
        line = line \
                .replace('\r', ' 」')\
                .replace('\n', ' 』') + '⬔'
        line = ' => ' + line
        print(line)
        return

    print(flush=True)
    if args.max_lines:
        lines = lines[:args.max_lines]
    if is_bin:
        digs = 1 + int(math.log2(lines[-1][0] + 1) / 8)
    else:
        digs = len(str(len(lines)))
    for i, line in enumerate(lines):
        if is_bin:
            i, line = line
            print_str = child_prefix_str + Fore.YELLOW + '{}│ '.format(i.to_bytes(digs, 'big').hex('.')) + Fore.WHITE + line + Style.RESET_ALL
            sys.stdout.buffer.write(print_str.encode('utf8', errors='ignore'))
            continue

        # TODO this is wrong with syntax highlighting
        lw = len(child_prefix_str + line)
        if args.max_line_width and lw > args.max_line_width:
            l = len(line)
            line = line[:args.max_line_width]
            while line[-1] in '\r\n':
                line = line[:-1]
            line = line + meta(' [{:d} chars]'.format(l)) + '\r\n'

        print_str = child_prefix_str + Fore.YELLOW + f'{(i + 1):{digs}d}│ ' + Fore.WHITE + line + Style.RESET_ALL
        sys.stdout.buffer.write(print_str.encode('utf8', errors='ignore'))

    skipped_bytes = st.st_size - len(data)
    skipped = max(0, len(lines) - args.max_lines) if args.max_lines else 0
    if skipped_bytes:
        print(child_prefix_str + meta(f'... [{st.st_size:d} bytes total]'))
    elif skipped:
        print(child_prefix_str + meta(f'... [{len(lines)} lines total]'))
    # elif '\n' not in line[-2:]:
    #     print()
    print(end='', flush=True)
    sys.stdout.buffer.flush()
