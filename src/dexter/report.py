# Report generators

import logging

from .DB import DB, Transaction, Column
from .console import console, format_amount


def print_expense_report(args):
    print('expense report', vars(args))
    
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

