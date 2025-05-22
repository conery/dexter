#
# Define a Rich Console object and styles used in terminal output
#

import csv
import sys

from .config import Config
from .DB import Entry, Transaction

from rich.console import Console
from rich.theme import Theme
from rich.style import Style
from rich.table import Table, Column

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

# console = Console(theme=dark_terminal)
console = Console(theme=light_terminal)

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
    'tags':    {'width': 5, 'justify': 'center'},
}

def print_records(docs, name=None, count=0):
    '''
    Print a grid containing descriptions of documents.  Each document
    class has its own `row` method that has the information it wants
    to display.  Groups documents by collection, then print each group.

    Arguments:
        docs:  a list of documents
    '''
    # dct = {}
    # for obj in docs:
    #     lst = obj.row()
    #     a = dct.setdefault(lst[0], [])
    #     a.append(lst)

    # for tbl, lst in dct.items():
    #     n = len(lst[0])
    #     grid = Table.grid(""*n, padding=[0,2,0,2])
    #     for row in lst:
    #         grid.add_row(*row)
    #     console.print(grid)
    #     console.print()

    if name:
        title = f'[bold blue]{name}'
        if count:
            title += f' ({count})'
        console.print(title)

    lst = [obj.row() for obj in docs]
    n = len(lst[0])
    grid = Table.grid(""*n, padding=[0,3,0,3])
    for row in lst:
        grid.add_row(*row)
    console.print(grid)
    console.print()

def tag_strings(rec):
    '''
    Return a string to display in the tags column of a table, looking up
    symbols for system tags.

    Arguments:
        lst:  an Entry document
    '''
    i = 0 if rec.column == Column.cr else 1
    return " ".join([Config.tag_syms[t][i] for t in rec.tags])

def print_transaction_table(
        lst, 
        as_csv=False, 
        name=None, 
        original=False, 
        styles={}
    ):

    if lst and isinstance(lst[0],Entry):
        header = dict(entry_header_format)
        row_type = 'entry'
    else:
        header = dict(transaction_header_format)
        row_type = 'transaction'

    colnames = header.keys()

    if as_csv:
        writer = csv.DictWriter(sys.stdout, colnames)
        writer.writeheader()
    else:
        t = Table(
            title=name,
            title_justify='left',
            title_style='table_header'
        )
        for h in colnames:
            args = styles.get(h) or header.get(h)
            t.add_column(h, **args)
            
    for rec in lst:
        row = []
        if row_type == 'entry':
            row.append(str(rec.date))
            row.append(rec.account)
            row.append(format_amount(rec.amount, dollar_sign=True))
            row.append(str(rec.column))
            row.append(rec.description)
            row.append(tag_strings(rec))
        else:
            row.append(str(rec.pdate))
            row.append(rec.pcredit)
            row.append(rec.pdebit)
            row.append(format_amount(rec.pamount, dollar_sign=True))
            row.append(rec.description)
            row.append(rec.comment)
            row.append(", ".join([f'{s}' for s in rec.tags]))
        if as_csv:
            writer.writerow(dict(zip(colnames,row)))
        else:
            t.add_row(*row)

    print()
    if not as_csv:
        console.print(t)

def print_info_table(dct):
    tbl = Table(
        Column(header='name', width=12),
        Column(header='account', justify='right'),        
        Column(header='transaction', justify='right'),
        Column(header='entry', justify='right'),        
        Column(header='reg_exp', justify='right'),
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
    n = len(recs[0])
    grid = Table.grid(""*n, padding=[0,2,0,2])
    for row in recs:
        grid.add_row(*row)
    if name:
        title = f'[bold blue]{name}'
        if count:
            title += f' ({count})'
        console.print(title)
    console.print(grid)
    console.print()
