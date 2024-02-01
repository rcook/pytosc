from argparse import ArgumentParser
from colorama import Fore
from pytosc.path import file_path
from pytosc.ui import cprint
import colorama
import os
import sys
import zlib


class App:
    pass


class UserError(RuntimeError):
    pass


def do_extract_xml(app, input_path, output_path):
    if output_path is None:
        output_path = input_path + ".xml"

    if os.path.exists(output_path):
        raise UserError(f"Output file {output_path} already exists")

    with open(input_path, "rb") as f:
        data = zlib.decompress(f.read())

    with open(output_path, "wb") as f:
        f.write(data)


def main(cwd, argv):
    def file_path_type(s):
        return file_path(cwd, s)

    parser = ArgumentParser(
        prog="pytosc",
        description="Manipulate TouchOSC layout files")

    subparsers = parser.add_subparsers(required=True)

    p = subparsers.add_parser("extract-xml")
    p.set_defaults(
        func=lambda app, args:
        do_extract_xml(
            app=app,
            input_path=args.input_path,
            output_path=args.output_path))
    p.add_argument(
        "--output-path",
        "-o",
        dest="output_path",
        type=file_path_type,
        required=False,
        help="path to output .xml file")
    p.add_argument(
        "input_path",
        type=file_path_type,
        help="path to input .tosc file")

    args = parser.parse_args(argv)
    app = App()

    try:
        args.func(app=app, args=args)
    except UserError as e:
        cprint(Fore.LIGHTRED_EX, e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    colorama.just_fix_windows_console()
    main(cwd=os.getcwd(), argv=sys.argv[1:])
