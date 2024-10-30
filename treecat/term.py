#! /usr/bin/python3.10
# -*- coding: utf-8 -*-


import argparse
import locale
import os
import re
import sys
from enum import Enum, IntEnum

try:
    import termios
except ImportError:
    termios = None

try:
    import colorama
except ImportError:
    colorama = None



def t_term():
  print('** Terminal settings ' + '*' * 40)
  print()
  print(f'System default encoding:    {sys.getdefaultencoding()}')
  print(f'Locale preferred encoding:  {locale.getpreferredencoding()}')
  print(f'Default locale: {locale.getdefaultlocale()}')
  print(f'Current locale: {locale.getlocale()}')
  print('stdin')
  print(f'    encoding: {sys.stdin.encoding}')
  print(f'    tty:      {sys.stdin.isatty()}')
  print(f'    errors:   {sys.stdin.errors}')
  print('stdout')
  print(f'    encoding: {sys.stdout.encoding}')
  print(f'    tty:      {sys.stdout.isatty()}')
  print(f'    errors:   {sys.stdout.errors}')
  if termios:
    print('termios attrs:')
    attrs = termios.tcgetattr(sys.stdin.fileno())
    print(f'    input:    {attrs[0]:016b}  {attrs[0]:04x}')
    print(f'    output:   {attrs[1]:016b}  {attrs[1]:04x}')
    print(f'    control:  {attrs[2]:016b}  {attrs[2]:04x}')
    print(f'    local:    {attrs[3]:016b}  {attrs[3]:04x}')
    print(f'    ispeed:   {attrs[4]}')
    print(f'    ospeed:   {attrs[5]}')
    print(f'    chars:    {b"".join(attrs[6]).hex(" ")}')
  else:
    print('termios not available')
  try:
    x = os.get_terminal_size(0)
    print(f'stdin  size: {x}')
  except OSError as e:
    print(f'stdin  size: {e}')
  try:
    x = os.get_terminal_size(1)
    print(f'stdout size: {x}')
  except OSError as e:
    print(f'stdout size: {e}')

  # TODO: termcap



