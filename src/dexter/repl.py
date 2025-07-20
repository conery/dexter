# Command line REPL used by scripts that review transactions one at a time

import click
from collections import namedtuple
from curses.ascii import ESC, ctrl, unctrl
import logging
import readline
import re

from rich.console import Group
from rich.panel import Panel
from rich.pretty import pprint
from rich.text import Text

import heapq
from thefuzz import fuzz

from .DB import DB, Transaction, Entry, Account, Category, Action
from .config import Config, Tag
from .console import console, format_amount
from .util import debugging

# A tuple that holds descriptions of previous entries with similar descriptions

PrevEntry = namedtuple('PrevEntry', ['description', 'date', 'tags', 'account'])

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
    RESET = ctrl('R')
    ACCEPT = ctrl('A')

cmnd_keys = { x[1] for x in vars(KEY).items() if not x[0].startswith('__') }
digit_keys = set('0123456789')
all_keys = cmnd_keys | digit_keys | { '?' }

field_names = {
    KEY.EDIT_DESC: 'description',
    KEY.EDIT_ACCOUNT: 'account',
    KEY.EDIT_COMMENT: 'comment',
    KEY.EDIT_TAGS: 'tags',
}

###
#
# Top level method for reviewing transactions
#

def repl(recs, args):
    '''
    The top level function, called from main when the command 
    is "review". 

    Arguments:
        recs: List of Entry objects provided by `select`
        args: Namespace object with command line arguments.
    '''
    # DB.open(args.dbname)
    # unpaired = DB.select(Entry, tag=Tag.U).order_by('date')
    account_parts = list(DB.account_name_parts(Category.E) | DB.account_name_parts(Category.I))
    account_names = DB.account_names(Category.E) | DB.account_names(Category.I)
    previous_entries = [e for e in DB.select(Entry, start_date=Config.DB.start_date) if e.tref and e.account in DB.real_accounts and len(e.description) > 10]
    logging.debug(f'prev {previous_entries}')
    if debugging():
        print('account parts:')
        pprint(account_parts)
        print('account names:')
        pprint(account_names)
    readline.parse_and_bind('tab: complete')
    readline.set_completer(completer_function(account_parts))
    row = 0
    # tlist = [make_candidate(e, args.fill_mode) for e in unpaired if matching(e,args)]
    tlist = [make_candidate(e, previous_entries) for e in recs]
    logging.debug(f'tlist {tlist}')
    try:
        if not debugging():
            console.set_alt_screen(True)
        while len(tlist) > 0:
            display_row(tlist[row])
            key = click.getchar()
            if key not in all_keys:
                continue
            match key:
                case '?':
                    show_help(all_keys)
                    continue
                case KEY.PREV:
                    if confirmed(tlist[row]):
                        row = (row - 1) % len(tlist)
                case KEY.NEXT:
                    if confirmed(tlist[row]):
                        row = (row + 1) % len(tlist)
                case KEY.FILL_DESC:
                    tlist[row].mode = (tlist[row].mode + 1) % 3
                case KEY.EDIT_DESC | KEY.EDIT_COMMENT | KEY.EDIT_TAGS:
                    edit_field(tlist[row], key)
                case KEY.EDIT_ACCOUNT:
                    edit_account(tlist[row], account_names)
                case ch if ch in digit_keys:
                    copy_previous(tlist[row], ch)
                case KEY.RESET:
                    reset_transaction(tlist[row])
                case KEY.ACCEPT:
                    if verify_and_save_transaction(tlist[row]):
                        del tlist[row]
                        if tlist:
                            row = row % len(tlist)
                case _:
                    continue
    except KeyboardInterrupt:
        pass
    except EOFError:
        pass
    
    console.set_alt_screen(False)

def show_help(keys):
    messages.append('\n editing commands:')
    for key, field in field_names.items():
        if key not in keys:
            continue
        messages.append(f'   {unctrl(key)} {field}')

