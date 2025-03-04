# Database schema and API

from enum import Enum
import logging
from mongoengine import *

class AccountType(Enum):
    EQUITY = 'equity'
    INCOME = 'income'
    ASSET = 'asset'
    EXPENSE = 'expense'
    LIABILITY = 'liability'
    UNKNOWN = 'unknown'

class Account(Document):
    name = StringField(required=True)
    group = EnumField(AccountType)     

class DB:
    '''
    A collection of static methods that implement the API to
    the database.
    '''

    @staticmethod
    def open(dbname):
        logging.info(f'DB: open {dbname}')
        connect(dbname)
