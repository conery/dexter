# Report generators

import logging
import re

from rich.table import Table, Column

from .DB import DB, Transaction
from .console import console, format_amount


def print_expense_report(args):
    '''
    Top level function for the 'expenses' command.  
    
    Arguments:
        args:  command line arguments
    '''
    logging.debug(f'expense report {vars(args)}')

    # kwargs = {}
    # for name in DB.transaction_constraints:
    #     if val := vars(args).get(name):
    #         kwargs[name] = val
    #         logging.debug(f'  {name} = {val}')

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
        logging.debug(f'expense_report: {recs}')
        if recs:
            print_expense_table(recs, group)

# expense_headers = {
#     'date':         {'width': 12},
#     'description':  {'width': 30, 'no_wrap': True},
#     '':             {'width': 20},
#     'amount':       {'width': 12, 'justify': 'right'},
# }

def print_expense_table(lst, name):
    '''
    Helper function for expense report.  Uses rich to print a table
    with one line per record and the updated balances.

    Arguments:
        lst: a list of Transaction objects
        name:  account name
    '''
    # print(name)
    # for obj in lst:
    #     print(obj)
    # return

    t = Table(
        Column(header='date', width=12),
        Column(header='description', width=30, no_wrap=True),
        Column(header='account', width=20),
        Column(header='debit', width=12, justify='right'),
        Column(header='credit', width=12, justify='right'),
        title=name,
        title_justify='left',
        title_style='table_header',
        # show_header=False
    )
    for obj in lst:
        for e in obj.entries:
            if not re.search(f'^{name}$',e.account):
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

