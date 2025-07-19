# Print or update transactions

import logging

from .DB import DB, Transaction, Entry
from .config import Config, Tag
from .console import print_transaction_table, print_csv_transactions, print_journal_transactions
from .repl import repl

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
        --repl              show records one at a time in a command line REPL
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

    if args.unpaired:
        args.entry = True
        args.tag = Tag.U.value

    if args.entry:
        cls = Entry
        dct = DB.entry_constraints
        order = DB.entry_order
    else:
        cls = Transaction
        dct = DB.transaction_constraints
        order = DB.transaction_order
    logging.debug(f'select {cls}')

    kwargs = {}
    for name in dct:
        if val := vars(args).get(name):
            kwargs[name] = val
            logging.debug(f'  {name} = {val}')

    if 'start_date' not in kwargs:
        kwargs['start_date'] = Config.start_date

    unused = DB.entry_unused if args.entry else DB.transaction_unused
    for arg in unused:
        if vars(args).get(arg):
            logging.warning(f'select: option not valid for {cls.__name__}: {arg} (ignored)')
    
    recs = DB.select(cls, **kwargs)

    if recs == []:
        return

    if args.order_by:
        recs = recs.order_by(args.order_by)

    for aname in actions.keys():
        if vars(args).get(aname):
            actions[aname](recs,args)
            break
    else:
        print_transaction_table(recs, args)
