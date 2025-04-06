#! /usr/bin/env python3

# Top level application for dexter (Double-entry Expense Tracker)

import argparse
import calendar
import logging
from pathlib import Path
import sys

from .config import Config
from .console import console
from .DB import DB
from .util import setup_logging, parse_date, date_range

from .io import import_records, export_records, add_records
from .pair import pair_entries
from .report import print_report
from .select import select_transactions

# Functions for commands (will be moved to modules)

def review_transactions(args):
    print('review_transactions')

def reconcile_statements(args):
    print('reconcile_statements')

def generate_report(args):
    print('generate_report')


def init_cli():
    """
    Use argparse to create the command line API, initialize the logger
    to print status messages on the console.

    Returns:
        a Namespace object with values of the command line arguments. 
    """
    months = [ m[:3].lower() for m in calendar.month_name[1:] ]

    parser = argparse.ArgumentParser()
    parser.add_argument('--dbname', metavar='X', help='database name', default='dexter')
    parser.add_argument('--log', metavar='X', choices=['quiet','info','debug'], default='info')
    parser.add_argument('--preview', action='store_true')
    parser.add_argument('--config', metavar='F', help='TOML file with configuration settings')
    
    subparsers = parser.add_subparsers(title='subcommands', dest='command')

    import_recs_parser = subparsers.add_parser('import', help='load documents into a database')
    import_recs_parser.add_argument('--file', metavar='F', help='name of file with records to import',default='dexter.docs')
    import_recs_parser.add_argument('--format', metavar='F', choices=['docs', 'journal'], help='file format')
    import_recs_parser.add_argument('--regexp', metavar='F', help='CSV file with regular expressions') 
    import_recs_parser.set_defaults(dispatch=import_records)

    export_recs_parser = subparsers.add_parser('export', help='export a database to a text file')
    export_recs_parser.add_argument('--file', metavar='F', help='name of output file',default='dexter.docs')
    export_recs_parser.add_argument('--force', action='store_true', help='overwrite existing file')
    export_recs_parser.set_defaults(dispatch=export_records)

    add_recs_parser = subparsers.add_parser('add', help='add new records from CSV files')
    add_recs_parser.add_argument('files', metavar='F', nargs='+', type=Path, help='name(s) of CSV file(s) with records to add')
    add_recs_parser.add_argument('--account', metavar='A', help='process only this account')
    add_recs_parser.add_argument('--start_date', metavar='D', type=parse_date, help='starting date')
    add_recs_parser.add_argument('--end_date', metavar='D', type=parse_date, help='ending date')
    add_recs_parser.add_argument('--month', metavar='D', choices=months, help='add records only for this month')
    add_recs_parser.set_defaults(dispatch=add_records)

    pair_parser = subparsers.add_parser('pair', help='make transactions from matching entries')
    pair_parser.add_argument('--repl', action='store_true', help='use a REPL to display and edit entries')
    pair_parser.set_defaults(dispatch=pair_entries)

    review_parser = subparsers.add_parser('review', help='review transactions')
    review_parser.set_defaults(dispatch=review_transactions)

    reconcile_parser = subparsers.add_parser('reconcile', help='reconcile statements')
    reconcile_parser.set_defaults(dispatch=reconcile_statements)

    report_parser = subparsers.add_parser('report', help='generate a report')
    report_parser.add_argument('content', metavar='X', choices=['balance', 'expense', 'transaction', 'audit'], help='file format')
    report_parser.set_defaults(dispatch=print_report)
    report_parser.add_argument('--csv', action='store_true', help='print in CSV format, with a header line')
    report_parser.add_argument('--compact', action='store_true', help='print each transaction on a single line')
    report_parser.add_argument('--start_date', metavar='D', type=parse_date, help='starting date')
    report_parser.add_argument('--end_date', metavar='D', type=parse_date, help='ending date')
    report_parser.add_argument('--month', metavar='M', choices=months, help='define start and end dates based on month name')
    report_parser.add_argument('--category', metavar='C', choices=['income','asset','liability','expense'], help='include accounts in this category only')

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

    setup_logging(args.log)
    logging.debug('command line arguments:')
    for name, val in vars(args).items():
        if val is not None:
            logging.debug(f'  --{name} {val}')

    return args 

def main():
    """
    Top level entry point
    """
    args = init_cli()
    try:
        Config.init(args.config)
        DB.open(args.dbname)
        args.dispatch(args)
    except Exception as err:
        console.print_exception(show_locals=True)
