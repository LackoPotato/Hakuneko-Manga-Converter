__author__ = "LackoPotatoes :3"
__version__ = "v0.8.0"
__license__ = "UNLICENSE"
import string

start = "\033["
_escaped_start = "\\033["


class modifier:
    def __init__(self, code: int):
        self.code = code

    def get_code(self) -> str:
        return f"{self.code}"

    def __str__(self) -> str:
        return f"{start}{self.get_code()}m"

    def __repr__(self) -> str:
        return f"{_escaped_start}{self.get_code()}m"


clear = modifier(0)


class font:
    bold = modifier(1)
    faint = modifier(2)
    italics = modifier(3)
    underline = modifier(4)
    blink_slow = modifier(5)
    blink_fast = modifier(6)
    swap = modifier(7)
    conceal = modifier(8)
    crossed = modifier(9)
    fraktur = modifier(20)
    normal = modifier(22)

    framed = modifier(51)
    encircled = modifier(52)
    overlined = modifier(53)


class disable:
    bold = modifier(21)
    italic_frankfurt = modifier(23)
    underline = modifier(24)
    blink = modifier(25)
    swap = modifier(26)
    conceal = modifier(27)
    crossed = modifier(28)
    encircled_framed = modifier(54)
    overlined = modifier(55)


class fore16:
    black = modifier(30)
    red = modifier(31)
    green = modifier(32)
    yellow = modifier(33)
    blue = modifier(34)
    magenta = modifier(35)
    cyan = modifier(36)
    white = modifier(37)

    class bright:
        black = modifier(90)
        red = modifier(91)
        green = modifier(92)
        yellow = modifier(93)
        blue = modifier(94)
        magenta = modifier(95)
        cyan = modifier(96)
        white = modifier(97)


foreground = modifier(38)
foreground_default = modifier(39)


class back16:
    black = modifier(40)
    red = modifier(41)
    green = modifier(42)
    yellow = modifier(43)
    blue = modifier(44)
    magenta = modifier(45)
    cyan = modifier(46)
    white = modifier(47)

    class bright:
        black = modifier(100)
        red = modifier(101)
        green = modifier(102)
        yellow = modifier(103)
        blue = modifier(104)
        magenta = modifier(105)
        cyan = modifier(106)
        white = modifier(107)


background = modifier(48)
background_default = modifier(49)


class ideogram:
    underline = modifier(60)
    double_underline = modifier(61)
    overline = modifier(62)
    stress_mark = modifier(64)
    off = modifier(65)


class color256:
    def __init__(self, r: int, g: int, b: int, foreground: bool = True):
        if 0 > r and 0 > g and 0 > b:
            raise Exception(
                f"color256: arguments r,g,b is less than 0 (0 ≤ r, g, b ≤ 255), ({r},{g},{b}) was given"
            )
        if r > 255 or g > 255 or b > 255:
            raise Exception(
                f"color256: arguments r,g,b is more than 5 (0 ≤ r, g, b ≤ 255), ({r},{g},{b}) was given"
            )
        if not isinstance(foreground, bool):
            raise TypeError("Argument foreground is not of type bool")

        self.r = r
        self.g = g
        self.b = b
        self.foreground = foreground

    def __eq__(self, val):
        return (
            isinstance(val, color256)
            and self.r == val.r
            and self.g == val.g
            and self.b == val.b
            and self.foreground == val.foreground
        )

    def get_code(self) -> str:
        return f"{foreground.get_code() if self.foreground else background.get_code()};2;{self.r};{self.g};{self.b}"

    def __str__(self) -> str:
        return f"{start}{self.get_code()}m"

    def __repr__(self) -> str:
        return f"color8({self.r},{self.g},{self.b} code=[\\033[{self.get_code()};m])"

    def __hash__(self):
        return hash((self.r, self.g, self.b, self.foreground))


class color5:
    def __init__(self, r: int, g: int, b: int, foreground: bool = True):
        if 0 > r and 0 > g and 0 > b:
            raise Exception(
                f"color5: arguments r,g,b is less than 0 (0 ≤ r, g, b ≤ 5), ({r},{g},{b}) was given"
            )
        if r > 255 or g > 255 or b > 255:
            raise Exception(
                f"color5: arguments r,g,b is more than 5 (0 ≤ r, g, b ≤ 5), ({r},{g},{b}) was given"
            )
        if not isinstance(foreground, bool):
            raise TypeError("Argument text_color is not of type bool")
        self.r = r
        self.g = g
        self.b = b
        self.foreground = foreground

    def __eq__(self, val):
        return (
            isinstance(val, color5)
            and self.r == val.r
            and self.g == val.g
            and self.b == val.b
            and self.foreground == val.foreground
        )

    def get_code(self) -> str:
        return f"{foreground.get_code() if self.foreground else background.get_code()};5;{16 + 36 * self.r + 6 * self.g + self.b}"

    def __str__(self) -> str:
        return f"{start}{self.get_code()};m"

    def __repr__(self) -> str:
        return f"color5({self.r},{self.g},{self.b} code=[\\033[{self.get_code()}m])"

    def __hash__(self):
        return hash((self.r, self.g, self.b, self.foreground))


def html(code: str, foreground: bool = True) -> color256:
    if not bool(len(code)):
        raise Exception(
            f"Length of argument [code] has to be <0, code is len({len(code)}) instead"
        )
    code = code.strip(string.whitespace).lstrip(string.whitespace)

    if code[0] == "#":
        code = code[1:]

    if len(code) == 3 and _ishex(code[1:]):
        r: int = int(code[0], 16) * 17
        g: int = int(code[1], 16) * 17
        b: int = int(code[2], 16) * 17
        return color256(r, g, b, foreground)

    if not _ishex(code):
        raise Exception(f"Code has to be valid hexadecimal ({code})")
    r: int = int(code[0:2], 16)
    g: int = int(code[2:4], 16)
    b: int = int(code[4:6], 16)
    return color256(r, g, b, foreground)


def _ishex(test_string: str) -> bool:
    for chr in test_string:
        if chr not in string.hexdigits:
            return False
    return True


def format(*options: int | color5 | color256 | modifier) -> str:
    return tformat(options)  # type: ignore


def tformat(options: tuple[int | color5 | color256 | modifier]) -> str:
    string = start
    for option in options:
        if isinstance(option, (color5, color256, modifier)):
            string += f"{option.get_code()};"
        else:
            string += f"{option};"
    return f"{string}m"


def qformat(string: str, *options: int | color5 | color256 | modifier) -> str:
    return f"{tformat(options)}{string}{clear}"  # type: ignore
