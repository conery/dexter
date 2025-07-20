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

        # Make a list of the special tags without the # at the front
        self._special_tags = [x.value[1:] for x in Tag.__members__.values()]

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
        with open(fn) as f:
            while line := f.readline():
                if len(line) == 1 or line.startswith((';','#')):
                    continue
                if ';' in line:
                    parts = line.split(';')
                    cmnd = parts[0].rstrip()
                    comment = parts[1]
                else:
                    cmnd = line.rstrip()
                    comment = ''
                tokens = cmnd.split()
                logging.debug(f'parse_file {tokens}')
                try:
                    if re.match(r'\d{4}-\d{2}-\d{2}', line):
                        self._new_transaction(tokens, comment)
                    elif re.match(r'^\s+', line):
                        self._new_posting(tokens, comment)
                    else:
                        self._parse_directive(tokens, comment)
                except Exception as err:
                    logging.error(f'JournalParser: error in {line.rstrip()}')
                    logging.error(err)
    
    def _parse_directive(self, tokens, comment):
        '''
        Helper function to process a directive.

        Arguments:
           tokens:  a list of tokens made from splitting the command
           comment:  the string following a semicolon
        '''
        if tokens[0] == 'account':
            self._new_account(tokens[1:], comment)
        else:
            raise ValueError(f'directive not implemented: {tokens[0]}')
        
    def _new_account(self, tokens, comment):
        '''
        Create a new account.

        Arguments:
           tokens:  a list of tokens following the word "account" in the current line
           comment:  the string following a semicolon
        '''
        logging.debug(f'JournalParser._new_account: {tokens}')
        name = tokens[0]
        logging.debug(f'JournalParser._new_account: {name}')
        if name == 'equity':
            return
        if name in self._account_names:
            logging.error(f'JournalParser: duplicate account name: {name}')
            return
        tags = self._parse_tags(comment)
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

    def _new_transaction(self, tokens, comment):
        '''
        Helper function to create a Transaction object from the current line.

        Arguments:
           tokens:  a list of tokens made from splitting the current line
           comment:  the string following a semicolon
        '''
        logging.debug(f'JournalParser._new_transaction {tokens} {comment.rstrip()}')
        self._transaction_date = tokens[0]
        self._transaction_total = 0
        trans = Transaction(
            description = ' '.join(tokens[1:])
        )
        trans.comment = comment.strip()
        # # tags = self._parse_tags(comment)
        # if 'pending:' in comment:
        #     # trans.tags = list(tags.keys())
        #     trans.tags = [ Tag.P.value ]
        trans.tags = list(self._parse_tags(comment).keys())
        self._transactions.append(trans)

    def _new_posting(self, tokens, comment):
        '''
        Helper function to create a new Entry object.  Appends the
        new object to the entries list of the most recent Transaction.

        Arguments:
           tokens:  a list of tokens made from splitting the current line
           comment:  the string following a semicolon
        '''
        logging.debug(f'JournalParser._new_posting {tokens} {comment}')
        acct = tokens[0].strip()

        if acct not in self._account_names:
            logging.error(f'JournalParser:  unknown account name: {acct}')
            return

        if len(tokens) > 1:
            amount = self._parse_amount(tokens[1])
            self._transaction_total += amount
        else:
            amount = -self._transaction_total

        tags = list(self._parse_tags(comment).keys())
        col = 'credit' if amount < 0 else 'debit'
        trans = self._transactions[-1]
        if trans.isbudget:
            tags.append(Tag.B)
        entry = Entry(
            date = self._transaction_date,
            description = comment.strip(),
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

    def _parse_amount(self, s):
        '''
        Convert a string with dollar signs, commas, and periods into a
        dollar amount.
        '''
        s = re.sub(r'[,$]','',s)
        return float(s)

    def _parse_tags(self, comment):
        '''
        Look for tags in the comment portion of a line.  Adds a hash tag in
        front of special tags.

        Arguments:
            comment:  characters following a semicolon on the current line

        Returns:
            a dictionary of tags and their values
        '''
        src = comment.strip()
        dct = { }
        for part in src.split(','):
            if ':' in part:
                tag = re.search(r'(\w+):', part)[1]
                if tag in self._special_tags:
                    tag = '#' + tag
                val = part[part.index(':')+1:].strip()
                dct[tag] = val
                logging.debug(f'parse_tags:  "{tag}" = "{val}"')
        return dct
