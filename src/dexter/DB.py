# Database schema and API

from enum import Enum
from hashlib import md5
import logging
from mongoengine import *

# from .schema import *

### Database Schema, defined using MongoEngine

class Category(Enum):
    Q = 'Q'         # equity
    I = 'I'         # income
    A = 'A'         # assets
    E = 'E'         # expenses
    L = 'L'         # liabilities

    def __str__(self):
        return self.value

class Column(Enum):
    cr = 'credit'
    dr = 'debit'

    def __str__(self):
        return self.value

class Account(Document):
    name = StringField(required=True)
    category = EnumField(Category, required=True)
    comment = StringField()

    def __str__(self):
        return f'<Acct {self.name} {self.category}'

    @queryset_manager
    def nominal_accounts(doc_cls, queryset):
        # return queryset.filter(Q(group='expenses') | Q(group='liabilities'))
        return queryset.filter(category__in=['E','L'])

class Entry(Document):
    # uid = StringField(required=True, unique=True)
    uid = StringField(required=True)
    date = DateField(required=True)
    description = StringField(required=True)
    account = StringField(required=True)
    column = EnumField(Column, required=True) 
    amount = FloatField(required=True)

    def __str__(self):
        e = '+' if self.column == Column.dr else '-'
        return f'<En {self.date} {self.account} {e}${self.amount}>'
    
    @property
    def hash(self):
        s = f'{self.account}{self.date}{self.amount}{self.description}'
        return md5(bytes(s, 'utf-8')).hexdigest()
    
    def clean(self):
        self.uid = self.hash

class Transaction(Document):
    description = StringField(required=True)
    comment = StringField()
    tags = ListField(StringField())
    entries = ListField(ReferenceField('Entry'))
    pdate = DateField()
    pdebit = StringField()
    pcredit = StringField()
    pamount = FloatField()

    def __str__(self):
        return f'<Tr {self.pdate} {self.pcredit} -> {self.pdebit} ${self.pamount} {self.description}>'

    @property
    def accounts(self):
        return { e.account for e in self.entries }

    @property
    def credits(self):
        return [ e for e in self.entries if e.column == Column.cr ]
    
    @property
    def debits(self):
        return [ e for e in self.entries if e.column == Column.dr ]

    @property
    def originals(self):
        return '/'.join(e.description for e in self.entries)
    
    def clean(self):
        self.pdate = min(e.date for e in self.entries)
        self.pamount = sum(e.amount for e in self.entries if e.column == Column.cr)
        self.pcredit = '/'.join(a.account for a in self.credits)
        self.pdebit = '/'.join(a.account for a in self.debits)

### Database API

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
        DB.models = [cls for cls in Document.__subclasses__() if hasattr(cls, 'objects')]
        DB.collections = { cls._meta["collection"]: cls for cls in DB.models }
        logging.debug(f'models: {DB.models}')

    @staticmethod
    def erase_database():
        '''
        Erase the database.
        '''
        DB.client.drop_database(DB.dbname)

    @staticmethod
    def add_record(collection: str, doc: str):
        '''
        Add a new record to a collection.

        Arguments:
            collection:  the name of the collection
            doc:  a JSON string with the document descriptio
        '''
        logging.debug(f'{collection} {doc}')
        cls = DB.collections[collection]
        obj = cls.from_json(doc, True)
        obj.save()

    @staticmethod
    def save_records(f):
        '''
        Iterate over collections, write each record along with its 
        collection name.

        Arguments:
            f: file object for the output
        '''

        for collection, cls in DB.collections.items():
            logging.debug(f'exporting {collection}')
            for obj in cls.objects:
                print(f'{collection}: {obj.to_json()}', file=f)
                
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
