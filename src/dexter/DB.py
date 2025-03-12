# Database schema and API

import logging
from mongoengine import *

from .io import JournalParser
from .schema import *

class DB:
    '''
    A collection of static methods that implement the API to
    the database.
    '''

    client = None
    database = None
    dbname = None

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
        DB.client = connect(dbname, UuidRepresentation='standard')
        DB.database = DB.client[dbname]
        DB.dbname = dbname

    @staticmethod
    def import_journal(fn: str):
        '''
        Read statements and transactions from a plain text accounting
        (.jorurnal) file.  Erases any previous documents in the database.

        Arguments:
            fn: path to the input file
        '''
        logging.info(f'DB:importing journal file:{fn}')
        DB.client.drop_database(DB.dbname)
        for obj in JournalParser().parse_file(fn):
            obj.save()

    entry_constraints = {
        'description': 'description__regex',
        'date':  'date',
        'start_date': 'date__gte',
        'end_date': 'date__lte',
    }

    transaction_constraints = {
        'description': 'description__regex',
        'comment': 'comment__regex',
        'date':  'pdate',
        'start_date': 'pdate__gte',
        'end_date': 'pdate__lte',
    }

    @staticmethod
    def select(cls, **constraints):
        '''
        Fetch transactions that match constraints.

        Arguments:
            cls:  the collection to search (Entry or Transaction)
            constraints:  a dictionary of field names and values
        '''
        if cls not in [Entry, Transaction]:
            raise ValueError('select: collection must be Entry or Transaction')
        mapping = DB.transaction_constraints if cls == Transaction else DB.entry_constraints
        dct = {}
        for field, value in constraints.items():
            if field not in mapping:
                raise ValueError(f'select: unknown constraint: {field}')
            dct[mapping[field]] = value
        return cls.objects(Q(**dct))
