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
                starts.append(DB.balance(aname, ending=start_date, nobudget=args.no_budget))
                ends.append(DB.balance(aname, ending=end_date, nobudget=args.no_budget))
        else:
            logging.error(f'ier: bad spec: {spec}')

    title = f'Account Balance   {start_date} to {end_date}'
    if not args.no_budget:
        title += '  ✉️'

    t = Table(
        Column(header='account', width=30),
        title_justify='left',
        title_style='table_header',
        title = title,        
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
        print_detail_table(acct, elist, start_date, args.no_budget)


def print_detail_table(acct, entries, start, nobudget):
    '''
    Helper function for expense report.  Uses rich to print a table
    with one line per record, updating balance.

    Arguments:
        acct:  account name
        entries:  list of entries for the account
        start: date to use for starting balance
    '''

    title=acct
    if not nobudget:
        title += '  ✉️'

    t = Table(
        Column(header='date', width=12),
        Column(header='description', width=25, no_wrap=True),
        # Column(header='account', width=22, no_wrap=True),
        Column(header='credit', width=20, no_wrap=True),
        Column(header='debit', width=20, no_wrap=True),
        Column(header='amount', width=12, justify='right'),
        # Column(header='credit', width=12, justify='right'),
        Column(header='balance', width=12, justify='right'),
        title=title,
        title_justify='left',
        title_style='table_header',
        # show_header=False
    )
    bal = DB.balance(acct, start)

    fills = []
    nonfills = []
    for e in entries:
        if Tag.B in e.tags:
            fills.append(e)
        else:
            nonfills.append(e)

    t.add_row(f'[blue italic]{start}','[blue italic]starting balance','','','',format_amount(bal, dollar_sign=True))

    if not nobudget:
        for e in fills:
            row = []
            bal += e.value
            row.append(f'[blue italic]{str(e.date)}')
            row.append(f'[blue italic]{e.tref.description}')
            row.append(DB.display_name(acct, markdown=True))
            row.append(DB.display_name(e.tref.pdebit, markdown=True))
            row.append(format_amount(e.value, dollar_sign=True))
            row.append(format_amount(bal, dollar_sign=True))
            t.add_row(*row)

    for e in nonfills:
        row = []
        bal += e.value
        debit = credit = ''
        if trans := e.tref:
            for x in trans.entries:
                if x.column == ColType.cr:
                    credit = DB.display_name(x.account, markdown=True)
                else:
                    debit = DB.display_name(x.account, markdown=True)
        row.append(str(e.date))
        row.append(trans.description)
        row.append(credit)
        row.append(debit)
        row.append(format_amount(e.value, dollar_sign=True))
        row.append(format_amount(bal, dollar_sign=True))
        t.add_row(*row)
    console.print()
    console.print(t)

def print_audit_report(args):
    print('audit report', vars(args))

def print_compact_transaction(obj):
    print('compact', obj)

