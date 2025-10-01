# Report generators

from datetime import date, timedelta
import logging
import re

from rich.table import Table, Column

from .DB import DB, Transaction, Entry, Column as ColType, Tag
from .console import console, format_amount
from .config import Config


def print_balance_report(args):
    '''
    Top level function for the 'report' command.  
    
    Arguments:
        args:  command line arguments
    '''
    DB.open(args.dbname)
    logging.debug(f'expense report {vars(args)}')

    accounts = []
    for acct in args.accts:
        if re.match(r'.*:\d+$', acct):
            lst = DB.expand_node(acct)
            accounts += lst
        else:
            accounts.append(acct)
    logging.debug(f'report: accounts = {accounts}')

    if args.grouped:
        print_grouped_report(args, accounts)
    else:
        print_detailed_report(args, accounts)

def print_grouped_report(args, accounts):
    '''
    Print a one-line summary of the balance of each account.
    '''
    start_date = args.start_date or Config.DB.start_date
    end_date = args.end_date or date.today()

    starts = []
    debits = []
    credits = []
    ends = []
    
    for aname in accounts:
        starts.append(DB.balance(aname, ending=start_date-timedelta(days=1), nobudget=args.no_budget))
        debits.append(DB.column_sum(aname, ColType.dr, starting=start_date, ending=end_date, nobudget=args.no_budget))
        credits.append(-DB.column_sum(aname, ColType.cr, starting=start_date, ending=end_date, nobudget=args.no_budget))
        ends.append(starts[-1] + debits[-1] + credits[-1])

    title = f'Account Balances   {start_date} to {end_date}'
    if not args.no_budget:
        title += '  ✉️'

    t = Table(
        Column(header='account', width=30),
        title_justify='left',
        title_style='table_header',
        title = title,        
    )

    t.add_column('starting', width=12, justify='right')
    t.add_column('debits', width=12, justify='right')
    t.add_column('credits', width=12, justify='right')
    t.add_column('ending', width=12, justify='right')

    for i in range(len(accounts)):
        name = accounts[i]
        if name.endswith('$'):
            name = name[:-1]
        row = [name]
        row.append(format_amount(starts[i], dollar_sign=True))
        row.append(format_amount(debits[i], dollar_sign=True))
        row.append(format_amount(credits[i], dollar_sign=True))
        row.append(format_amount(ends[i], dollar_sign=True))
        t.add_row(*row)
    t.add_section()
    row = ['[blue italic]total']
    for col in [starts, debits, credits, ends]:
        row.append(format_amount(sum(col), dollar_sign=True))
    t.add_row(*row)
    console.print()
    console.print(t)

def print_detailed_report(args, accounts):
    '''
    Detailed expense report, with one line for each transaction
    in the date range.
    '''
    start_date = args.start_date or Config.DB.start_date
    end_date = args.end_date or date.today()
    entries = {}

    for aname in accounts:
        entries[aname] = DB.select(Entry, account=aname, start_date=start_date, end_date=end_date).order_by('date')

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
    if acct.endswith('$'):
        acct = acct[:-1]

    title=acct
    if not nobudget:
        title += '  ✉️'

    t = Table(
        Column(header='date', width=12),
        Column(header='description', width=25, no_wrap=True),
        Column(header='credit', width=20, no_wrap=True),
        Column(header='debit', width=20, no_wrap=True),
        Column(header='amount', width=12, justify='right'),
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
        if Tag.B.value in e.tags:
            fills.append(e)
        else:
            nonfills.append(e)

    logging.debug(f'fills {fills}')
    logging.debug(f'nonfills {nonfills}')

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
        row.append(str(e.date))
        if trans := e.tref:
            for x in trans.entries:
                if x.column == ColType.cr:
                    credit = DB.display_name(x.account, markdown=True)
                else:
                    debit = DB.display_name(x.account, markdown=True)
            row.append(trans.description)
        else:
            row.append('[red italic]unpaired')
        row.append(credit)
        row.append(debit)
        row.append(format_amount(e.value, dollar_sign=True))
        row.append(format_amount(bal, dollar_sign=True))
        t.add_row(*row)
    console.print()
    console.print(t)

def print_audit_report(args):
    '''
    Top level function for the 'audit' command.  
    
    Arguments:
        args:  command line arguments
    '''
    DB.open(args.dbname)
    logging.debug(f'audit report {vars(args)}')

    for cls in [Transaction, Entry]:
        for obj, reason in DB.validate(cls):
            console.print(f'{reason}: {obj}')        
