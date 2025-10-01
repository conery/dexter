#
# Define a Rich Console object and styles used in terminal output
#

import calendar
import csv
import logging
import sys

from .config import Config
from .DB import DB, Entry, Column

from rich.console import Console
from rich.theme import Theme
from rich.style import Style
from rich.table import Table, Column as TableColumn
from rich.markup import escape

# Suggested colors for terminals with a light theme

light_terminal = Theme({
    'table_header': Style(
        color = 'black',
        bgcolor= 'grey82',
    ),
})

# Suggest colors for terminals with a dark theme

dark_terminal = Theme({
    'table_header': Style(
        color = 'white',
        bgcolor= 'dodger_blue2',
    ),
    'highlight': Style(
        color = 'honeydew2',
        bgcolor = 'grey42',
    ),
    'error': Style(
        color = 'red'
    ),
    'autofill': Style(
        color = 'honeydew2',
    ),
    'editable': Style(
        color = 'white',
        bgcolor = 'grey39',
        italic = True
    ),
    'edited': Style(
        color = 'dodger_blue2',
        bgcolor = 'grey82',
    ),
})

console = Console(theme=dark_terminal, emoji=None)
# console = Console(theme=light_terminal)

def format_amount(n, dollar_sign=False):
    '''
    Return a string to print for a dollar amount.  If dollar_sign is true include
    a dollar sign at the front and include commas as a thousands separator.
    '''
    sign = '−' if n < 0 else ''
    if dollar_sign:
        return f'{sign}${round(abs(n),2):,.2f}'
    else:
        return f'{sign}{round(abs(n),2):.2f}'

def format_date(date):
    '''Return a date string to use in reports'''
    m = int(date[5:7])
    d = int(date[8:])
    return calendar.month_abbr[m] + ' ' + str(d)


transaction_header_format = {
    'date':         {'width': 12},
    'credit':       {'width': 20},
    'debit':        {'width': 20},
    'amount':       {'width': 12, 'justify': 'right'},
    'description':  {'width': 30, 'no_wrap': True},
    'comment':      {'width': 15, 'no_wrap': True},
    'tags':         {'width': 15},
}

entry_header_format = {
    'date':    {'width': 12},
    'account': {'width': 25},
    'amount':  {'width': 15, 'justify': 'right'},
    'column':  {'width': 10, 'justify': 'center'},
    'description':  {'width': 30, 'no_wrap': True},
    'tags':    {'width': 15},
    # 'tref':    {'width': 12},
}

def make_row(rec, row_type, abbrev):
    '''
    Helper function for print_transaction_table and print_csv_transactions.
    Extra data from a record and save it in a list.
    '''
    row = []
    if row_type == 'entry':
        acct = DB.abbrev(rec.account) if abbrev else rec.account
        row.append(str(rec.date))
        row.append(acct)
        row.append(format_amount(rec.amount, dollar_sign=True))
        row.append(rec.column.value)
        row.append(rec.description)
        # row.append(", ".join([f'{s.value}' for s in rec.tags]))
        row.append(', '.join(rec.tags))
        # row.append(str(rec.tref)[:10])
    else:
        cr = DB.abbrev(rec.pcredit) if abbrev else DB.display_name(rec.pcredit, markdown=True)
        dr = DB.abbrev(rec.pdebit) if abbrev else DB.display_name(rec.pdebit, markdown=True)
        row.append(str(rec.pdate))
        row.append(cr)
        row.append(dr)
        row.append(format_amount(rec.pamount, dollar_sign=True))
        row.append(rec.description)
        row.append(rec.comment)
        row.append(", ".join([f'{s}' for s in rec.tags]))
    return row

def print_transaction_table(lst, args):
    '''
    Function called by select command to print a list of Entry or Transaction
    objects in a tabular form.

    Arguments:
        lst:  the selected objects
        args:  command line options
    '''
    if isinstance(lst[0],Entry):
        header = dict(entry_header_format)
        row_type = 'entry'
        name = 'Entries'
    else:
        header = dict(transaction_header_format)
        row_type = 'transaction'
        name = 'Transactions'

    colnames = header.keys()

    t = Table(
        title=name,
        title_justify='left',
        title_style='table_header'
    )
    for h in colnames:
        t.add_column(h, **header.get(h))
            
    for rec in lst:
        row = make_row(rec, row_type, args.abbrev)
        t.add_row(*row)

    console.print()
    console.print(t)

def print_csv_transactions(lst, args = None):
    '''
    Function called by select command to print a list of Entry or Transaction
    objects as CSV records.

    Arguments:
        lst:  the selected objects
        args:  command line options
    '''
    if len(lst) == 0:
        return
    
    if isinstance(lst[0],Entry):
        header = dict(entry_header_format)
        row_type = 'entry'
    else:
        header = dict(transaction_header_format)
        row_type = 'transaction'

    colnames = header.keys()

    writer = csv.DictWriter(sys.stdout, colnames)
    writer.writeheader()

    for rec in lst:
        row = make_row(rec, row_type, args and args.abbrev)
        writer.writerow(dict(zip(colnames,row)))

def print_journal_transactions(lst, args = None):
    '''
    Function called by select command to print a list of Entry or Transaction
    objects in Journal format.

    Arguments:
        lst:  the selected objects
        args:  command line options
    '''
    for obj in lst:
        line = f'{obj.pdate}   {obj.description}'
        if obj.comment:
            line += f'   ; {obj.comment}'
        print(line)
        for e in obj.entries:
            acct = DB.abbrev(e.account) if (args and args.abbrev) else e.account
            amt = format_amount(e.value, dollar_sign=True)
            line = f'    {acct:20s} {amt:>15s}'
            if e.description:
                line += f'     ; {e.description}'
            print(line)
        print()

def print_info_table(dct):
    tbl = Table(
        TableColumn(header='name', width=12),
        TableColumn(header='account', justify='right'),        
        TableColumn(header='transaction', justify='right'),
        TableColumn(header='entry', justify='right'),        
        TableColumn(header='reg_exp', justify='right'),
        title='Databases',
        title_justify='left',
        title_style='table_header',
    )
    for dbname, info in dct.items():
        row = [dbname]
        for col in ['account', 'transaction', 'entry', 'reg_exp']:
            n = info.get(col) or 0
            row.append(str(n))
        tbl.add_row(*row)
    print()
    console.print(tbl)
    
def print_grid(recs: list, name: str = None, count: int = 0):
    if name:
        title = f'[bold blue]{name}'
        if count:
            title += f' ({count})'
        console.print(title)
    if len(recs) > 0:
        n = len(recs[0])
        grid = Table.grid(""*n, padding=[0,2,0,2])
        for row in recs:
            grid.add_row(*row)
        console.print(grid)
    console.print()

def print_records(docs, name=None, count=0):
    '''
    Print a grid containing descriptions of documents.  Each document
    class has its own `row` method that has the information it wants
    to display.  Groups documents by collection, then print each group.

    Arguments:
        docs:  a list of documents
    '''

    if name:
        title = f'[bold blue]{name}'
        if count:
            title += f' ({count})'
        console.print(title)

    if len(docs) > 0:
        lst = [obj.row() for obj in docs]
        n = len(lst[0])
        grid = Table.grid(""*n, padding=[0,3,0,3])
        for row in lst:
            grid.add_row(*row)
        console.print(grid)
    console.print()
