# Report generators

import datetime
import logging
import re

from rich.table import Table, Column

from .DB import DB, Transaction, Entry
from .console import console, format_amount
from .config import Tag


def print_expense_report(args):
    '''
    Top level function for the 'expenses' command.  
    
    Arguments:
        args:  command line arguments
    '''
    logging.debug(f'expense report {vars(args)}')
    if args.details:
        print_expense_details(args)
    else:
        print_expense_summary(args)

def print_expense_summary(args):
    '''
    Print a one-line summary of the balance of each account.
    '''
    accts = []
    starts = []
    ends = []
    for group in DB.account_groups(args.accts):
        accts.append(group)
        dct = {'account': group}
        if args.start_date and args.end_date:
            starts.append(DB.balance(group, ending=args.start_date, budgets=args.budget))
            ends.append(DB.balance(group, ending=args.end_date, budgets=args.budget))
        elif date := (args.start_date or args.end_date):
            starts.append(DB.balance(group, ending=date, budgets=args.budget))
        else:
            starts.append(DB.balance(group, budgets=args.budget))
    print_summary_table(accts, args, starts, ends)

def print_summary_table(accts, args, bal1, bal2):
    '''
    Helper function for `print_expense_summary`.  Prints a table with
    one or two budget columns, depending on the combination of date
    options from the command line.
    '''
    logging.debug(f'print_detail_table {accts} {bal1} {bal2}')
    title = 'Account Balance'
    match (args.start_date, args.end_date):
        case (start, end) if start and end:
            title += f'  {start} to {end}'
        case (start, None):
            title += f'  from {start}'
        case (None, end):
            title += f'  to {end}'
        case _:
            pass

    t = Table(
        Column(header='account', width=30),
        title=title,
        title_justify='left',
        title_style='table_header',
        # show_header=False
    )
    if args.start_date and args.end_date:
        t.add_column('starting', width=12, justify='right')
        t.add_column('ending', width=12, justify='right')
        t.add_column('difference', width=12, justify='right')
    else:
        t.add_column('balance', width=12, justify='right')
    for i in range(len(accts)):
        row = [accts[i]]
        row.append(format_amount(bal1[i], dollar_sign=True))
        if args.start_date and args.end_date:
            row.append(format_amount(bal2[i], dollar_sign=True))
            row.append(format_amount(bal2[i]-bal1[i], dollar_sign=True))
        t.add_row(*row)
    console.print()
    console.print(t)


def print_expense_details(args):
    '''
    Detailed expense report, with one line for each transaction
    in the date range.
    '''
    dct = {}
    for arg in ['start_date', 'end_date']:
        if val := vars(args).get(arg):
            dct[arg] = val
    
    for group in DB.account_groups(args.accts):
        logging.debug(f'expense_report: group {group}')
        kwargs = dct | {'debit': group}
        debits = DB.select(Transaction, **kwargs)
        kwargs = dct | {'credit': group}
        credits = DB.select(Transaction, **kwargs)
        recs = sorted(list(debits)+list(credits), key=lambda t: t.pdate)
        bal = DB.balance(group, ending=args.start_date - datetime.timedelta(days=1))
        logging.debug(f'expense_report: {recs}')
        if recs:
            print_detail_table(recs, group, bal, args.budget, args.start_date)

# expense_headers = {
#     'date':         {'width': 12},
#     'description':  {'width': 30, 'no_wrap': True},
#     '':             {'width': 20},
#     'amount':       {'width': 12, 'justify': 'right'},
# }

def print_detail_table(lst, name, bal, budget, date):
    '''
    Helper function for expense report.  Uses rich to print a table
    with one line per record and the updated balances.

    Arguments:
        lst: a list of Transaction objects
        name:  account name
        bal:  the account's starting balance
        budget:  include budget transactions if True
    '''
    # print(name)
    # for obj in lst:
    #     print(obj)
    # return

    balance_header = '✉️  balance' if budget else 'balance'

    t = Table(
        Column(header='date', width=12),
        Column(header='description', width=30, no_wrap=True),
        Column(header='account', width=30),
        Column(header='debit', width=12, justify='right'),
        Column(header='credit', width=12, justify='right'),
        Column(header=balance_header, width=12, justify='right'),
        title=name,
        title_justify='left',
        title_style='table_header',
        # show_header=False
    )
    t.add_row(f'[blue italic]{date}','[blue italic]starting balance','','','',format_amount(bal, dollar_sign=True))
    for obj in lst:
        for e in obj.entries:
            if not re.search(f'^{name}$',e.account):
                continue
            if not budget and Tag.B.value in obj.tags:
                continue
            row = []
            row.append(str(e.date))
            row.append(obj.description)
            if e.column.value == 'debit':
                row.append(obj.pcredit)
                row.append(format_amount(e.amount, dollar_sign=True))
                row.append('')
            else:
                row.append(obj.pdebit)
                row.append('')
                row.append(format_amount(e.amount, dollar_sign=True))
            bal += e.value
            row.append(format_amount(bal, dollar_sign=True))
            t.add_row(*row)
    console.print()
    console.print(t)

def print_audit_report(args):
    print('audit report', vars(args))

def print_balance_report(args):
    '''
    Print account balances to stdout.

    Arguments:
        args:  command line arguments
    '''
    logging.debug(f'balance report {vars(args)}')


def print_compact_transaction(obj):
    print('compact', obj)

# def print_journal_transaction(obj):
#     line = f'{obj.pdate} {obj.description:<30s}'
#     if obj.comment or obj.tags:
#         line += f'[italic] ; {obj.comment} {obj.tags}'
#     console.print(line)
#     for entry in obj.entries:
#         line = f'    {entry.account:<26s}'
#         amt = entry.amount if entry.column == Column.dr else -entry.amount
#         samt = format_amount(amt, dollar_sign=True)
#         line += f'{samt:>15s}'
#         if not entry.description.startswith('match '):
#             line += f'  ; {entry.description}'
#         console.print(line)
#     console.print()