def t_unicode():
  # https://emojipedia.org/unicode-10.0/
  print('** Unicode support ' + '*' * 40)
  print()

  print('''Unicode 15.1 (2023-09-12):
      🫨 🩵 🩶 🩷 🫸 🫷 🫎 🫏 🪽 🪿 🪼 🫚 🪻 🫛 🪭 🪮 🪇 🪈 🪯 🛜''')
  print('''Unicode 14.0 (2021-09-14):
      🫢 🫣 🫡 🫥 🫤 🥹 🫱 🫲 🫳 🫴 🫰 🫵 🫶 🫦 🫅 🫃 🫄 🧌 🪸 🪷 🪹
      🪺 🫘 🫗 🫙 🛝 🛞 🛟 🪬 🪩 🪫 🩼 🩻 🫧 🪪 🟰''')
  print('''Unicode 13.0 (2020-03-10):
      🥲 🥸 🤌 🫀 🫁 🥷 🫂 🦬 🦣 🦫 🦤 🪶 🦭 🪲 🪳 🪰 🪱 🪴 🫐 🫒 🫑
      🫓 🫔 🫕 🫖 🧋 🪨 🪵 🛖 🛻 🛼 🪄 🪅 🪆 🪡 🪢 🩴 🪖 🪗 🪘 🪙 🪃
      🪚 🪛 🪝 🪜 🛗 🪞 🪟 🪠 🪤 🪣 🪥 🪦 🪧''')
  print('''Unicode 12.0 (2019-03-05):
      🥱 🤎 🤍 🤏 🦾 🦿 🦻 🧏 🧍 🧎 🦧 🦮 🦥 🦦 🦨 🦩 🧄 🧅 🧇 🧆 🧈
      🦪 🧃 🧉 🧊 🛕 🦽 🦼 🛺 🪂 🪐 🤿 🪀 🪁 🦺 🥻 🩱 🩲 🩳 🩰 🪕 🪔
      🪓 🦯 🩸 🩹 🩺 🪑 🪒 🟠 🟡 🟢 🟣 🟤 🟥 🟧 🟨 🟩 🟦 🟪 🟫''')
  print('''Unicode 11.0 (2018-06-05):
      🥰 🥵 🥶 🥴 🥳 🥺 🦵 🦶 🦷 🦴 🦸 🦹 🦰 🦱 🦳 🦲 🦝 🦙 🦛 🦘🦡
      🦢 🦚 🦜 🦟 🦠 🥭 🥬 🥯 🧂 🥮 🦞 🧁 🧭 🧱 🛹 🧳 🧨 🧧 🥎 🥏 🥍
      🧿 🧩 🧸 🧵 🧶 🥽 🥼 🥾 🥿 🧮 🧾 🧰 🧲 🧪 🧫 🧬 🧴 🧷 🧹 🧺 🧻
      🧼 🧽 🧯''')
  print('''Unicode 10.0 (2017-06-20):
      🤩 🤪 🤭 🤫 🤨 🤮 🤯 🧐 🤬 🧡 🤟 🤲 🧠 🧒 🧑 🧔 🧓 🧕 🤱 🧙 🧚
      🧛 🧜 🧝 🧞 🧟 🧖 🧗 🧘 🦓 🦒 🦔 🦕 🦖 🦗 🥥 🥦 🥨 🥩 🥪 🥣 🥫
      🥟 🥠 🥡 🥧 🥤 🥢 🛸 🛷 🥌 🧣 🧤 🧥 🧦 🧢 ₿''')
  print('''Unicode 9.0 (2016-06-21):
      🤣 🤥 🤤 🤢 🤧 🤠 🤡 🖤 🤚 🤞 🤙 🤛 🤜 🤝 🤳 🤦 🤷 🤴 🤵 🤰 🤶
      🕺 🤺 🤸 🤼 🤽 🤾 🤹 🦍 🦊 🦌 🦏 🦇 🦅 🦆 🦉 🦎 🦈 🦋 🥀 🥝 🥑
      🥔 🥕 🥒 🥜 🥐 🥖 🥞 🥓 🥙 🥚 🥘 🥗 🦐 🦑 🥛 🥂 🥃 🥄 🛵 🛴 🛑
      🛶 🥇 🥈 🥉 🥊 🥋 🥅 🥁 🛒 ''')
  print('''Unicode 8.0 (2015-06-17):
      🙃 🤑 🤗 🤔 🤐 🙄 🤒 🤕 🤓 🤖 🤘 🏻 🏼 🏽 🏾 🏿 🦁 🦄 🦃 🦂 🧀
      🌭 🌮 🌯 🍿 🦀 🍾 🏺 🕌 🕍 🕋 🏐 🏏 🏑 🏒 🏓 🏸 📿 🏹 🛐 🕎 ''')
  print('''Unicode 7.0 (2014-06-16):
      🙂 🙁 🕳️ 🗨️ 🗯️ 🖐️ 🖖 🖕 👁️ 🕵️ 🕴️ 🏌️ 🏋️ 🛌 🗣️ 🐿️ 🕊️ 🕷️ 🕸️ 🏵️ 🌶️
      🍽️ 🗺️ 🏔️ 🏕️ 🏖️ 🏜️ 🏝️ 🏞️ 🏟️ 🏛️ 🏗️ 🏘️ 🏚️ 🏙️ 🏎️ 🏍️ 🛣️ 🛤️ 🛢️ 🛳️ 🛥️
      🛩️ 🛫 🛬 🛰️ 🛎️ 🕰️ 🌡️ 🌤️ 🌥️ 🌦️ 🌧️ 🌨️ 🌩️ 🌪️ 🌫️ 🌬️ 🎗️ 🎟️ 🎖️ 🏅 🕹️
      🖼️ 🕶️ 🛍️ 🎙️ 🎚️ 🎛️ 🖥️ 🖨️ 🖱️ 🖲️ 🎞️ 📽️ 📸 🕯️ 🗞️ 🏷️ 🗳️ 🖋️ 🖊️ 🖌️ 🖍️
      🗂️ 🗒️ 🗓️ 🖇️ 🗃️ 🗄️ 🗑️ 🗝️ 🛠️ 🗡️ 🛡️ 🗜️ 🛏️ 🛋️ 🕉️ ⏸️ ⏹️ ⏺️ 🏴 🏳️
      🏲 🖷 🖏 🕭 🕪 🗪 🎕 🖅 🖿 🕼 🕱 🕮 🗴 🎝 🛊 🗇 🛦 🖰 🗶 🖳 🗷 🛧 🗉 🕈 🛈 🗬 🔾 🕬 🖧 🕾 🖪
      🖶 🖑 🛪 🖣 🗹 🗢 🕨 🖾 🖓 🖠 🗅 🗵 🖉 🖩 🖎 🗕 🗮 🖄 🗠 🖹 🗎 🕲 🗭 🖡 🖔 🗸 🗆 🖸 🌣 🛱 🖽
      🖭 🖒 🖚 🔿 🖫 🖯 🗫 🖵 🕄 🎘 🗌 🗥 🌢 🗘 🖜 🗀 🗏 🖬 🗖 🗤 🖁 🏶 🕩 🖙 🖀 🏱 🗗 🗰 🛉 🖢 🖺
      🖟 🕽 🎔 🕿 🖞 🖗 🖝 🗟 🗐 🛆 🖦 🖮 🛇 🗁 🖻 🗱 📾 🖘 🕫 🗍 🗈 🖴 🖃 🗙 🗛 🖛 🎜 🕅 🛨 🗚 🕻
      🗋 🕇 🗧 🗦 🗲 🛲 🕆 🖂 🗊 🗩 🖈 🗔 🖆 ''')

  print('''Unicode 6.1 (Unknown):
      😀 😗 😙 😛 😑 😬 😴 😕 😟 😮 😯 😦 😧 🕀 🕁 🕃 🕂 ''')
  # TODO
  # print('''Unicode 5.0 (2017-06-20): ''')
  # print('''Unicode 4.0 (2017-06-20): ''')
  # print('''Unicode 3.0 (2017-06-20): ''')
  # print('''Unicode 2.0 (2017-06-20): ''')
  # print('''Unicode 1.0 (2017-06-20): ''')

  print()

  def print_codes(name, codes, span=32):
    codes = list(codes)
    print(f'{name}:')

    for i in range(0, len(codes), span):
        print(' ' * 8 + '  '.join(codes[i:i+span]))

  # https://unicode-table.com/en/blocks/spacing-modifier-letters/
  # https://unicode-explorer.com/blocks

  print_codes('Arrows',           map(chr, range(0x2190, 0x2200)))
  print_codes('Arrows-A',         map(chr, range(0x27f0, 0x2800)))
  print_codes('Arrows-B',         map(chr, range(0x2900, 0x2980)))
  print_codes('Arrows-C',         map(chr, range(0x1f800,0x1f900)))
  print_codes('Miscellaneous Symbols and Arrows',
                                  map(chr, range(0x2b00, 0x2c00)))
  print_codes('Miscellaneous Symbols-B',
                                  map(chr, range(0x2980, 0x2a00)))
  print_codes('Miscellaneous Technical',
                                  map(chr, range(0x2300, 0x2400)))
  print_codes('Control Pictures', map(chr, range(0x2400, 0x2440)))
  print_codes('Specials',         map(chr, range(0xfff0, 0x10000)))

  print_codes('Currency Symbols', map(chr, range(0x20a0, 0x20d0)))

  print_codes('General Punctuation',
                                  map(chr, range(0x2000, 0x2070)))
  print_codes('Supplemental Punctuation',
                                  map(chr, range(0x2e00, 0x2e80)))

  print_codes('Letterlike Symbols',
                                  map(chr, range(0x2100, 0x2150)))
  print_codes('Number Forms',
                                  map(chr, range(0x2150, 0x2190)))
  print_codes('Mathematical Operators',
                                  map(chr, range(0x2200, 0x2300)))
  print_codes('Supplemental Mathematical Operators',
                                  map(chr, range(0x2a00, 0x2b00)))
  print_codes('Mathematical Alphanumeric Symbols',
                                  map(chr, range(0x1d400, 0x1d800)), span=26)

  print_codes('Box drawing',      map(chr, range(0x2500, 0x2580)))
  print_codes('Block elements',   map(chr, range(0x2580, 0x25a0)))
  print_codes('Geometric shapes', map(chr, range(0x25a0, 0x2600)))
  print_codes('Geometric Shapes Extended',
                                  map(chr, range(0x1f780, 0x1f800)))
  print_codes('Optical Character Recognition',
                                  map(chr, range(0x2440, 0x2460)))
  print_codes('Ideographic Description Characters',
                                  map(chr, range(0x2ff0, 0x3000)))
  print_codes('Halfwidth and Fullwidth Forms',
                                  map(chr, range(0xff00, 0xfff0)))
  print_codes('Alchemical Symbols',
                                  map(chr, range(0x1f700, 0x1f780)))

  print_codes('Miscellaneous Symbols and Pictographs',
                                  map(chr, range(0x1f300, 0x1f600)), span=26)
  print_codes('Supplemental Symbols and Pictographs',
                                  map(chr, range(0x1f900, 0x1fa00)), span=26)
  print_codes('Emoticons',
                                  map(chr, range(0x1f600, 0x1f650)), span=26)

  print_codes('Useful',           map(chr, [
    8227, 394263, 5665, 10003, 10007, 8210, 8211, 8212, 8213, 11834, 11835, 12291, 167, 182, 183, 8216, 8217, 8218, 8220, 8221, 8222, 8224, 8225, 8226, 8230, 8253, 8258, 8592, 8593, 8594, 8595, 9744, 9745, 9746, 9755, 9758, 9884, 9733, 9734, 9633, 9956, 9166, 9003, 9251, 160, 173, 8203, 8204, 169, 174, 8482, 8730, 8731, 8732, 177, 8723, 8242, 8243, 8244, 8719, 8721, 8722, 215, 8901, 8725, 8733, 8739, 8740, 8771, 8772, 8773, 8774, 8775, 8776, 8777, 8796, 8797, 8799, 8800, 8801, 8804, 8805, 8810, 8811, 8734, 8706, 8747, 8748, 8749, 10764, 8750, 8751, 8752, 8753, 8754, 8755, 8711, 8834, 8835, 8838, 8839, 8836, 8745, 8746, 8712, 8714, 8713, 8715, 8717, 8716, 8709, 8736, 8737, 8738, 10178, 8735, 172, 8743, 8744, 8718, 8756, 8757, 8704, 8707, 8708, 8304, 185, 178, 179, 8308, 8309, 8310, 8311, 8312, 8313, 8320, 8321, 8322, 8323, 8324, 8325, 8326, 8327, 8328, 8329, 189, 8531, 8532, 188, 190, 8533, 8534, 8535, 8536, 8537, 8538, 8528, 8539, 8540, 8541, 8542, 8529, 8530, 8543, 8260, 8942, 8943, 8944, 8945, 10216, 10217, 176, 952, 956, 960, 8450, 8461, 8467, 8469, 8473, 8474, 8477, 8484, 120134, 9729, 9735, 9730, 9748, 9736, 9737, 9788, 9728, 9789, 9790, 9791, 9792, 9793, 9794, 9795, 9796, 9954, 9797, 9798, 9799, 9907, 9911, 9800, 9811, 9803, 9924, 9925, 9926, 9927, 9928, 10052, 127744, 127745, 127746, 127756, 127761, 127763, 127765, 127767, 127769, 127776, 295, 411, 936, 955, 957, 968, 969, 8652, 9005, 937, 8452, 65098, 65102, 394263, 5665, 9211, 9212, 9213, 11096, 9214, 3647, 8383, 162, 164, 36, 8364, 8372, 8377, 8356, 8362, 8369, 8381, 163, 8378, 8361, 165, 8240, 8241, 128176, 128177, 128179, 128200, 128201, 9833, 9834, 9835, 9836, 9837, 9838, 9839, 119046, 119047, 119056, 119068, 119070, 119071, 119072, 119073, 119074, 119075, 119076, 119077, 119078, 119248, 119249, 119082, 119083, 119092, 119099, 119100, 119101, 119134, 119137, 119138, 119139, 119140, 119186, 119187, 127925, 127926, 127928, 127931, 129685, 9749, 9982, 127813, 127818, 127823, 129361, 127828, 127829, 127833, 127838, 127843, 127848, 127853, 127858, 127863, 127868, 127827, 9760, 9761, 9762, 9763, 9764, 9774, 9775, 9855, 9877, 9888, 9889, 9936, 9960, 128137, 128138, 9812, 9813, 9814, 9815, 9816, 9817, 9818, 9819, 9820, 9821, 9822, 9823, 9824, 9825, 9826, 9827, 9828, 9829, 9830, 9831, 9917, 9918, 9975, 127918, 127923, 127933, 127936, 127939, 127942, 127945, 127992, 9216, 9222, 9224, 9225, 9226, 9229, 9237, 9600, 9604, 9612, 9616, 9651, 8895, 11036, 9826, 9645, 11040, 11041, 9675, 11053, 9194, 9193, 9195, 9196, 9197, 9198, 9658, 9668, 9650, 9660, 9651, 9661, 9673, 9678, 9986, 9988, 9989, 10003, 10004, 10005, 10006, 10007, 10008, 10060, 128077, 128078, 8227,
  ]))
  print_codes('ASCI ++ ',         map(chr, range(0x0, 0xff)))

  print()


