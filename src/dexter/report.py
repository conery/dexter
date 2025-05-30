# Report generators

import datetime
import logging
import re

from rich.table import Table, Column

from .DB import DB, Transaction, Entry, Column as ColType
from .console import console, format_amount
from .config import Config, Tag


def print_balance_report(args):
    '''
    Top level function for the 'report' command.  
    
    Arguments:
        args:  command line arguments
    '''
    DB.open(args.dbname)
    logging.debug(f'expense report {vars(args)}')
    
    if args.grouped:
        print_grouped_report(args)
    else:
        print_detailed_report(args)

def print_grouped_report(args):
    '''
    Print a one-line summary of the balance of each account.
    '''
    start_date = args.start_date or Config.start_date
    end_date = args.end_date or datetime.date.today()

    accts = []
    starts = []
    ends = []
    
    for spec in (args.accts or DB.account_glob()):
        if alist := DB.account_glob(spec):
            for aname in alist:
                logging.debug(f'report (grouped):  balances for {aname}')
                accts.append(aname)
                starts.append(DB.balance(aname, ending=start_date, nobudget=args.nobudget))
                ends.append(DB.balance(aname, ending=end_date, nobudget=args.nobudget))
        else:
            logging.error(f'ier: bad spec: {spec}')

    t = Table(
        Column(header='account', width=30),
        title_justify='left',
        title_style='table_header',
        title = f'Account Balance   {start_date} to {end_date}'
    )

    if args.start_date and args.end_date:
        t.add_column('starting', width=12, justify='right')
        t.add_column('ending', width=12, justify='right')
        t.add_column('difference', width=12, justify='right')
    else:
        t.add_column('balance', width=12, justify='right')

    for i in range(len(accts)):
        row = [accts[i]]
        if args.start_date and args.end_date:
            row.append(format_amount(starts[i], dollar_sign=True))
            row.append(format_amount(ends[i], dollar_sign=True))
            row.append(format_amount(ends[i]-starts[i], dollar_sign=True))
        elif args.start_date:
            row.append(format_amount(starts[i], dollar_sign=True))
        else:
            row.append(format_amount(ends[i], dollar_sign=True))
        t.add_row(*row)
    console.print()
    console.print(t)

def print_detailed_report(args):
    '''
    Detailed expense report, with one line for each transaction
    in the date range.
    '''
    start_date = args.start_date or Config.start_date
    end_date = args.end_date or datetime.date.today()
    entries = {}

    for spec in (args.accts or DB.account_glob()):
        if alist := DB.account_glob(spec):
            for aname in alist:
                logging.debug(f'report:  transactions for {aname}')
                entries[aname] = DB.select(Entry, account=aname, start_date=start_date, end_date=end_date).order_by('date')
        else:
            logging.error(f'report: bad spec: {spec}')

    for acct, elist in entries.items():
        print_detail_table(acct, elist, start_date)


def print_detail_table(acct, entries, start):
    '''
    Helper function for expense report.  Uses rich to print a table
    with one line per record, updating balance.

    Arguments:
        acct:  account name
        entries:  list of entries for the account
        start: date to use for starting balance
    '''

    t = Table(
        Column(header='date', width=12),
        Column(header='description', width=22, no_wrap=True),
        Column(header='account', width=22, no_wrap=True),
        Column(header='debit', width=12, justify='right'),
        Column(header='credit', width=12, justify='right'),
        Column(header='balance', width=12, justify='right'),
        title=acct,
        title_justify='left',
        title_style='table_header',
        # show_header=False
    )
    bal = DB.balance(acct, start)
    t.add_row(f'[blue italic]{start}','[blue italic]starting balance','','','',format_amount(bal, dollar_sign=True))
    for e in entries:
        if trans := e.tref:
            s = trans.pdebit if e.column == ColType.cr else trans.pcredit
            other = DB.display_name(s, markdown=True)
        else:
            s = 'unpaired' if Tag.U in e.tags else 'missing'
            trans = Transaction(description=f'[red]{s}')
            other = ''
        row = []
        row.append(str(e.date))
        row.append(trans.description)
        row.append(other)
        if e.column.value == 'debit':
            row.append(format_amount(e.amount, dollar_sign=True))
            row.append('')
        else:
            row.append('')
            row.append(format_amount(e.amount, dollar_sign=True))
        bal += e.value
        row.append(format_amount(bal, dollar_sign=True))
        t.add_row(*row)
    console.print()
    console.print(t)

def print_audit_report(args):
    print('audit report', vars(args))

def print_compact_transaction(obj):
    print('compact', obj)

