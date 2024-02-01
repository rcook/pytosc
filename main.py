from argparse import ArgumentParser, BooleanOptionalAction
from colorama import Fore
from pytosc.app import App
from pytosc.error import UserError
from pytosc.path import file_path
from pytosc.ui import cprint
from pytosc.zlib import is_zlib_file
import colorama
import os
import sys
import xml.etree.ElementTree as ET
import zlib


TOSC_EXT = ".tosc"
XML_EXT = ".xml"
XML_INDENT = "  "


def check_output_file(output_path, force_overwrite):
    if not force_overwrite and os.path.exists(output_path):
        raise UserError(
            f"Output file {output_path} already exists: pass --force to overwrite")


def do_extract_xml(app, input_path, output_path, pretty_xml, force_overwrite):
    if output_path is None:
        output_path = input_path + XML_EXT

    check_output_file(
        output_path=output_path,
        force_overwrite=force_overwrite)

    if not is_zlib_file(input_path):
        raise UserError(f"Input file {input_path} is not a zlib stream")

    with open(input_path, "rb") as f:
        data = zlib.decompress(f.read())

    if pretty_xml:
        tree = ET.fromstring(data)
        ET.indent(tree, space=XML_INDENT, level=0)
        data = ET.tostring(tree, encoding="utf-8")

    with open(output_path, "wb") as f:
        f.write(data)


def do_make_tosc(app, input_path, output_path, shrink_xml, force_overwrite):
    if output_path is None:
        if input_path.endswith(TOSC_EXT + XML_EXT):
            output_path = input_path[0:-len(XML_EXT)]
        elif input_path.endswith(XML_EXT):
            output_path = input_path[0:-len(XML_EXT)] + TOSC_EXT
        else:
            output_path = input_path + TOSC_EXT

    check_output_file(
        output_path=output_path,
        force_overwrite=force_overwrite)

    if is_zlib_file(input_path):
        raise UserError(f"Input file {input_path} is already a zlib stream")

    with open(input_path, "rb") as f:
        data = f.read()

    if shrink_xml:
        tree = ET.fromstring(data)
        ET.indent(tree, space="", level=0)
        data = ET.tostring(tree, encoding="utf-8")

    with open(output_path, "wb") as f:
        f.write(zlib.compress(data))


def main(cwd, argv):
    def file_path_type(s):
        return file_path(cwd, s)

    def add_input_path_arg(p, **kwargs):
        p.add_argument(
            "input_path",
            **{
                "type": file_path_type,
                **kwargs
            })

    def add_output_path_arg(p, **kwargs):
        p.add_argument(
            "--output-path",
            "-o",
            **{
                "dest": "output_path",
                "type": file_path_type,
                "required": False,
                **kwargs
            })

    def add_force_overwrite_arg(p, **kwargs):
        p.add_argument(
            "--force",
            "-f",
            **{
                "dest": "force_overwrite",
                "action": BooleanOptionalAction,
                "default": False,
                "required": False,
                "help": "force overwrite of output file if it already exists",
                **kwargs
            })

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
            output_path=args.output_path,
            pretty_xml=args.pretty_xml,
            force_overwrite=args.force_overwrite))
    add_input_path_arg(p, help="path to input .tosc file")
    add_output_path_arg(p, help="path to output .xml file")
    add_force_overwrite_arg(p)
    p.add_argument(
        "--pretty-xml",
        "-p",
        dest="pretty_xml",
        action=BooleanOptionalAction,
        default=False,
        required=False,
        help="pretty-print XML output")

    p = subparsers.add_parser("make-tosc")
    p.set_defaults(
        func=lambda app, args:
        do_make_tosc(
            app=app,
            input_path=args.input_path,
            output_path=args.output_path,
            shrink_xml=args.shrink_xml,
            force_overwrite=args.force_overwrite))
    add_input_path_arg(p, help="path to input .xml file")
    add_output_path_arg(p, help="path to output .tosc file")
    add_force_overwrite_arg(p)
    p.add_argument(
        "--shrink-xml",
        "-s",
        dest="shrink_xml",
        action=BooleanOptionalAction,
        default=False,
        required=False,
        help="shrink XML before compressing")

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