def rgb_from_hsv(h, s, v):
  c = float(s * v)
  m = float(v - c)
  h = h / 60.
  x = c * (1. - abs((h % 2) - 1.))
  r, g, b = {
    0: (c, x, 0),
    1: (x, c, 0),
    2: (0, c, x),
    3: (0, x, c),
    4: (x, 0, c),
    5: (c, 0, x),
  }[int(h) % 6]
  return r + m, g + m, b + m

assert rgb_from_hsv(0, 0, 0) == (0, 0, 0)
assert rgb_from_hsv(0, 0, 1) == (1, 1, 1)
assert rgb_from_hsv(60, 1, .75) == (.75, .75, 0)


# https://en.wikipedia.org/wiki/ANSI_escape_code#Description
# https://gist.github.com/ConnerWill/d4b6c776b509add763e17f9f113fd25b
class ANSI:
  ESC = '\x1b'    # also known as '\033',  '\e',  '^['
  CSI = '['       # control sequence introducer
  OSC = ']'       # operating system command

  # CSI codes
  class CONTROL:
    SGR         = 'm'   # select graphical representation
    MOUSE_ON    = 'h'
    MOUSE_OFF   = 'l'
    RESET       = 'c'

  class GRAPHICS(IntEnum):
    RESET   = 0
    BOLD    = 1
    DIM     = 2
    ITALIC  = 3
    UNDERLINE=4
    BLINK   = 5
    BLINK2  = 6
    REVERSE = 7
    BLACK   = 8
    STRIKE  = 9

  class COLOR(IntEnum):
    FG8     = 30
    BG8     = 40
    BRIGHT8 = 60
    FG      = 38
    BG      = 48
    CS256   = 5
    CS24B   = 2

  class COLOR8(IntEnum):
    BLACK   = 0
    RED     = 1
    GREEN   = 2
    YELLOW  = 3
    BLUE    = 4
    MAGENTA = 5
    CYAN    = 6
    WHITE   = 7
    DEFAULT = 9

  class COLOR256(IntEnum):
    BLACK   = 16
    MAX_VAL = 5
    GREY    = 232
    GRAY    = GREY

  class MOUSE(IntEnum):
    X10               = 9       # doesn't work in mobaxterm
    VT200             = 1000    # button clicks
    VT200_HIGHLIGHT   = 1001    # doesn't work in mobaxterm
    BTN_EVENT         = 1002    # button clicks plus motion when button down
    ANY_EVENT         = 1003    # doesn't work in mobaxterm
    FOCUS_EVENT       = 1004    # doesn't work in mobaxterm

    ALTERNATE_SCROLL  = 1007    # ??
    EXT_MODE          = 1005
    SGR_EXT_MODE      = 1006    # different encoding for larger coordinates
    URXVT_EXT_MODE    = 1015
    PIXEL_POSITION    = 1016

  CSI_RE = re.compile('\001?\033\\[((?:\\d|;)*)([a-zA-Z])\002?')
  OSC_RE = re.compile('\001?\033\\]([^\a]*)(\a)\002?')
  @staticmethod
  def strip(x):
    x = re.sub(ANSI.CSI_RE, '', x)
    x = re.sub(ANSI.OSC_RE, '', x)
    return x

  @staticmethod
  def graphics(x):
    return f'{ANSI.ESC}{ANSI.CSI}{x}{ANSI.CONTROL.SGR}'

  @staticmethod
  def color_fg8(x):
    return ANSI.graphics(ANSI.COLOR.FG8 + x)

  @staticmethod
  def color_bg8(x):
    return ANSI.graphics(ANSI.COLOR.BG8 + x)

  @staticmethod
  def color_256(x):
    # each channel [0, 6]
    if isinstance(x, tuple):
      r, g, b = x
      if isinstance(b, float):
        r = int(r * ANSI.COLOR256.MAX_VAL)
        g = int(g * ANSI.COLOR256.MAX_VAL)
        b = int(b * ANSI.COLOR256.MAX_VAL)
      x = 16 + 36 * r + 6 * g + b
    return f'{ANSI.COLOR.CS256};{x}'

  def color_fg256(x):
    x = ANSI.color_256(x)
    return ANSI.graphics(f'{ANSI.COLOR.FG};{x}')

  @staticmethod
  def color_bg256(x):
    x = ANSI.color_256(x)
    return ANSI.graphics(f'{ANSI.COLOR.BG};{x}')

  @staticmethod
  def color_fg24b(x):
    r, g, b = x
    return ANSI.graphics(f'{ANSI.COLOR.FG};{ANSI.COLOR.CS24B};{r};{g};{b}')

  @staticmethod
  def color_bg24b(x):
    r, g, b = x
    return ANSI.graphics(f'{ANSI.COLOR.BG};{ANSI.COLOR.CS24B};{r};{g};{b}')


  @staticmethod
  def graphics_reset():
    return ANSI.graphics(ANSI.GRAPHICS.RESET)

  @staticmethod
  def mouse(x):
    return f'{ANSI.ESC}{ANSI.CSI}?{x}{ANSI.CONTROL.MOUSE_ON}'

  def mouse_off(x):
    return f'{ANSI.ESC}{ANSI.CSI}?{x}{ANSI.CONTROL.MOUSE_OFF}'


