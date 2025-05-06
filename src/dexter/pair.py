#  Method for pairing entries to create transactions

import logging
import re

from .DB import DB, Transaction, Entry, Action, Column
from .config import Config, Tag
from .console import print_records

def pair_entries(args):
    '''
    The top level function, called from main when the command 
    is "pair". 

    Arguments:
        args: Namespace object with command line arguments.
    '''
    logging.info(f'Finding matches for unpaired entries')
    logging.debug(f'pair {vars(args)}')

    unpaired = DB.select(Entry, tag=Tag.U)

    new_transactions = []
    credits = {}
    debits = {}
    alternatives = []
    unmatched = []

    for entry in sorted(unpaired, key=lambda e: e.date):
        if lst := DB.find_regexp(entry.description):
            if len(lst) > 0:
                alternatives.append(lst[1:])
            regexp = lst[0]
            match regexp.action:
                case Action.T: 
                    new_transactions.append(matching_transaction(entry, regexp))
                case Action.X:
                    xfer_part(entry, regexp, credits, debits)
                case _:
                    logging.error(f'pair: unknown action {regexp.action} for {entry}')
        else:
            unmatched.append(entry)

    xfers = combine_xfer_parts(credits, debits)

    if args.preview:
        logging.info(f'{len(new_transactions)} Matched')
        print_records(new_transactions)
        logging.info(f'{len(xfers)} Transfers')
        print_records(xfers)
        logging.info(f'{len(unmatched)} unmatched')
    else:
        logging.info(f'pair: {len(new_transactions)} matched')
        logging.info(f'pair: {len(xfers)} paired')
        logging.info(f'pair: {len(unmatched)} unmatched')
        save_matched_transactions(new_transactions)
        save_xfers(xfers)

def matching_transaction(entry, regexp):
    '''
    A description from a CSV file matched a regular expression.  Use the match
    to create a new Entry and pair with the the existing one in a new Transaction.
    '''
    new_entry = Entry(
        date = entry.date,
        description = "match " + entry.description,
        account = regexp.acct,
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
    for obj in lst:
        try:
            obj.entries[0].tags.remove(Tag.U)
            obj.entries[0].save()
            obj.entries[1].save()
            obj.save()
        except Exception as err:
            logging.error(f'pair: error while saving transaction: {err}')

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
                t = Transaction(description=f'{e1.note} {e1.account} ⧓ {e2.account}')
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
        try:
            for e in obj.entries:
                e.tags.remove(Tag.U)
                e.save()
            obj.save()
        except Exception as err:
            logging.error(f'pair: error saving transfer: {obj}')
