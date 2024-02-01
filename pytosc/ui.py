from colorama import Style
from io import StringIO


def cprint(fore, *args, **kwargs):
    file = kwargs.pop("file", None)
    with StringIO() as stream:
        print(*args, **kwargs, file=stream)
        print(fore + stream.getvalue() + Style.RESET_ALL, end="", file=file)