assert ANSI.strip('x') == 'x'

def t_colors():
  print('** Color support ' + '*' * 40)
  colorama.init()
  bpx = '⬛'
  box = '▀▄'
  # box = 'AA'


  print('8 Color FG:    ', end=' ')
  for color in ANSI.COLOR8:
    print(f'{ANSI.color_fg8(color.value)} {color.name:^8} {ANSI.graphics_reset()}', end=' ')

  print('\n8 Color BG:    ', end=' ')
  for color in ANSI.COLOR8:
    print(f'{ANSI.color_bg8(color.value)} {color.name:^8} {ANSI.graphics_reset()}', end=' ')

  print('\n8 Color BRIGHT:', end=' ')
  for color in ANSI.COLOR8:
    print(f'{ANSI.color_fg8(ANSI.COLOR.BRIGHT8 + color.value)} {color.name:^8} {ANSI.graphics_reset()}', end=' ')

  print('\n8 Color BOLD:  ', end=' ')
  for color in ANSI.COLOR8:
    print(f'{ANSI.graphics(ANSI.GRAPHICS.BOLD)}{ANSI.color_fg8(color.value)} {color.name:^8} {ANSI.graphics_reset()}', end=' ')

  print('\n8 Color DIM:   ', end=' ')
  for color in ANSI.COLOR8:
    print(f'{ANSI.graphics(ANSI.GRAPHICS.DIM)}{ANSI.color_fg8(color.value)} {color.name:^8} {ANSI.graphics_reset()}', end=' ')

  print('\nStyles:\n        ', end=' ')
  for style in ANSI.GRAPHICS:
      print(f'{ANSI.graphics(style.value)} {style.name:^8} {ANSI.graphics_reset()}', end=' ')

  print('\n 8x8 Color:')
  for fg in ANSI.COLOR8:
    for bg in ANSI.COLOR8:
      print(f'{ANSI.color_fg8(fg.value)}{ANSI.color_bg8(bg.value)}{box}{ANSI.graphics_reset()}', end='')
    print()

  print('\n256 Color:')
  print('{:17s}{:17s}{:17s}{}'.format('Red/Green', 'Green/Blue', 'Blue/Red', 'Grey'))
  for y in range(6):
    for x in range(6): # R/G
      r, g, b = y, x, 0
      c = 16 + 36 * r + 6 * g + b
      print(f'{ANSI.color_fg256(c)}{box}{ANSI.graphics_reset()}', end='')
    print('    ', end=' ')
    for x in range(6): # G/B
      r, g, b = 0, y, x
      c = 16 + 36 * r + 6 * g + b
      print(f'{ANSI.color_fg256(c)}{box}{ANSI.graphics_reset()}', end='')
    print('    ', end=' ')
    for x in range(6): # G/B
      r, g, b = x, 0, y
      c = 16 + 36 * r + 6 * g + b
      print(f'{ANSI.color_fg256(c)}{box}{ANSI.graphics_reset()}', end='')
    print('    ', end=' ')
    for x in range(4): # Grey
      c = 232 + y * 4 + x
      print(f'{ANSI.color_fg256(c)}{box}{ANSI.graphics_reset()}', end='')
    print()

  # HSV
  print('\nHSV:')
  S = 10
  H = 70
  for s in range(S):
    for h in range(H):
      r = rgb_from_hsv(h * 360 / H, s / S, 1)
      # print(r)
      print(f'{ANSI.color_fg256(r)}{box}{ANSI.graphics_reset()}', end='')
    print()

  print('\n24-Bit Color:')
  X = 16
  for y in range(X):
    for x in range(X):
      r, g, b = y * X + x, 0, 0
      print(f'{ANSI.color_fg24b((r,g,b))}{box}{ANSI.graphics_reset()}', end='')
    print('    ', end='')
    for x in range(X):
      r, g, b = 0, y *X + x, 0
      print(f'{ANSI.color_fg24b((r,g,b))}{box}{ANSI.graphics_reset()}', end='')
    print('    ', end='')
    for x in range(X):
      r, g, b = 0, 0, y * X + x
      print(f'{ANSI.color_fg24b((r,g,b))}{box}{ANSI.graphics_reset()}', end='')
    print('    ', end='')
    for x in range(X):
      r = g = b = y * X + x
      print(f'{ANSI.color_fg24b((r,g,b))}{box}{ANSI.graphics_reset()}', end='')
    print()


