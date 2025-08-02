# Print or update transactions

import logging

from .DB import DB, Transaction, Entry, Tag
from .config import Config
from .console import print_transaction_table, print_csv_transactions, print_journal_transactions
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

    if 'start_date' not in kwargs:
        kwargs['start_date'] = Config.DB.start_date

    return kwargs

# Table mapping action names (from the command line) with functions that
# implement the action:

def not_implemented(recs, args):
    print('not implemented')

actions = {
    'csv':        print_csv_transactions,
    'journal':    print_journal_transactions,
    'repl':       repl,
    'panel':      not_implemented,
    'update':     not_implemented,
    'delete':     not_implemented,
    'set_tag':    not_implemented,
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

    for arg in ['account', 'credit', 'debit']:
        if val := kwargs.get(arg):
            if val.startswith('@'):
                kwargs[arg] = r'\b' + val + r'\b'

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
        # recs = recs.order_by(args.order_by)
        recs = sorted(recs, key=lambda x: x[cls.order_by.get(col)])

    for aname in actions.keys():
        if vars(args).get(aname):
            actions[aname](recs,args)
            break
    else:
        print_transaction_table(recs, args)
