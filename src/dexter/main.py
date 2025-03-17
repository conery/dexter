#! /usr/bin/env python3

# Top level application for dexter (Double-entry Expense Tracker)

import argparse
import calendar
import logging
from pathlib import Path
import sys

from .util import setup_logging, parse_date, date_range
from .DB import DB

from .io import import_records, export_records
from .select import select_transactions

# Functions for commands (will be moved to modules)

def parse_csv_files(args):
    print('import_transactions')

def parse_statements(args):
    print('parse_statements')

def review_transactions(args):
    print('review_transactions')

def reconcile_statements(args):
    print('reconcile_statements')

def generate_report(args):
    print('generate_report')


def init_cli():
    """
    Use argparse to create the command line API.

    Returns:
        a Namespace object with values of the command line arguments. 
    """
    months = [ m[:3].lower() for m in calendar.month_name[1:] ]

    parser = argparse.ArgumentParser()
    parser.add_argument('--dbname', metavar='X', help='database name', default='dexter')
    parser.add_argument('--log', metavar='X', choices=['quiet','info','debug'], default='info')
    
    subparsers = parser.add_subparsers(title='subcommands', dest='command')

    import_parser = subparsers.add_parser('import', help='load documents into a database')
    import_parser.add_argument('--file', metavar='F', help='name of file with records to import',default='dexter.json')
    import_parser.add_argument('--format', metavar='F', choices=['json', 'journal'], help='file format', default='json')
    import_parser.set_defaults(dispatch=import_records)

    export_parser = subparsers.add_parser('export', help='export a database to a text file')
    export_parser.add_argument('--file', metavar='F', help='name of output file',default='dexter.json')
    export_parser.add_argument('--format', metavar='F', choices=['json', 'journal'], help='file format', default='json')
    export_parser.set_defaults(dispatch=export_records)

    collect_parser = subparsers.add_parser('collect', help='import transactions from CSV files')
    collect_parser.set_defaults(dispatch=parse_csv_files)

    statements_parser = subparsers.add_parser('parse', help='import card and bank account statements')
    statements_parser.set_defaults(dispatch=parse_statements)

    review_parser = subparsers.add_parser('review', help='review transactions')
    review_parser.set_defaults(dispatch=review_transactions)

    reconcile_parser = subparsers.add_parser('reconcile', help='reconcile statements')
    reconcile_parser.set_defaults(dispatch=reconcile_statements)

    reports_parser = subparsers.add_parser('report', help='generate a report')
    reports_parser.set_defaults(dispatch=generate_report)

    select_parser = subparsers.add_parser('select', help='select transactions')
    select_parser.add_argument('--entry', action='store_true', help='seach individual debit or credit entries')
    select_parser.add_argument('--date', metavar='D', type=parse_date, help='transaction date')
    select_parser.add_argument('--start_date', metavar='D', type=parse_date, help='starting date')
    select_parser.add_argument('--end_date', metavar='D', type=parse_date, help='ending date')
    select_parser.add_argument('--month', metavar='M', choices=months, help='define start and end dates based on month name')
    select_parser.add_argument('--credit', metavar='A', help='credit account name (transaction)')
    select_parser.add_argument('--debit', metavar='A', help='debit account name (transaction)')
    select_parser.add_argument('--account', metavar='A', help='account name (entry)')
    select_parser.add_argument('--column', metavar='C', choices=['credit','debit'], help='entry type (entry)')
    select_parser.add_argument('--description', metavar='X', help='descriptions pattern')
    # select_parser.add_argument('--original', metavar='X', help='original description pattern')
    select_parser.add_argument('--comment', metavar='X', help='comment pattern (transaction)')
    select_parser.add_argument('--tag', metavar='X', help='tag pattern (transaction)')
    select_parser.add_argument('--amount', metavar='N', type=float, help='amount')
    select_parser.add_argument('--min_amount', metavar='N', type=float, help='minimum amount')
    select_parser.add_argument('--max_amount', metavar='N', type=float, help='maximum amount')
    select_parser.add_argument('--csv', action='store_true', help='print in CSV format, with a header line')
    select_parser.add_argument('--total', action='store_true', help='print total amount of selected transactions')
    select_parser.add_argument('--update', metavar='F V', nargs=2, help='update fields')
    select_parser.set_defaults(dispatch=select_transactions)

    if len(sys.argv) == 1:
        parser.print_usage()
        exit(1)

    args = parser.parse_args()

    if args.command is None:
        print('command required')
        parser.print_usage()
        exit(1)

    if 'month' in vars(args):
        if m := args.month:
            ds, de = date_range(m)
            args.start_date = ds
            args.end_date = de
    
    return args 

def main():
    """
    Top level entry point
    """
    args = init_cli()
    setup_logging(args.log)
    logging.debug('command line arguments:')
    for name, val in vars(args).items():
        if val is not None:
            logging.debug(f'  --{name} {val}')
    try:
        DB.open(args.dbname)
        args.dispatch(args)
    except Exception as err:
        logging.error(err)
