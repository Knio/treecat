# coding=utf8

import functools
import string
import sys
import mimetypes


# TODO use own term
from colorama import Fore, Back, Style


from . import term


RESET = term.ANSI.graphics_reset()


def hsize(x, empty=True):
    s = ''
    if x == 0 and empty:
        s += term.ANSI.color_fg256(term.ANSI.COLOR256.GRAY + 4)
        s += 'empty'
        s += RESET
        return s

    n = 0
    while x > 9999:
        x /= 1024
        n += 1

    s += f'{int(x):d} '

    fg = term.rgb_from_hsv(270 + n * 65, 0.3, .9)
    s += term.ANSI.color_fg256(fg)
    s += ['  B', 'KiB', 'MiB', 'GiB', 'TiB'][n]
    s += RESET
    return s

BIN_AL = list(string.ascii_letters + string.digits)
@functools.cache
def bin_style(x):
    '''
    make a byte printable and colored
    '''
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
    '''
    visual, printable, form of bytes, with colors
    '''
    s = []
    for x in data:
        style, c = bin_style(x)
        s.append(f'{style}{c}{RESET}')
    return ''.join(s)


def bin_hex(data, width):
    '''
    visual, printable, form of bytes, as hex codes, with colors
    '''
    s = []
    last_style = ''
    for x in data:
        style, c = bin_style(x)
        p = ' '
        if last_style != style:
            last_style = style
            p = f'{RESET} {style}'
        s.append(f'{p}{x:02x}')
    s.append(RESET)
    s.extend(['   '] * (width - len(s) + 1))
    return ''.join(s)


def xxd(data, width):
    '''
    generator for printable lines of some binary data,
    with <width> bytes shown on each line. the actual printable
    line width will be approximately 4-5x the number of bytes.
    '''
    if width < 0:
        width = 32
    for i in range(0, len(data), width):
        span = data[i:i + width]
        line = ' {} {}│{} {}{}\n'.format(
            bin_hex(span, width),
            RESET + Fore.YELLOW,
            RESET,
            bin_str(span),
            RESET,
        )
        yield i, line


def syntax_int(text):
    '''
    color a decimal-encoded integer with visual thousands separators
    '''
    if len(text) > 30:
        return
    try:
        i = int(text)
    except ValueError:
        return
    l = len(text)

    prefix, digits, suffix = re.match(r'^(\D*)(\d+)(\s*)$', text).groups()
    res = [suffix, RESET]
    for i in range(len(digits), 0, -3):
        fg = term.rgb_from_hsv(i * 30, .2, 1)
        res.append(text[i-3:i])
        res.append(term.ANSI.color_fg256(fg))

    res.append(prefix)
    res.append(Fore.YELLOW)
    return ''.join(reversed(res))


def syntax_highlight(p, text):
    # TODO: if file is a single integer, color by 000's
    if int_text := syntax_int(text):
        return int_text
    try:
        import pygments
        import pygments.lexers
        import pygments.formatters
        import pygments.styles
    except ImportError:
        return text
    try:
        mtype, _encoding = mimetypes.guess_type(str(p))
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
            text, lexer,
            # TODO this does not work on u14-screen-mobaxterm
            # or deb-12-screen-win-terminal
            # pygments.formatters.TerminalTrueColorFormatter(style=style))
            pygments.formatters.Terminal256Formatter(style=style))
    except Exception as e:
        print(e, file=sys.stderr)
    return text

