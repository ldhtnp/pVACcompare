import argparse
import sys
from subprocess import call
from scripts import run_compare_tsv
from scripts import run_compare_yml
from scripts import run_compare_json

def define_parser():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers()

    compare_tsv_parser = subparsers.add_parser(
        "compare-tsv",
        help="Compare tsv files",
        add_help=False
    )
    compare_tsv_parser.set_defaults(func=run_compare_tsv.main)

    compare_yml_parser = subparsers.add_parser(
        "compare-yml",
        help="Compare yml files",
        add_help=False
    )
    compare_yml_parser.set_defaults(func=run_compare_yml.main)

    compare_json_parser = subparsers.add_parser(
        "compare-json",
        help="Compare json files",
        add_help=False
    )
    compare_json_parser.set_defaults(func=run_compare_json.main)

    return parser

def main():
    parser = define_parser()
    args, unknown = parser.parse_known_args()
    if hasattr(args, 'func'):
        args.func(unknown)
    else:
        parser.print_help()
        print("Error: No command specified")
        sys.exit(-1)


if __name__ == '__main__':
    main()