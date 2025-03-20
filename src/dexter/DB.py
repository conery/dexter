# Database schema and API

from datetime import date
import json
import logging
from mongoengine import *

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
        logging.debug(f'DB: open {dbname}')
        DB.client = connect(dbname, UuidRepresentation='standard')
        DB.database = DB.client[dbname]
        DB.dbname = dbname

    @staticmethod
    def erase_database():
        '''
        Erase the database.
        '''
        DB.client.drop_database(DB.dbname)

    @staticmethod
    def print_records(f):
        '''
        Iterate over collections, write each record along with its 
        collection name.

        Arguments:
            f: file object for the output
        '''

        models = [cls for cls in Document.__subclasses__() if hasattr(cls, 'objects')]

        for cls in models:
            collection = cls._meta['collection']
            logging.debug(f'exporting {collection}')
            for obj in cls.objects:
                print(f'["{collection}", {obj.to_json()}]', file=f)
                
    # These dictionaries map command line arguments to names of 
    # object attributes to use in calls that select objects.

    entry_constraints = {
        'description': 'description__iregex',
        'date':  'date',
        'start_date': 'date__gte',
        'end_date': 'date__lte',
        'amount':  'amount',
        'min_amount': 'amount__gte',
        'max_amount': 'amount__lte',
        'account': 'account__iregex',
        'column': 'column',
    }

    transaction_constraints = {
        'description': 'description__iregex',
        'comment': 'comment__iregex',
        'date':  'pdate',
        'start_date': 'pdate__gte',
        'end_date': 'pdate__lte',
        'amount':  'pamount',
        'min_amount': 'pamount__gte',
        'max_amount': 'pamount__lte',
        'debit': 'pdebit__iregex',
        'credit': 'pcredit__iregex',
        'tag': 'tags',
    }

    @staticmethod
    def select(collection, **constraints):
        '''
        Fetch transactions that match constraints.

        Arguments:
            collection:  the collection to search (Entry or Transaction)
            constraints:  a dictionary of field names and values
        '''
        if collection not in [Entry, Transaction]:
            raise ValueError('select: collection must be Entry or Transaction')
        mapping = DB.transaction_constraints if collection == Transaction else DB.entry_constraints
        dct = {}
        for field, value in constraints.items():
            if field not in mapping:
                raise ValueError(f'select: unknown constraint: {field}')
            dct[mapping[field]] = value
        return collection.objects(Q(**dct))
