#! /usr/bin/env python3

# Top level application for dexter (Double-entry Expense Tracker)

import argparse
import calendar
import logging
from pathlib import Path
import sys

from pymongo.errors import ServerSelectionTimeoutError

from .config import Config, initialize_config, setup
from .console import console
from .DB import DB, Transaction, Entry
from .util import setup_logging, parse_date, date_range

from .fill import fill
from .io import print_info, init_database, save_records, restore_records, import_records, export_records
from .pair import pair_entries
from .reconcile import reconcile_statements
from .report import print_audit_report, print_balance_report
from .select import select

def init_cli():
    """
    Use argparse to create the command line API, then initialize the logger
    to print status messages on the console.

    Returns:
        a Namespace object with values of the command line arguments. 
    """
    months = [ m[:3].lower() for m in calendar.month_name[1:] ]
    orders = set(Transaction.order_by.keys()) | set(Entry.order_by.keys())

    parser = argparse.ArgumentParser()
    parser.add_argument('--dbname', metavar='X', help='database name')
    parser.add_argument('--log', metavar='X', choices=['quiet','info','debug'], default='info')
    parser.add_argument('--preview', action='store_true')
    parser.add_argument('--config', metavar='F', help='TOML file with configuration settings')
    
    subparsers = parser.add_subparsers(title='subcommands', dest='command')

    audit_parser = subparsers.add_parser('audit', help='print an audit report')
    audit_parser.set_defaults(dispatch=print_audit_report)
    audit_parser.add_argument('--start_date', metavar='D', type=parse_date, help='starting date')
    audit_parser.add_argument('--end_date', metavar='D', type=parse_date, help='ending date')
    audit_parser.add_argument('--month', metavar='M', choices=months, help='define start and end dates based on month name')

    export_parser = subparsers.add_parser('export', help='write transactions to file')
    export_parser.set_defaults(dispatch=export_records)
    export_parser.add_argument('file', metavar='F', type=Path, help='name of output file')
    export_parser.add_argument('--start_date', metavar='D', type=parse_date, help='starting date')
    export_parser.add_argument('--end_date', metavar='D', type=parse_date, help='ending date')
    export_parser.add_argument('--month', metavar='M', choices=months, help='add records only for this month')

    fill_parser = subparsers.add_parser('fill', help='fill envelopes')
    fill_parser.set_defaults(dispatch=fill)
    fill_parser.add_argument('files', metavar='F', nargs='*', help='TOML files with budget')
    fill_parser.add_argument('--date', metavar='D', type=parse_date, help='transaction date')
    fill_parser.add_argument('--month', metavar='M', choices=months, help='infer date from month name')

    import_parser = subparsers.add_parser('import', help='add new records from files')
    import_parser.set_defaults(dispatch=import_records)
    import_parser.add_argument('files', metavar='F', nargs='+', type=Path, help='name(s) of file(s) with records to add')
    import_parser.add_argument('--account', metavar='A', help='account name')
    import_parser.add_argument('--start_date', metavar='D', type=parse_date, help='starting date')
    import_parser.add_argument('--end_date', metavar='D', type=parse_date, help='ending date')
    import_parser.add_argument('--month', metavar='M', choices=months, help='add records only for this month')
    import_parser.add_argument('--regexp', action='store_true', help='CSV files have regular expression definitions')
    import_parser.add_argument('--extract_text', action='store_true', help='print lines of text in a PDF file')

    info_parser = subparsers.add_parser('info', help='print DB status')
    info_parser.set_defaults(dispatch=print_info)

    init_db_parser = subparsers.add_parser('init', help='initialize a database')
    init_db_parser.set_defaults(dispatch=init_database)
    init_db_parser.add_argument('file', metavar='F', help='name of file with account definitions')
    init_db_parser.add_argument('--force', action='store_true', help='replace an existing database')

    pair_parser = subparsers.add_parser('pair', help='make transactions from matching entries')
    pair_parser.set_defaults(dispatch=pair_entries)

    reconcile_parser = subparsers.add_parser('reconcile', help='reconcile statements')
    reconcile_parser.set_defaults(dispatch=reconcile_statements)
    reconcile_parser.add_argument('--card', metavar='C', help='card name')
    actions = reconcile_parser.add_mutually_exclusive_group()
    actions.add_argument('--csv', action='store_true', help='print payments and purchases in CSV format')
    actions.add_argument('--repl', action='store_true', help='show each card in command line REPL')
    actions.add_argument('--apply', action='store_true', help='update cards if fully reconciled')

    report_parser = subparsers.add_parser('report', help='print a balance report')
    report_parser.set_defaults(dispatch=print_balance_report)
    report_parser.add_argument('accts', metavar='A', nargs='*', help='accounts')
    report_parser.add_argument('--start_date', metavar='D', type=parse_date, help='starting date')
    report_parser.add_argument('--end_date', metavar='D', type=parse_date, help='ending date')
    report_parser.add_argument('--month', metavar='M', choices=months, help='define start and end dates based on month name')
    report_parser.add_argument('--no_budget', action='store_true', help='remove budget transactions')
    report_parser.add_argument('--abbrev', action='store_true', help='print abbreviated names')
    report_parser.add_argument('--grouped', action='store_true', help='group by account name')

    restore_recs_parser = subparsers.add_parser('restore', help='load documents into a database')
    restore_recs_parser.set_defaults(dispatch=restore_records)
    restore_recs_parser.add_argument('file', metavar='F', help='name of file with records to restore')
    restore_recs_parser.add_argument('--force', action='store_true', help='replace an existing database')

    save_recs_parser = subparsers.add_parser('save', help='save a database to a text file')
    save_recs_parser.set_defaults(dispatch=save_records)
    save_recs_parser.add_argument('file', metavar='F', help='name of output file')
    save_recs_parser.add_argument('--force', action='store_true', help='overwrite existing file')

    select_parser = subparsers.add_parser('select', help='select transactions or postings')
    select_parser.set_defaults(dispatch=select)
    select_parser.add_argument('--entry', action='store_true', help='select individual debits or credits')
    select_parser.add_argument('--uid', metavar='X', help='unique object ID (entry)')
    select_parser.add_argument('--date', metavar='D', type=parse_date, help='transaction or posting date')
    select_parser.add_argument('--start_date', metavar='D', type=parse_date, help='starting date')
    select_parser.add_argument('--end_date', metavar='D', type=parse_date, help='ending date')
    select_parser.add_argument('--month', metavar='M', choices=months, help='define start and end dates based on month name')
    select_parser.add_argument('--credit', metavar='A', help='credit account name (transaction)')
    select_parser.add_argument('--debit', metavar='A', help='debit account name (transaction)')
    select_parser.add_argument('--account', metavar='A', help='account name (entry)')
    select_parser.add_argument('--column', metavar='C', choices=['credit','debit'], help='entry type (posting)')
    select_parser.add_argument('--description', metavar='X', help='descriptions pattern')
    select_parser.add_argument('--comment', metavar='X', help='comment pattern (transaction)')
    select_parser.add_argument('--tag', metavar='X', help='tag pattern')
    select_parser.add_argument('--amount', metavar='N', type=float, help='amount')
    select_parser.add_argument('--min_amount', metavar='N', type=float, help='minimum amount')
    select_parser.add_argument('--max_amount', metavar='N', type=float, help='maximum amount')
    select_parser.add_argument('--abbrev', action='store_true', help='show abbreviated account names')
    select_parser.add_argument('--order_by', metavar='C', choices=orders, default='date', help='sort order')
    select_parser.add_argument('--total', action='store_true', help='show total amount of selected transactions')
    select_parser.add_argument('--unpaired', action='store_true', help='set --entry and --tag #unpaired')
    actions = select_parser.add_mutually_exclusive_group()
    actions.add_argument('--update', metavar='F V', nargs=2, help='update fields')
    actions.add_argument('--delete', action='store_true', help='delete selected records')
    actions.add_argument('--split', action='store_true', help='add new debits to a record')
    actions.add_argument('--csv', action='store_true', help='print in CSV format, with a header line')
    actions.add_argument('--journal', action='store_true', help='print in Journal format (transaction)')
    actions.add_argument('--repl', action='store_true', help='show selection in command line REPL')
    actions.add_argument('--gui', action='store_true', help='show selection in a GUI')

    setup_parser = subparsers.add_parser('setup', help='initialize a project directory')
    setup_parser.add_argument('--tutorial', action='store_true', help='copy tutorial data to new project')

    if len(sys.argv) == 1:
        parser.print_usage()
        exit(1)

    args = parser.parse_args()
    setup_logging(args.log)

    if args.command is None:
        print('command required')
        parser.print_usage()
        exit(1)

    if args.command == 'setup':
        try:
            setup(args)
        except FileExistsError as err:
            logging.error(f'File exists: {err}')
        exit(0)

    if 'month' in vars(args):
        if m := args.month:
            ds, de = date_range(m)
            args.start_date = ds
            args.end_date = de

    logging.debug('command line arguments:')
    for name, val in vars(args).items():
        if val is not None:
            logging.debug(f'  --{name} {val} {type(val)}')

    return args 

def main():
    """
    Top level entry point
    """
    args = init_cli()
    try:
        initialize_config(args.config)
        DB.init()
        args.dispatch(args)
    except ServerSelectionTimeoutError:
        logging.error("Can't connect to MongoDB server")
    except (ValueError, FileNotFoundError, ModuleNotFoundError) as err:
        logging.error(err)
    except Exception as err:
        console.print_exception(show_locals=True)
