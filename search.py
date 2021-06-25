from argparse import ArgumentParser
from search import main


def get_parser():
    parser = ArgumentParser(
        description="""The script is designed to process logs.
        Searches for objects based on certain criteria.
        You can set specific conditions for the selection of values."""
    )
    parser.add_argument(
        "-C",
        "--context",
        choices=["full", "context", "null"],
        default="null",
        metavar="",
        help="""Filter lines containing 'content'.
        'context': with contetx,
        'null': without context,
        'full': both.
        Default: 'null'.""",
    )
    parser.add_argument(
        "-T",
        "--time",
        type=int,
        default=600,
        metavar="",
        help="""Determine the time in the range of selection of values. In seconds. Default: 600.""",
    )
    parser.add_argument(
        "-P",
        "--path",
        type=str,
        metavar="",
        help="""Path to log file or directory with log files.""",
    )
    parser.add_argument(
        "-L",
        "--limit",
        type=int,
        required=False,
        metavar="",
        help="""How many lines of result to display. Do not specify to display the entire list.""",
    )
    parser.add_argument(
        "-A",
        "--ip-address",
        nargs="+",
        metavar="",
        help="""Create a list of ip addresses, filtering by these addresses will be carried out.""",
    )
    parser.add_argument(
        "-B",
        "--black-list",
        action="store_true",
        help="""Set the checkbox to filter by excluding ip addresses.""",
    )
    parser.add_argument(
        "-S",
        "--save",
        action="store_true",
        help="""set this flag to save data to the sqlite database.""",
    )
    parser.add_argument(
        "-V",
        "--verbose",
        action="store_true",
        help="""display the received data.""",
    )

    return parser.parse_args()


if __name__ == "__main__":
    parser = get_parser()
    main(
        ip_address=parser.ip_address,
        black_list=parser.black_list,
        context=parser.context,
        verbose=parser.verbose,
        limit=parser.limit,
        time=parser.time,
        save=parser.save,
        path=parser.path,
    )