def t_color256():
  print('** 256 Colors ' + '*' * 40)
  colorama.init()
  FW = ANSI.color_fg256(255)
  BW = ANSI.color_bg256(255)
  FB = ANSI.color_fg256(0)
  BB = ANSI.color_bg256(0)
  RS = ANSI.graphics_reset()
  N = 6
  for i in range(N):
    for j in range(N):
      for k in range(N):
        c = 16
        c += i * N**2
        c += k * N**1
        c += j * N**0
        print((
          f'{BB}{ANSI.color_fg256(c)} {c:3d}{RS}'
          f'{FW}{ANSI.color_bg256(c)} {c:=3d} {RS}'
          f'{BW}{ANSI.color_fg256(c)} {c:<3d} {RS}  '
          ), end='')
      # if (j % 2) == 1:
      print()



def t_mouse():
    # https://invisible-island.net/xterm/ctlseqs/ctlseqs.html#h2-Mouse-Tracking


  def getch():
    # TODO make windows version
    import tty, termios
    orig_settings = termios.tcgetattr(sys.stdin)
    tty.setraw(sys.stdin)
    c = os.read(sys.stdin.fileno(), 128)
    # c = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)
    return c

  def parse_mouse_event(b):
    return b[0] == 0x1b

  mode = ANSI.MOUSE.BTN_EVENT
  mode = ANSI.MOUSE.VT200_HIGHLIGHT
  try:
    # enable mouse tracking
    print(ANSI.mouse(mode), end='', flush=True)
    print(ANSI.mouse(ANSI.MOUSE.SGR_EXT_MODE), end='', flush=True)

    while 1:
      print('Press a key: ([q] to quit)', end=' ', flush=True)
      c = getch()
      print(f'Got input: {c!r}\n')
      if b'q' in c:
          break
      if parse_mouse_event(c):
          # handle highlight tracking?
          print(f'{ANSI.ESC}{ANSI.CSI}1;10;10;20;20T')

  finally:
    # reset mouse tracking
    print(ANSI.mouse_off(mode), end='', flush=True)
    print(ANSI.mouse_off(ANSI.MOUSE.SGR_EXT_MODE), end='', flush=True)


def main():
  parser = argparse.ArgumentParser(
      formatter_class=argparse.RawTextHelpFormatter,
      description=__doc__,
  )
  tests = [f[2:] for f in globals() if f.startswith('t_')]
  parser.add_argument('tests',
      nargs='*',
      choices=tests,
      default=tests,
  )
  args = parser.parse_args()

  for i in args.tests:
    globals()[f't_{i}']()

if __name__ == '__main__':
  main()
