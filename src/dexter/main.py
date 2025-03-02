#! /usr/bin/env python3

# Top level application for dexter (Double-entry Expense Tracker)

import argparse
import sys

# Functions for commands (will be moved to modules)

def initialize_database(args):
    print('initialize_database')

def backup_database(args):
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

def init_cli():
    """
    Use argparse to create the command line API.

    Returns:
        a Namespace object with values of the command line arguments. 
    """

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='subcommands', dest='command')

    init_parser = subparsers.add_parser('init', help='initialize a database')
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
    # setup_logging(args.log)
    # DB.open(args.db)
    args.dispatch(args)
