#  Methods for reading and writing database contents

import json
import logging
from pathlib import Path
import re

from .DB import DB, Account, Entry, Transaction, Category
# from .schema import *

###
#
# Methods for exporting and importing records from a text file.  
#

def export_records(args):
    '''
    The top level function, called from main when the command 
    is "export".  Writes records from all collections to a single
    JSON file.

    Arguments:
        args: Namespace object with command line arguments.
    '''
    logging.info(f'Exporting to {args.file}')
    logging.debug(f'export {vars(args)}')
    try:
        mode = 'w' if args.force else 'x'
        with open(args.file, mode) as f:
            DB.save_records(f)
    except FileExistsError as err:
        logging.error(f'file exists: {args.file}, use --force to overwrite')
        exit(1)

def import_records(args):
    '''
    The top level function, called from main when the command 
    is "import".  Redirects to the method that will load the data,
    using the file name extension or command line argument to 
    determine the input file format.

    Arguments:
        args: Namespace object with command line arguments.
    '''
    logging.debug(f'import {vars(args)}')

    p = Path(args.file)
    fmt = args.format or p.suffix[1:]
    match fmt:
        case 'json': import_json(p)
        case 'journal': import_journal(p)
        case _: logging.error(f'init: unknown file extension:{p.suffix}')

# Import records from a JSON file (created by a previous call to
# export_records)

def import_json(fn: Path):
    '''
    Read accounts and transactions from a JSON file.  Erases any
    previous documents in the database.

    Arguments:
        fn: path to the input file
    '''
    logging.info(f'DB:importing JSON file:{fn}')
    DB.erase_database()

    with open(fn) as f:
        for line in f:
            try:
                sep = line.find(':')
                collection = line[:sep]
                doc = line[sep+1:].strip()
                DB.add_record(collection, doc)
            except Exception as err:
                logging.error(err)

# Import records from a .journal file

def import_journal(fn: Path):
    '''
    Read accounts and transactions from a plain text accounting
    (.jorurnal) file.  Erases any previous documents in the database.

    Arguments:
        fn: path to the input file
    '''
    logging.info(f'DB:importing journal file:{fn}')
    DB.erase_database()
    for obj in JournalParser().parse_file(fn):
        obj.save()

def parse_amount(s):
    '''
    Convert a string with dollar signs, commas, and periods into a
    dollar amount.
    '''
    s = re.sub(r'[,$]','',s)
    return float(s)

class JournalParser:
    '''
    Translate statements in a .journal file (the format used by
    hldeger and other "plain text accounting") apps.

    The algorithm creates one DB document (an Account, a Transaction,
    or an Entry) for each line in the file.  It assumes that when it
    sees a line for an Entry it can append it to the current Transaction.
    '''

    def __init__(self):
        '''
        Initialize the data structures that will hold the records
        to insert.
        '''
        self.accounts = []
        self.entries = []
        self.transactions = []

        self.account_types = list(Category.__members__.keys())
        self.account_names = set()
        self.transaction_date = None

    # def validate_account(self, acct):
    #     parts = acct.split(':')
    #     if parts[0] not in self.account_types:
    #         raise ValueError(f'unknown account type: {parts[0]}')

    def new_account(self, cmnd, comment):
        '''
        Helper function to create an Account document from the current line.

        Expected format:
           account G N
        where G is a single-letter account type and N is the account name.
        '''
        logging.debug(f'JournalParser.new_account "{cmnd}"')
        _, cat, spec = cmnd.split()
        assert cat in self.account_types, f'  (unknown category: {cat})'
        assert spec not in self.account_names, f'  (duplicate account name: {spec})'
        acct = Account(
            name=spec, 
            category=cat,
        )
        if len(comment) > 0:
            acct.note = comment[0].strip()
        self.accounts.append(acct)
        self.account_names.add(spec)

    def new_transaction(self, cmnd, comment):
        '''
        Helper function to create a Transaction object from the current line.
        '''
        logging.debug(f'JournalParser.new_transaction "{cmnd}"')
        m = re.match(r'(\d{4}-\d{2}-\d{2})(.*)', cmnd)
        self.transaction_date = m.group(1)
        trans = Transaction(
            description = m.group(2).strip(),
        )
        if len(comment) > 0:
            trans.comment = comment[0].strip()
        self.transactions.append(trans)

    def new_entry(self, cmnd, comment):
        '''
        Helper function to create a new Entry object.  Appends the
        new object to the entries list of the most recent Transaction
        (which means it raises an exception if there is no Transaction).
        '''
        logging.debug(f'JournalParser.new_entry {cmnd}')
        acct, amt = cmnd.split()
        # self.validate_account(acct)
        if acct not in self.account_names:
            raise ValueError(f'unknown account: {acct}')
        amount = parse_amount(amt)
        desc = comment[0].strip() if comment else ''
        col = 'credit' if amount < 0 else 'debit'
        trans = self.transactions[-1]
        entry = Entry(
            uid = '',               # UIDs not needed in .journal files
            date = self.transaction_date,
            description = desc,
            account = acct,
            column = col,
            amount = abs(amount),
        )
        trans.entries.append(entry)
        self.entries.append(entry)

    def parse_file(self, fn):
        '''
        Parse a file, saving account names and transactions in
        instance variables.

        Arguments:
            fn: path to the input file
        '''
        patterns = [
            (r'account', self.new_account),
            (r'\d{4}-\d{2}-\d{2}', self.new_transaction),
            (r'\s+\w+', self.new_entry),
        ]
        with open(fn) as f:
            while line := f.readline():
                cmnd, *comment = re.split(r'[;#]', line.rstrip())
                if len(cmnd) == 0:
                    continue
                try:
                    for pat, func in patterns:
                        if re.match(pat,cmnd):
                            func(cmnd,comment)
                            break
                    else:
                        raise ValueError('unknown statement')
                except Exception as err:
                    logging.error(f'JournalParser: error in {cmnd}')
                    logging.error(err)
            logging.debug(f'End of file')

        # return objects in the order we want them saved
        return self.accounts + self.entries + self.transactions

###
#
# Top level method for parsing a CSV file to add new records to a DB
#

def add_records(args):
    '''
    The top level function, called from main when the command 
    is "add".  Parses one or more CSV files to create new Entry
    documents.

    Arguments:
        args: Namespace object with command line arguments.
    '''
    logging.info(f'add {vars(args)}')
