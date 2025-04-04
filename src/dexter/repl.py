# Command line REPL used by scripts that review transactions one at a time

import click
from curses.ascii import ESC, ctrl, unctrl
import readline
import re
import string
import sys

from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.console import Group

from .DB import DB, Transaction, Entry
from .console import console, format_amount
from .util import debugging

# class TPanel(Panel):

#     def __init__(self, transaction):
#         self.transaction = transaction
#         self.entry = transaction.entries[0]
#         # save attributes used to compose panel (both editable and not)
#         super().__init__(
#             Group(self.tline(), self.eline(), self.xline()),
#             width=100, 
#             padding=1, 
#             title='New Transaction', 
#             title_align="left"
#         )
#         # self.set_eline()

#     def tline(self):
#         # return Text(f'{self.date} [white on grey39]{self.desc} ; # ')
#         desc = self.transaction.description or ' ^P description           '
#         comm = self.transaction.comment or ' ^N comment    '
#         tags = self.transaction.tags or ' ^G tags '
#         line = Text(str(self.entry.date))
#         line += Text('  ')
#         line += Text(desc, style='editable')
#         line += Text('  ; ')
#         line += Text(comm, style='editable')
#         line += Text('  # ')
#         line += Text(tags, style='editable')
#         return line

#     def eline(self):
#         acct = f'    {self.entry.account:<30s}'
#         amt = format_amount(self.entry.amount, dollar_sign=True)
#         return Text(acct) + Text(amt)

#     def xline(self):
#         acct = self.transaction.entries[1].account or ' ^A account '
#         return Text('    ') + Text(acct, style='editable')


def make_panel(trans):
    '''
    Create the layout for displaying a transaction.
    '''

    def tline():
        line = Text(str(trans.entries[0].date))
        line += Text('  ')
        line += text['description']
        line += Text('  ; ')
        line += text['comment']
        line += Text('  # ')
        line += text['tags']
        return line

    def a1line():
        e = trans.entries[0]
        acct = f'{e.account:<35s}'
        amt = format_amount(e.amount, dollar_sign=True)
        line = indent
        line += Text(acct)
        line += Text(amt)
        line += Text(' ; ')
        line += Text(e.description)
        return line
    
    def a2line():
        return indent + text['account']
    
    text = {
        'description': Text(trans.description or (' ⌃P description     ')),
        'comment': Text(trans.comment or (' ⌃N comment  ')),
        'tags': Text(trans.tags or ' ⌃G tags '),
        'account': Text(trans.entries[1].account or ' ⌃A account ')
    }

    for f, t in text.items():
        t.style = 'edited' if f in trans.edited else 'editable'

    indent = Text('    ')
    grp = Group(tline(), a1line(), a2line())
    return Panel(grp, width=100, padding=1, title='New Transaction', title_align="left")

# Set up command line completion

def completer_function(tokens):

    def completer(text, state):
        matches = [s for s in tokens if s.startswith(text)]
        return matches[state]

    return completer

# Key combinations used to trigger updates

class KEY:
    PREV = chr(ESC) + '[' + 'A'
    NEXT = chr(ESC) + '[' + 'B'
    EDIT_DESC = ctrl('P')             # mnemonic:  "payee"
    EDIT_COMMENT = ctrl('N')          # mnemonic:  "note"
    EDIT_TAGS = ctrl('G')
    EDIT_ACCOUNT = ctrl('T')          # mnemonic:  "to"
    EDIT_REGEXP = ctrl('E')
    FILL_DESC = ctrl('F')
    MOD_DESC = ctrl('L')              # mnemonic:  "lambda"
    ACCEPT = ctrl('A')

cmnd_keys = { x[1] for x in vars(KEY).items() if not x[0].startswith('__') }
digit_keys = set('0123456789')
all_keys = cmnd_keys | digit_keys | { '?' }

field_names = {
    KEY.EDIT_DESC: 'description',
    KEY.EDIT_COMMENT: 'comment',
    KEY.EDIT_TAGS: 'tags',
    KEY.MOD_DESC: 'description',
}

# Display a single transactions.  If there were any
# issues when making the row they were appended to the message list,
# display that list after the row.

messages = [ ]

def display_row(trans):
    console.clear()
    console.print(make_panel(trans))

def make_candidate(e):
    '''
    Create a suggested Entry object to pair with the current Entry and
    a Transaction for the pair.

    Arguments:
        e:  an Entry object derived from a line in a CSV file

    Returns:
        the new Transaction
    '''
    new_entry = Entry(
        date = e.date,
        description = "repl " + e.description,
        column = e.column.opposite(),
        amount = e.amount,
    )
    new_transaction = Transaction()
    new_transaction.entries.append(e) 
    new_transaction.entries.append(new_entry)
    new_transaction.edited = set()
    return new_transaction

def REPL(entries):
    row = 0
    tlist = [make_candidate(e) for e in entries]
    try:
        if not debugging():
            console.set_alt_screen(True)
        while len(tlist) > 0:
            display_row(tlist[row])
            key = click.getchar()
            if key not in all_keys:
                continue
            match key:
                case KEY.PREV:
                    row = (row - 1) % len(tlist)
                case KEY.NEXT:
                    row = (row + 1) % len(tlist)
                case KEY.FILL_DESC:
                    fill_description(tlist[row])
                case KEY.EDIT_DESC | KEY.EDIT_COMMENT | KEY.EDIT_TAGS:
                    edit_field(tlist[row], key)
                case KEY.EDIT_ACCOUNT:
                    edit_account(tlist[row])
                case KEY.MOD_DESC:
                    modify_description(tlist[row])
                case _:
                    continue
    except KeyboardInterrupt:
        pass
    except EOFError:
        pass
    
    console.set_alt_screen(False)

def fill_description(trans):
    '''
    Copy the description from the entry to the transaction
    '''
    trans.description = trans.entries[0].description
    trans.edited.add('description')

def edit_field(trans, key):
    '''
    Use readline to edit the contents of a field in a transaction.  If the
    field is not empty use the current contents to initialize the line.

    Arguments:
        trans:  the transaction to update
        key: the keystroke that triggered the edit (specifies the field)
    '''
    field = field_names[key]
    if s := trans[field]:
        h = lambda: readline.insert_text(s)
        readline.set_startup_hook(h)
    text = input(field + '> ')
    trans[field] = text
    trans.edited.add(field)

def edit_account(trans):
    '''
    Edit the account field on the new entry, using command completion
    to fill in account names.

    TBD:  check for splits, edit the selected split

    Arguments:
        trans:  the transaction to update
    '''
    pass

def modify_description(rec):
    '''
    Get a second keystroke, use it to specify a function to apply to the
    description field.
    '''

    abbrevs_and_articles = {
        '&amp;': '&',
        'And': 'and',
        'For': 'for',
        'In': 'in',
        'Of': 'of',
        'Or': 'or',
        'The': 'the',
    }

    pass
