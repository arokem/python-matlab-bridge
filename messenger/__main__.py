import sys

from argparse import ArgumentParser

from .make import *

def command_line():
    """
    Manages command line arguments.

    Returns
    -------
    Namespace containing parsed arguments
    """
    parser = ArgumentParser(prog='messenger')

    parser.add_argument(
        "target",
        choices=["matlab", "octave"],
        type=str.lower,
        help="target to be built"
    )
    parser.add_argument(
        "--static",
        action="store_true",
        help="statically link libzmq"
    )
    return parser.parse_args()

def main():
    args   = command_line()
    build  = {
        'matlab': build_matlab,
        'octave': build_octave,
    }
    target = build[args.target]

    return target(static=args.static)

if __name__ == '__main__':
    sys.exit(main())