PANEL_WIDTH = 120
DESC_WIDTH = 65
COMMENT_WIDTH = 20
TAGS_WIDTH = 15
ACCT_WIDTH = 30

def padded(s, w):
    '''
    Adjust s so it is n chars long, either by truncating strings
    longer than n or by add spaces to the end 
    '''
    if len(s) > w:
        return s[:w]
    else:
        return s + ' '*(w-len(s))

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
        line += Text(padded(acct,ACCT_WIDTH))
        line += Text(amt)
        line += Text(' ; ')
        line += Text(e.description[:DESC_WIDTH])
        return line
    
    def a2line():
        return indent + text['account']
    
    desc = trans.description or suggested(trans)

    text = {
        'description': Text(padded(desc,DESC_WIDTH)),
        'comment': Text(padded(trans.comment or ' comment ', COMMENT_WIDTH)),
        'tags': Text(padded(trans.tags or ' tags ', TAGS_WIDTH)),
        'account': Text(padded(trans.entries[1].account or ' account ', ACCT_WIDTH))
    }

    for f, t in text.items():
        t.style = 'edited' if f in trans.edited else 'editable'

    indent = Text('    ')
    grp = Group(tline(), a1line(), a2line())
    return Panel(grp, width=PANEL_WIDTH, padding=1, title='New Transaction', title_align="left")

# Set up command line completion

def completer_function(tokens):

    def completer(text, state):
        matches = [s for s in tokens if s.startswith(text)]
        return matches[state]

    return completer

# Display a single entry.  If there were any
# issues when making the row they were appended to the message list,
# display that list after the row.

messages = [ ]

def display_row(trans):
    console.clear()
    console.print(make_panel(trans))
    console.print()
    for i, x in enumerate(trans.similar):
        line = f'   ({i})  {x.date}'
        line += f'  {x.description[:40]:40s}'
        line += f'  {DB.abbrev(x.account):20s}'
        line += f'  {x.tags}'
        console.print(line)
    if messages:
        for m in messages:
            console.print(m)
    messages.clear()
    console.print()

def matching(e, args):
    '''
    Return True if the description and account in entry e match
    patterns specified on the command line.

    Arguments:
        e:  an Entry object derived from a line in a CSV file
        args:  command line arguments

    '''
    # Relies on the fact that the default patterns are empty strings and a
    # regular expression search when the pattern is empty is always True.

    return re.search(args.description, e.description, re.I) and re.search(args.account, e.account, re.I)

