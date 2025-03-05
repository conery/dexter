#  Methods for reading and writing database contents

import logging
import re

from .schema import *

class JournalParser:
    '''
    Translate statements in a .journal file (the format used by
    hldeger and other "plain text accounting") apps
    '''

    def __init__(self):
        '''
        Initialize the data structures that will hold the records
        to insert.
        '''
        self.accounts = []
        self.posts = []
        self.transactions = []

        self.account_types = [x.value for x in AccountType.__members__.values()]

    def new_account(self, line):
        try:
            _, spec = line.split()
            grp = re.match(r'(\w+):', spec).group(1)
            assert grp in self.account_types, f'  (unknown group: {grp})'
            acct = Account(name=spec, group=grp)
            self.accounts.append(acct)
            acct.save()
            logging.debug(f'JournalParser.new_account {spec}')
        except Exception as err:
            logging.error(f'JournalParser.new_account: error in {line}')
            logging.error(err)

    def new_transaction(self, line):
        logging.debug(f'JournalParser.new_transaction {line}')

    def new_post(self, line):
        logging.debug(f'JournalParser.new_post {line}')

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
            (r'\s+\w+', self.new_post),
        ]
        with open(fn) as f:
            while line := f.readline():
                if len(line) == 1 or line[0] in '#;':
                    continue
                for pat, func in patterns:
                    if re.match(pat,line):
                        func(line.strip())
                        break
                else:
                    logging.error(f'error parsing "{line.strip()}"')
        return {
            'accounts': self.accounts,
            'posts':  self.posts,
            'transactions': self.transactions,
        }
