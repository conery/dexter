#  Methods for reading and writing database contents

import logging
import re

from .schema import *

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

