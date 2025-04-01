#  Method for pairing entries to create transactions

import logging
import re

from .DB import DB, Transaction, Entry, Action, Column
from .config import Config
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

    unpaired = DB.select(Entry, tag=Config.unpaired_tag)

    new_transactions = []
    credits = []
    debits = []
    alternatives = []
    unmatched = []

    for entry in unpaired:
        if lst := DB.find_regexp(entry.description):
            if len(lst) > 0:
                alternatives.append(lst[1:])
            regexp = lst[0]
            match regexp.action:
                case Action.T: 
                    new_transactions.append(matching_transaction(entry, regexp))
                case Action.X:
                    if entry.column == Column.cr:
                        credits.append(entry)
                        debits.append(matching_transfer(entry, regexp))
                    else:
                        debits.append(entry)
                        credits.append(matching_transfer(entry, regexp))
                case _:
                    logging.error(f'pair: unknown action {regexp.action} for {entry}')
        else:
            unmatched.append(entry)

    if args.preview:
        logging.info('Matched')
        print_records(new_transactions)
        logging.info('Transfers (credits)')
        print_records(credits)
        logging.info('Transfers (debits)')
        print_records(debits)
        logging.info(f'{len(unmatched)} unmatched')
    else:
        logging.info(f'pair: {len(new_transactions)} matched')
        logging.info(f'pair: {len(credits)} paired')
        save_transactions(new_transactions)

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

def matching_transfer(entry, regexp):
    return Entry()

def save_transactions(lst):
    '''
    Save the new transactions in the database.  We also need to remove the
    #unpaired tag from the first entry and save both entries.

    Arguments:
        lst: a list of new Transaction objects
    '''
    for obj in lst:
        try:
            obj.entries[0].tags.remove(Config.unpaired_tag)
            obj.entries[0].save()
            obj.entries[1].save()
            obj.save()
        except Exception as err:
            logging.error(f'pair: error while saving transaction: {err}')