# def make_candidate(e, n):
def make_candidate(e, prev):
    '''
    Create a suggested Entry object to pair with the Entry e and
    a Transaction for the pair.

    Arguments:
        e:  an Entry object derived from a line in a CSV file
        prev:  a list of previously defined Entry objects

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
    new_transaction.mode = Config.Select.fill_mode
    new_transaction.similar = find_similar(e, prev)
    for x in new_transaction.similar:
        logging.debug(f'similar: {x}')
    return new_transaction

def find_similar(e, prev):
    '''
    Find descriptions of previous entries with similar descriptions

    Arguments:
        e:  a new entry with a description from a CSV file
        prev: a list of previously paired entries
    '''
    lst = []
    dset = set()
    for p in prev:
        score = fuzz.token_set_ratio(e.description, p.description)
        if score >= Config.Select.min_similarity and p.description not in dset:
            t = p.tref
            heapq.heappush(lst, PrevEntry(t.description, p.date, t.tags, t.entries[1].account))
            dset.add(p.description)
    return heapq.nlargest(Config.Select.max_similar, lst)

def suggested(trans):
    '''
    Use the transaction's fill mode to create a string to display
    in the description box
    '''
    match trans.mode:
        case 0:  
            desc = ' description '
        case 1:  
            desc = trans.entries[0].description
        case 2:  
            desc = apply_regexp(trans.entries[0].description)
    return desc

def apply_regexp(desc):
    '''
    If one of "fill" regexps matches this description use it, otherwise
    apply all of the "sub" regexps.
    '''
    if e := DB.find_first_regexp(desc, Action.F):
        logging.debug(f'review: apply F {e} "{desc}"')
        desc = e.apply(desc)
    else:
        logging.debug(f'review: apply S "{desc}"')
        desc = DB.apply_all_regexp(desc)
    return desc

def edit_field(trans, key):
    '''
    Use readline to edit the contents of a field in a transaction.  If the
    field is not empty use the current contents to initialize the line.

    Arguments:
        trans:  the transaction to update
        key: the keystroke that triggered the edit (specifies the field)
    '''
    field = field_names[key]
    alt = suggested(trans) if (field == 'description' and trans.mode) else ""
    s = trans[field] or alt
    h = lambda: readline.insert_text(s)
    readline.set_startup_hook(h)
    text = input(field + '> ')
    trans[field] = text
    if text:
        trans.edited.add(field)
    else:
        trans.edited.discard(field)

def edit_account(trans, names):
    '''
    Edit the account field on the new entry, using command completion
    to fill in account names.

    TBD:  check for splits, edit the selected split

    Arguments:
        trans:  the transaction to update
        names:  list of account names
    '''
    entry = trans.entries[1]
    s = entry.account or ""
    h = lambda: readline.insert_text(s)
    readline.set_startup_hook(h)
    text = input('account> ')

    if len(text) == 0:
        entry.account = text
        trans.edited.discard('account')
        return
    
    # messages.append(f'"{text}" in {names}')
    if accts := names.get(text):
        # messages.append(f'{accts}')
        if len(accts) > 1:
            messages.append(f'[red]ambiguous, choose from {accts}')
        else:
            entry.account = list(accts)[0]
            trans.edited.add('account')
    else:
        messages.append(f'[red]unknown account: {text}')

def copy_previous(trans, key):
    '''
    Copy the description, account, and tags from a previous transaction.

    Arguments:
        trans:  the transaction to update
        key: the digit key that selected the previous transaction
    '''
    n = int(key)
    if n < len(trans.similar):
        prev = trans.similar[n]
        entry = trans.entries[1]
        entry.account = prev.account
        trans.description = prev.description
        trans.edited |= {'account','description'}
        if prev.tags:
            trans.tags = prev.tags
            trans.edited.add('tags')
        trans.copy = prev

def reset_transaction(trans):
    '''
    Reinitialize the fields of the transaction.
    '''
    trans.description = ''
    trans.comment = ''
    trans.tags = []
    trans.entries[1].account = ''
    trans.edited = set()

def confirmed(trans):
    '''
    User has hit up or down arrow.  If there are changes to a field
    ask if they should be saved.  Return True if the move should be
    taken, False to continue editing the current transaction.
    '''
    if trans.edited:
        console.out('\nDiscard changes? [yN] ', end='', style='blue italic')
        key = click.getchar()
        if key in 'yY':
            reset_transaction(trans)
            return True
        else:
            return False
    else:
        return True

def verify_and_save_transaction(trans):
    '''
    Verify the user has supplied required fields and if so save the
    new transaction.  Return True if the transaction can be deleted
    from the list.

    Arguments:
        trans:  the transaction to save
    '''
    missing = []
    if 'description' not in trans.edited:
        if trans.mode > 0:
            trans.description = suggested(trans)
        else:
            missing.append('description')
    if 'account' not in trans.edited:
        missing.append('account')

    if missing:
        messages.append(f'[red]Missing required fields: {", ".join(missing)}')
        return False
    else:
        if 'tags' in trans.edited:
            trans.tags = [s if s.startswith('#') else f'#{s}' for s in re.split(r'[\s,]+', trans.tags)]
        trans.entries[0].tags.remove(Tag.U)
        DB.save_records([trans])
        return True
