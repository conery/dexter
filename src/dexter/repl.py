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
from .console import console

tline = '  {date}  {desc:<40s} ; {comm:<20s} # {tags:<20s}'

def make_panel(trans):
    '''
    Create the layout for displaying a transaction.
    '''
    tline = Text(f'{trans.entries[0].date}  ', style='autofill')
    tline.append(Text(f'^P {trans.description:40s}', style='editable'))
    tline.append(' ; ')
    tline.append(Text(f'^N comment           ', style='editable'))
    tline.append(' # ')
    tline.append(Text(f'^G tags        ', style='editable'))
    lines = [tline]
    for e in trans.entries:
        eline = f'    {e.amount} {e.account}'
        lines.append(eline)

    grp = Group(*lines)
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
    EDIT_REGEXP = ctrl('E')
    SET_TAGS = ctrl('G')
    MOD_DESC = ctrl('L')              # mnemonic:  "lambda"
    ACCEPT = ctrl('A')

cmnd_keys = { x[1] for x in vars(KEY).items() if not x[0].startswith('__') }
digit_keys = set('0123456789')
all_keys = cmnd_keys | digit_keys | { '?' }

# Display a single transactions.  If there were any
# issues when making the row they were appended to the message list,
# display that list after the row.

messages = [ ]

def display_row(trans):
    console.clear()
    console.print(make_panel(trans))

def REPL(entries):
    e = entries[0]
    new_entry = Entry(
        date = e.date,
        description = "match " + e.description,
        account = "blank",
        column = e.column.opposite(),
        amount = e.amount,
    )
    new_transaction = Transaction(
        description = "new trans"
    )
    new_transaction.entries.append(e) 
    new_transaction.entries.append(new_entry)
 
    display_row(new_transaction)
