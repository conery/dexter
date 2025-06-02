#  Methods for reading and writing database contents

import csv
import logging
import os
from pathlib import Path
import re

from .DB import DB, Account, Entry, Transaction, RegExp, Category, Tag
from .config import Config
from .util import parse_date


class JournalParser:
    '''
    Parse statements in a .journal file, the format used by
    hldeger and other "plain text accounting" apps.

    The algorithm creates one DB document (an Account, a Transaction,
    or an Entry) for each line in the file.  It assumes that when it
    sees a line for an Entry it can append it to the current Transaction.
    '''

    def __init__(self, db_accounts, db_uids):
        '''
        Initialize the data structures that will hold the records
        to insert.

        Arguments:
            db_accounts: set of names of accounts already defined
            db_uids:     set of UIDs of current entries
        '''
        self._accounts = [ Account(name = 'equity', category = Category.Q)]
        self._entries = []
        self._transactions = []

        self._account_types = list(Category.__members__.keys())
        self._account_names = { 'equity' }
        self._abbrevs = { }
        self._transaction_date = None
        self._transaction_total = 0

        if db_accounts:
            self._account_names |= db_accounts
        self._existing_uids = db_uids

    @property
    def account_list(self):
        return self._accounts
    
    @property
    def transaction_list(self):
        return self._transactions

    @property
    def entry_list(self):
        return self._entries

    def parse_file(self, fn):
        '''
        Parse a file, saving account names and transactions in
        instance variables.

        Arguments:
            fn: path to the input file
        '''
        patterns = [
            (r'account', self._new_account),
            (r'\d{4}-\d{2}-\d{2}', self._new_transaction),
            (r'\s+\w+', self._new_entry),
        ]
        with open(fn) as f:
            while line := f.readline():
                cmnd, *comment = re.split(r'[;#]', line.rstrip())
                if len(cmnd) == 0:
                    continue
                try:
                    for pat, func in patterns:
                        if re.match(pat,cmnd):
                            func(cmnd, *comment)
                            break
                    else:
                        raise ValueError('unknown statement')
                except Exception as err:
                    logging.error(f'JournalParser: error in {cmnd}')
                    logging.error(err)

    def _parse_amount(self, s):
        '''
        Convert a string with dollar signs, commas, and periods into a
        dollar amount.
        '''
        s = re.sub(r'[,$]','',s)
        return float(s)
    
    def _new_account(self, cmnd, comment=''):
        '''
        Helper function to create an Account document from the current line.

        Arguments:
           cmnd:  a string with the 'account' command followed by the account name
           comment: the comment field from the line

        Expected format of the command part
           account N C
        where N is the account name and C is a category name
        '''
        logging.debug(f'JournalParser._new_account: {cmnd} {comment}')
        lst = cmnd.split()
        name = lst[1].strip()
        if name == 'equity':
            return

        if name in self._account_names:
            logging.error('JournalParser: duplicate account name: {name}')
            return

        tags = { }
        for seg in comment.split(','):
            if m := re.search(r'(\w+):(.*)', seg):
                tags[m[1]] = m[2].strip()
        if 'type' in tags:
            tags['category'] = tags['type']
        logging.debug(tags)

        acct = Account(
            name = name, 
            category = tags.get('category') or name.split(':')[0],
            abbrev = tags.get('abbrev'),
            parser = tags.get('parser') 
        )
        self._accounts.append(acct)

        self._account_names.add(name)
        if t := tags.get('abbrev'):
            self._abbrevs[t] = name

    def _new_transaction(self, date, comment=''):
        '''
        Helper function to create a Transaction object from the current line.

        Arguments:
           date: the date from the front of the line
           comment: the comment field from the line
        '''
        logging.debug(f'JournalParser._new_transaction {date} {comment}')
        m = re.match(r'(\d{4}-\d{2}-\d{2})(.*)', date)
        self._transaction_date = m.group(1)
        self._transaction_total = 0
        trans = Transaction(
            description = m.group(2).strip(),
        )
        # comment = tokens[0].strip() if tokens else ''
        trans.comment = comment.strip()
        trans.tags = [f'#{s[:-1]}' for s in re.findall(r'\w+:', comment)]
        self._transactions.append(trans)

    def _new_entry(self, cmnd, desc=''):
        '''
        Helper function to create a new Entry object.  Appends the
        new object to the entries list of the most recent Transaction.

        Arguments:
           cmnd: a string with the account name and amount
           comment: the comment field from the line
        '''
        logging.debug(f'JournalParser._new_entry {cmnd} {desc}')
        parts = cmnd.strip().split()
        acct = parts[0]

        if acct not in self._account_names:
            logging.error(f'JournalParser:  unknown account name: {acct}')
            return

        if len(parts) > 1:
            amount = self._parse_amount(parts[1])
            self._transaction_total += amount
        else:
            amount = -self._transaction_total

        tags = re.findall(r'\w+:', desc)
        col = 'credit' if amount < 0 else 'debit'
        trans = self._transactions[-1]
        if trans.isbudget:
            tags.append(Tag.B)
        entry = Entry(
            date = self._transaction_date,
            description = desc.strip(),
            account = acct,
            column = col,
            amount = abs(amount),
            tags = tags,
        )

        if entry.hash in self._existing_uids:
            logging.debug(f'skipping existing entry {entry}')
            return
        
        trans.entries.append(entry)
        self._entries.append(entry)

