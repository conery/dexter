# Print or update transactions

import csv
import logging
import sys

from .DB import DB, Transaction, Entry, Tag
from .config import Config
from .console import console, print_transaction_table, print_csv_transactions, print_journal_transactions
from .repl import repl


def validate_options(args):
    '''
    Helper function to check combinations of command line arguments.

    Returns the type of object to select and a dictionary that maps command line 
    constraint names to attribute names for the type.
    '''
    if args.unpaired:
        args.entry = True
        args.tag = Tag.U.value

    if args.entry:
        for opt in ['journal','credit','debit']:
            if getattr(args,opt):
                raise ValueError(f'select: --{opt} cannot be used with --entry')
        cls = Entry
        tags = { x.name for x in Tag }
        if args.tag in tags:
            args.tag = Tag[args.tag].value
    else:
        for opt in ['repl']:
            if getattr(args,opt):
                raise ValueError(f'select: --{opt} requires --entry')
        cls = Transaction
    logging.debug(f'select {cls}')

    unused = {'comment'} if args.entry else {'column'}
    for arg in unused:
        if vars(args).get(arg):
            raise ValueError(f'select: option not valid for {cls.__name__}: {arg}')

    return cls

def collect_parameters(cls, args):
    '''
    Helper function to set up search parameters based on command
    line arguments.
    '''
    kwargs = {}
    for name in cls.constraints:
        if val := vars(args).get(name):
            kwargs[name] = val
            logging.debug(f'  {name} = {val}')

    if ('start_date' not in kwargs) and ('date' not in kwargs):
        kwargs['start_date'] = Config.DB.start_date

    return kwargs

def print_unpaired_csv(recs, args):
    '''
    Special case for CSV output, reformats unknowns for easier display in
    a spreadsheet.
    '''
    colnames = ['date','account','amount','category','description','note']
    writer = csv.DictWriter(sys.stdout, colnames)
    writer.writeheader()
    for rec in recs:
        desc = rec.description[:rec.description.find(' §')]
        row = [rec.date, DB.abbrev(rec.account), -rec.value, 'fill me', desc,'']
        writer.writerow(dict(zip(colnames,row)))

# Delete selected records

def delete(recs, args):
    console.print('[blue]Delete Records')
    for obj in recs:
        console.print(f'  {obj.row()}')
        if not args.preview:
            obj.delete()

# Table mapping action names (from the command line) with functions that
# implement the action.

def not_implemented(recs, args):
    print('not implemented')

actions = {
    'csv':        print_csv_transactions,           # defined in .console
    'journal':    print_journal_transactions,       # defined in .console
    'repl':       repl,                             # defined in .repl
    'panel':      not_implemented,
    'delete':     delete,
}

def select(args):
    '''
    Select records using constraints specified on the command line.

    By default select transactions, but if `--entry` is specified search for
    individual debits or credits.

    The default is to display the selection in a table in the terminal window.
    Alternate actions are:

        --csv               display records as CSV (for import to a spreadsheet)
        --journal           display using Journal format [transactions only]
        --repl              show records one at a time in a command line REPL (entry only)
        --panel             display records in a GUI
        --update            bulk update of a specified attribute in all selected records
        --tag               add or remove a tag on all selected records
        --delete            delete all selected records

    Constraints:

        --description S     description must include string S
        --comment S         comment must include string S (transactions only)

        --date D            date must equal D
        --start_date D      date on or after D
        --end_date D        date on or before D
        --month M           define start and end date based on month name

        --account A         account name pattern
        --column C          ledger column (credit or debit) (postings only)

        --amount N          amount must equal N
        --min_amount N      amount greater than or equal to N
        --max_amount N      amount less than or equal to N

    Other options:

        --abbrev            show abbreviated account names
        --order_by C        sort records by attribute C (default: date)
        --total             print total amount of all items
        --unpaired          sets --entry and --tag #unpaired
    '''
    DB.open(args.dbname)

    cls = validate_options(args)
    kwargs = collect_parameters(cls, args)

    logging.debug(f'kwargs {str(kwargs)}')

    if (cls == Transaction) and ('account' in kwargs):
        acct = kwargs.pop('account')
        debits = DB.select(cls, **(kwargs | {'debit': acct}))
        credits = DB.select(cls, **(kwargs | {'credit': acct}))
        recs = list(debits) + list(credits)
    else:
        recs = list(DB.select(cls, **kwargs))

    if len(recs) == 0:
        return

    if col := args.order_by:
        recs = sorted(recs, key=lambda x: x[cls.order_by.get(col)])

    # Find the intersection of the set of action names and the set of
    # command line options that have values -- if one of the actions was
    # specified the intersection will have that action name.
    #
    # Special case -- printing unpaired in CSV reformats entries for
    # more readable display in spreadsheet

    if args.unpaired and args.csv:
        print_unpaired_csv(recs, args)
    elif aname := set(actions.keys()) & {x for (x,y) in vars(args).items() if y}:
        actions[aname.pop()](recs, args)
    else:
        print_transaction_table(recs, args)
