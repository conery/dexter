# Report generators

import logging

from .DB import DB, Transaction, Entry
from .console import print_transaction_table

def print_report(args):
    '''
    Report generator.  Command line options specify which type of report
    to make and what format to use.

    Arguments:
        args:  command line arguments
    '''
    match args.content:
        case 'audit':           print_audit_report(args)
        case 'balance':         print_balance_report(args)
        case 'expense':         print_expense_report(args)
        case 'transaction':     print_transaction_report(args)

def print_audit_report(args):
    print('audit report', vars(args))

def print_balance_report(args):
    print('balance report', vars(args))

def print_expense_report(args):
    print('expense report', vars(args))

def print_transaction_report(args):
    '''
    Print transactions to stdout.  The default format is a ledger/hledger
    journal, use --compact to print one line per transaction, --csv for
    CSV output.  Other supported arguments are start date, end date, month.

    Arguments:
        args:  command line arguments
    '''
    logging.debug('Transaction report')

    dct = DB.transaction_constraints
    kwargs = {}

    for name in dct:
        if val := vars(args).get(name):
            kwargs[name] = val
            logging.debug(f'  {name} = {val}')

    if args.csv:
        printer = print_csv_transaction
    elif args.compact:
        printer = print_compact_transaction
    else:
        printer = print_journal_transaction

    for t in DB.select(Transaction, **kwargs):
        printer(t)

def print_csv_transaction(obj):
    print('csv', obj)

def print_compact_transaction(obj):
    print('compact', obj)

def print_journal_transaction(obj):
    print('journal', obj)

