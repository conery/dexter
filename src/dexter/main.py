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

from .io import init_database, save_records, restore_records, import_records, export_records
from .pair import pair_entries
from .report import print_audit_report, print_balance_report, print_expense_report
from .review import review_unpaired
from .select import select_transactions

# Stub functions for commands (will be moved to modules)

def reconcile_statements(args):
    logging.error('reconcile not implemented')

def add_transaction(args):
    logging.error('add not implemented')


def init_cli():
    """
    Use argparse to create the command line API, initialize the logger
    to print status messages on the console.

    Returns:
        a Namespace object with values of the command line arguments. 
    """
    months = [ m[:3].lower() for m in calendar.month_name[1:] ]

    parser = argparse.ArgumentParser()
    parser.add_argument('--dbname', metavar='X', help='database name')
    parser.add_argument('--log', metavar='X', choices=['quiet','info','debug'], default='info')
    parser.add_argument('--preview', action='store_true')
    parser.add_argument('--config', metavar='F', help='TOML file with configuration settings')
    
    subparsers = parser.add_subparsers(title='subcommands', dest='command')

    config_parser = subparsers.add_parser('config', help='print default config file')

    init_db_parser = subparsers.add_parser('init', help='initialize a database')
    init_db_parser.set_defaults(dispatch=init_database)
    init_db_parser.add_argument('--file', metavar='F', help='name of file with account definitions', required=True)
    init_db_parser.add_argument('--format', metavar='C', choices=['journal','csv'], help='file format')

    import_parser = subparsers.add_parser('import', help='add new records from files')
    import_parser.set_defaults(dispatch=import_records)
    import_parser.add_argument('files', metavar='F', nargs='+', type=Path, help='name(s) of file(s) with records to add')
    import_parser.add_argument('--account', metavar='A', help='process only this account')
    import_parser.add_argument('--start_date', metavar='D', type=parse_date, help='starting date')
    import_parser.add_argument('--end_date', metavar='D', type=parse_date, help='ending date')
    import_parser.add_argument('--month', metavar='D', choices=months, help='add records only for this month')

    export_parser = subparsers.add_parser('export', help='write transactions to file')
    export_parser.set_defaults(dispatch=export_records)
    export_parser.add_argument('--file', metavar='F', type=Path, required=True, help='name of output file')
    export_parser.add_argument('--start_date', metavar='D', type=parse_date, help='starting date')
    export_parser.add_argument('--end_date', metavar='D', type=parse_date, help='ending date')
    export_parser.add_argument('--month', metavar='D', choices=months, help='add records only for this month')

    save_recs_parser = subparsers.add_parser('save', help='save a database to a text file')
    save_recs_parser.set_defaults(dispatch=save_records)
    save_recs_parser.add_argument('--file', metavar='F', help='name of output file',default='dexter.docs')
    save_recs_parser.add_argument('--force', action='store_true', help='overwrite existing file')

    restore_recs_parser = subparsers.add_parser('restore', help='load documents into a database')
    restore_recs_parser.set_defaults(dispatch=restore_records)
    restore_recs_parser.add_argument('--file', metavar='F', help='name of file with records to restore',default='dexter.docs')

    pair_parser = subparsers.add_parser('pair', help='make transactions from matching entries')
    pair_parser.set_defaults(dispatch=pair_entries)

    review_parser = subparsers.add_parser('review', help='review transactions')
    review_parser.set_defaults(dispatch=review_unpaired)

    add_trans_parser = subparsers.add_parser('add', help='add a new transaction')
    add_trans_parser.set_defaults(dispatch=add_transaction)

    reconcile_parser = subparsers.add_parser('reconcile', help='reconcile statements')
    reconcile_parser.set_defaults(dispatch=reconcile_statements)

    audit_parser = subparsers.add_parser('audit', help='print an audit report')
    audit_parser.set_defaults(dispatch=print_audit_report)
    audit_parser.add_argument('--start_date', metavar='D', type=parse_date, help='starting date')
    audit_parser.add_argument('--end_date', metavar='D', type=parse_date, help='ending date')
    audit_parser.add_argument('--month', metavar='M', choices=months, help='define start and end dates based on month name')

    balance_parser = subparsers.add_parser('balance', help='print a balance report')
    balance_parser.set_defaults(dispatch=print_balance_report)
    balance_parser.add_argument('accts', metavar='A', nargs='*', help='accounts')
    balance_parser.add_argument('--level', metavar='D', type=parse_date, help='starting date')
    balance_parser.add_argument('--budget', action='store_true', help='include budget transactions')
    balance_parser.add_argument('--start_date', metavar='D', type=parse_date, help='starting date')
    balance_parser.add_argument('--end_date', metavar='D', type=parse_date, help='ending date')
    balance_parser.add_argument('--month', metavar='M', choices=months, help='define start and end dates based on month name')

    journal_parser = subparsers.add_parser('journal', help='print journals for expense accounts')
    journal_parser.set_defaults(dispatch=print_expense_report)
    journal_parser.add_argument('accts', metavar='A', nargs='*', help='accounts')
    journal_parser.add_argument('--budget', action='store_true', help='include budget transactions')
    journal_parser.add_argument('--details', action='store_true', help='print each transaction on a single line')
    journal_parser.add_argument('--start_date', metavar='D', type=parse_date, help='starting date')
    journal_parser.add_argument('--end_date', metavar='D', type=parse_date, help='ending date')
    journal_parser.add_argument('--month', metavar='M', choices=months, help='define start and end dates based on month name')

    select_parser = subparsers.add_parser('select', help='select transactions')
    select_parser.set_defaults(dispatch=select_transactions)
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

    if len(sys.argv) == 1:
        parser.print_usage()
        exit(1)

    args = parser.parse_args()

    if args.command is None:
        print('command required')
        parser.print_usage()
        exit(1)

    if args.command == 'config':
        Config.print_default()
        exit(0)

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
        DB.open(args.dbname, args.command not in ['init','restore'])
        args.dispatch(args)
    except (ValueError, FileNotFoundError, ModuleNotFoundError) as err:
        logging.error(err)
    # except FileNotFoundError as err:
    #     logging.error(err)
    # except ModuleNotFoundError as err:
    #     logging.error(err)
    except Exception as err:
        console.print_exception(show_locals=True)
