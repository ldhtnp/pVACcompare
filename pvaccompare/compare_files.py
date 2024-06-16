import argparse
import sys
from subprocess import call
from scripts import compare_tsv
from scripts import compare_yml

def define_parser():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers()

    #add subcommands
    compare_tsv_parser = subparsers.add_parser(
        "compare-tsv",
        help="Compare tsv files",
        add_help=False
    )
    compare_tsv_parser.set_defaults(func=compare_tsv.main)

    compare_yml_parser = subparsers.add_parser(
        "compare-yml",
        help="Compare yml files",
        add_help=False
    )
    compare_yml_parser.set_defaults(func=compare_yml.main)

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