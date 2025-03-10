#! /usr/bin/env python3

# Top level application for dexter (Double-entry Expense Tracker)

import argparse
import calendar
import logging
from pathlib import Path
import sys

from .util import setup_logging
from .DB import DB
from .select import select_transactions

# Functions for commands (will be moved to modules)

def initialize_database(args):
    '''
    Top level function for the `init` command.

    Arguments:
        args: Namespace object with command line arguments.
    '''
    p = Path(args.file)
    match p.suffix:
        case '.journal': DB.import_journal(p)
        case _: logging.error(f'init: unknown file extension:{p.suffix}')

def backup_database(args):
    raise RuntimeError("nope")
    print('backup_database')

def import_transactions(args):
    print('import_transactions')

def parse_statements(args):
    print('parse_statements')

def review_transactions(args):
    print('review_transactions')

def reconcile_statements(args):
    print('reconcile_statements')

def generate_report(args):
    print('generate_report')

# Lists used to define choices in command line options, and also later in the program

months = [ m[:3].lower() for m in calendar.month_name[1:] ]

def init_cli():
    """
    Use argparse to create the command line API.

    Returns:
        a Namespace object with values of the command line arguments. 
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('--dbname', metavar='X', help='database name', default='dexter')
    parser.add_argument('--log', metavar='X', choices=['quiet','info','debug'], default='info')
    
    subparsers = parser.add_subparsers(title='subcommands', dest='command')

    init_parser = subparsers.add_parser('init', help='load documents into a database')
    init_parser.add_argument(
        '--file', 
        metavar='F', 
        help='name of file with records to import',
        default='dexter.json'
    )
    init_parser.set_defaults(dispatch=initialize_database)

    backup_parser = subparsers.add_parser('backup', help='export a database to a text file')
    backup_parser.set_defaults(dispatch=backup_database)

    import_parser = subparsers.add_parser('import', help='import transactions from CSV files')
    import_parser.set_defaults(dispatch=import_transactions)

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
    select_parser.add_argument('--date', metavar='D', help='transaction date')
    select_parser.add_argument('--start_date', metavar='D', help='starting date')
    select_parser.add_argument('--end_date', metavar='D', help='ending date')
    select_parser.add_argument('--month', metavar='M', choices=months, help='define start and end dates based on month name')
    select_parser.add_argument('--credit', metavar='A', help='credit account name')
    select_parser.add_argument('--debit', metavar='A', help='debit account name')
    select_parser.add_argument('--account', metavar='A', help='source or destination account name')
    select_parser.add_argument('--description', metavar='X', help='descriptions pattern')
    select_parser.add_argument('--original', metavar='X', help='original description pattern')
    select_parser.add_argument('--comment', metavar='X', help='comment pattern')
    select_parser.add_argument('--tags', metavar='X', help='tag pattern')
    select_parser.add_argument('--amount', metavar='N', type=float, help='transaction amount')
    select_parser.add_argument('--min_amount', metavar='N', type=float, help='minimum transaction amount')
    select_parser.add_argument('--max_amount', metavar='N', type=float, help='maximum transaction amount')
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
    
    return args 

def main():
    """
    Top level entry point
    """
    args = init_cli()
    setup_logging(args.log)
    try:
        DB.open(args.dbname)
        args.dispatch(args)
    except Exception as err:
        logging.error(err)
