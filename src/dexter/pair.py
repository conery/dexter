#  Method for pairing entries to create transactions

import logging
import re

from .DB import DB, Transaction, Entry, Action, Column, Tag
# from .config import Tag
from .console import print_records, print_grid

def pair_entries(args):
    '''
    The top level function, called from main when the command 
    is "pair". 

    Arguments:
        args: Namespace object with command line arguments.
    '''
    DB.open(args.dbname)
    logging.debug(f'pair {vars(args)}')

    unpaired = DB.select(Entry, tag=Tag.U.value)

    new_transactions = []
    credits = {}
    debits = {}
    unmatched = []
    fillable = []

    for entry in unpaired:
        logging.debug(f'pair: find regexp for {entry.description}')
        if regexp := DB.find_first_regexp(entry.description, Action.T):
            logging.debug(f'  found {regexp}')
            if trans := matching_transaction(entry, regexp):
                logging.debug(f'  new transaction: {trans.description}')
                new_transactions.append(trans)
            else:
                logging.debug('    apply failed')
                unmatched.append(entry)
        elif regexp := DB.find_first_regexp(entry.description, Action.X):
            logging.debug(f'  xfer {regexp}')
            xfer_part(entry, regexp, credits, debits)
        elif regexp := DB.find_first_regexp(entry.description, Action.F):
            logging.debug(f'  fill {regexp}')
            fillable.append(entry)
        else:
            logging.debug(f'    no match')
            unmatched.append(entry)

    xfers = combine_xfer_parts(credits, debits)

    if args.preview:
        preview_transactions(new_transactions)
        preview_transfers(xfers)
        preview_unmatched(fillable, "Will be matched during review")
        preview_unmatched(unmatched, "Unmatched")

        unpaired_xfers = []
        for lst in list(debits.values()) + list(credits.values()):
            for e in lst:
                unpaired_xfers.append(e)
        preview_unmatched(unpaired_xfers, "Unpaired xfer")
    else:
        logging.info(f'pair: {len(new_transactions)} matched')
        logging.info(f'pair: {len(xfers)} paired')
        logging.info(f'pair: {len(fillable)} to be filled')
        logging.info(f'pair: {len(unmatched)} unmatched')
        save_matched_transactions(new_transactions)
        save_xfers(xfers)

def preview_transactions(lst):
    any(t.clean() for t in lst)
    print_records(lst, name='Matched', count=len(lst))

def preview_transfers(lst):
    any(t.clean() for t in lst)
    print_records(lst, name='Transfers', count=len(lst))

def preview_unmatched(lst, title):
    print_grid([[DB.abbrev(e.account), e.description] for e in lst], name=title, count=len(lst))

def matching_transaction(entry, regexp):
    '''
    Helper function for pair_entries.  A record from a CVS file matches a regular
    expression.  Use the match to create a new Entry object and pair it with the 
    existing one in a new Transaction.

    Arguments:
        entry:  the Entry object for the CSV record
        regexp:  the RegExp object for the matching regular expression

    Returns:
        a new Transaction object or None if the account name in the RegExp is invalid
    '''
    acct = DB.fullname(regexp.acct)
    if acct is None:
        logging.error(f'pair: unknown account name {regexp.acct} in regexp')
        new_transaction = None
    else:
        new_entry = Entry(
            date = entry.date,
            description = "match " + entry.description,
            account = acct,
            column = entry.column.opposite(),
            amount = entry.amount,
        )
        new_transaction = Transaction(
            description = regexp.apply(entry.description)
        )
        new_transaction.entries.append(entry)      # IMPORTANT: add original entry first
        new_transaction.entries.append(new_entry)
    return new_transaction

def save_matched_transactions(lst):
    '''
    Save the new transactions in the database.  We also need to remove the
    #unpaired tag from the first entry and save both entries.

    Arguments:
        lst: a list of new Transaction objects
    '''
    # for obj in lst:
    #     try:
    #         obj.entries[0].tags.remove(Tag.U)
    #         obj.entries[0].save()
    #         obj.entries[1].save()
    #         obj.save()
    #     except Exception as err:
    #         logging.error(f'pair: error while saving transaction: {err}')
    for obj in lst:
        obj.entries[0].tags.remove(Tag.U.value)
    DB.save_records(lst)

def xfer_part(entry, regexp, credits, debits):
    '''
    Add the entry to one of the dictionaries that holds transfer parts,
    using the amount as the key.

    Note: put the result of applying the regexp in a new 'note' field of the
    entry.  This field is not part of the model and won't be saved with
    the updated Entry.
    '''
    entry.note = regexp.apply(entry.description)
    key = str(entry.amount)
    dct = credits if entry.column == Column.cr else debits
    dct.setdefault(key, [])
    dct[key].append(entry)

def combine_xfer_parts(credits, debits):
    '''
    Candidates for the two ends of a transfer are in dictionaries indexed
    by amount.  Iterate over the dictionaries to find matching ends.

    Arguments:
        credits:  dictionary with credit halves
        debits:   dictionary with debit halves
    '''
    logging.debug(f'combining {len(credits)} credits with {len(debits)} debits')
    logging.debug(credits)
    logging.debug(debits)
    res = []
    for amt, clist in credits.items():
        logging.debug(f'amt {amt} entries {clist}')
        if dlist := debits.get(amt):
            while clist and dlist:
                e1 = clist.pop(0)
                e2 = dlist.pop(0)
                logging.debug('(%s %s) paired with (%s %s)', e1.account, e1.description, e2.account, e2.description)
                t = Transaction(description=f'{e1.note}')
                t.entries += [e1,e2]
                res.append(t)
    return res

def save_xfers(lst):
    '''
    Save the new transactions formed by combining two transfer parts.

    Arguments:
        lst: the list of transactions
    '''
    for obj in lst:
        for e in obj.entries:
            e.tags.remove(Tag.U.value)
    DB.save_records(lst)
