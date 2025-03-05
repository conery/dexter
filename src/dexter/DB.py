# Database schema and API

# from enum import Enum
import logging
# from mongoengine import *

from .io import JournalParser
from .schema import *

# class AccountType(Enum):
#     EQUITY = 'equity'
#     INCOME = 'income'
#     ASSET = 'asset'
#     EXPENSE = 'expense'
#     LIABILITY = 'liability'
#     UNKNOWN = 'unknown'

# class Account(Document):
#     name = StringField(required=True)
#     group = EnumField(AccountType)     

class DB:
    '''
    A collection of static methods that implement the API to
    the database.
    '''

    client = None
    database = None

    @staticmethod
    def open(dbname: str):
        '''
        Connect to a MongoDB server and database.  Saves the connection
        and database in static variables that are accessible outside the
        class.

        Arguments:
            dbname:  name of the databaae to use
        '''
        logging.info(f'DB: open {dbname}')
        DB.client = connect(dbname)
        DB.database = DB.client[dbname]

    @staticmethod
    def import_journal(fn: str):
        '''
        Read statements and transactions from a plain text accounting
        (.jorurnal) file.  Erases any previous documents in the database.

        Arguments:
            fn: path to the input file
        '''
        logging.info(f'DB:importing journal file:{fn}')
        p = JournalParser()
        p.parse_file(fn)
