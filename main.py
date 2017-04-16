import sys
import json
from argparse import ArgumentParser

import kml
import tsv
from extract import all_routes

def main():
    parser = ArgumentParser(description='Scrape downloaded AJAX data for the bus schedule')
    parser.add_argument('data_dir', metavar='DATA_DIR', help='Path of AJAX data (probably matching "data-[0-9]+")')
    parser.add_argument('format', choices=['json', 'kml', 'tsv'], help='Output format')
    tab_spec = parser.add_mutually_exclusive_group(required=True)
    tab_spec.add_argument('--tab-file', '-f',  help='File containing list of names of tabs with schedules in them')
    tab_spec.add_argument('--tab-list', '-l', metavar='TAB_NAME', nargs='*', help='List of names of tabs with schedules in them')
    args = parser.parse_args()

    if args.tab_list is not None:
        tab_names = args.tab_list
    if args.tab_file is not None:
        with open(args.tab_file, 'r') as f:
            tab_names = list(map(lambda x: x.strip(), f))

    routes = all_routes(args.data_dir, tab_names)

    if args.format == 'json':
        json.dump(routes, sys.stdout)
    elif args.format == 'kml':
        kml.dump(routes, sys.stdout)
    elif args.format == 'tsv':
        tsv.dump(routes, sys.stdout)


if __name__ == '__main__':
    main()
