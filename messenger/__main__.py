from argparse import ArgumentParser

from .make import *

def command_line():
    """
    Manages command line arguments.

    Returns
    =======
    Namespace containing parsed arguments
    """

    parser = ArgumentParser()
    parser.add_argument(
        "target",
        choices=["matlab", "octave"],
        type=str.lower,
        help="target to be built"
    )
    parser.add_argument(
        "--static",
        action="store_true",
        help="staticly link libzmq"
    )
    return parser.parse_args()



def main():
    args = command_line()
    if args.target == "matlab":
        build_matlab(static=args.static)
    elif args.target == "octave":
        build_octave()
    else:
        raise ValueError()

if __name__ == '__main__':
    main()
