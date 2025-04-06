# Database schema and API

from enum import Enum
from hashlib import md5
import logging
import re
import string

from mongoengine import *
import pandas as pd

from .config import Config, Tag

### Database Schema, defined using MongoEngine

class Category(Enum):
    Q =  'equity'
    I =  'income'
    A =  'asset'
    E =  'expense'
    L =  'liability'

    def __str__(self):
        return self.value

class Column(Enum):
    cr = 'credit'
    dr = 'debit'

    def __str__(self):
        return self.value
    
    def opposite(self):
        return Column.dr if self.value == 'credit' else Column.cr
    
class Action(Enum):
    T = 'trans'
    X = 'xfer'

    def __str__(self):
        return self.value

class Account(Document):
    name = StringField(required=True)
    category = EnumField(Category, required=True)
    comment = StringField()

    def __str__(self):
        return f'<Acct {self.name} {self.category}>'
    
    def row(self):
        return [
            'account',
            str(self.category),
            self.name,
            self.comment,
        ]

    @queryset_manager
    def nominal_accounts(doc_cls, queryset):
        return queryset.filter(category__in=['E','I'])

class Entry(Document):
    uid = StringField(required=True, unique=True)
    date = DateField(required=True)
    description = StringField(required=True)
    account = StringField(required=True)
    column = EnumField(Column, required=True) 
    amount = FloatField(required=True)
    tags = ListField(EnumField(Tag))

    meta = {'strict': False}

    def __str__(self):
        e = '+' if self.column == Column.dr else '-'
        return f'<En {self.date} {self.account} {e}${self.amount}>'
    
    def row(self):
        amt = f'${self.amount:.02f}'
        style = '[red]' if self.column == Column.cr else ""
        return [
            'entry',
            str(self.date),
            f'{style}{amt:>15s}',
            f'{self.account:20}',
            self.description[:50],
            str(self.tags),
        ]
    
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

    def row(self):
        return [
            'transaction',
            str(self.pdate),
            f'{self.pcredit} -> {self.pdebit}',
            self.description,
        ]

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

class RegExp(Document):
    action = EnumField(Action, required=True) 
    expr = StringField(required=True)
    repl = StringField(required=True)
    acct = StringField(required=True)

    def __str__(self):
        return f'<RE {self.action} {self.expr} {self.repl} ${self.acct}>'

    def row(self):
        return [
            'regexp',
            str(self.action),
            f"r'self.expr'",
            self.repl,
            self.acct,
        ]
    
    placeholder = r'{(\d+)(\.\w+)?}'

    transforms = {
        '': lambda s: s,
        '.lower':  lambda s: s.lower(),
        '.capwords':  lambda s: string.capwords(s),
    }

    def matches(self, s):
        '''
        Return True if this regular expression matches a string.

        Arguments:
            s: the string to match
        '''
        return bool(re.match(self.expr, s, re.I))

    def apply(self, s: str):
        '''
        If this regular expression matches the string s return the 
        result (after substituting parts), otherwise return None

        Arguments:
            s: the string to match
        '''
        repl = None

        if m := re.match(self.expr, s, re.I):
            repl = self.repl
            for i, f in re.findall(RegExp.placeholder, self.repl, re.I):
                if f:
                    repl = repl.replace(f,'')
                repl = repl.replace(f'{{{i}}}', RegExp.transforms[f](m[int(i)+1]))

        return repl    

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
    def import_from_json(collection: str, doc: str):
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
    def export_as_json(f):
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


    MAX_DUPS = 10

    def save_records(recs):
        '''
        Save new records from a CSV file in the database.  Handle duplicates in 
        new records by modifying the description so the UID is different from the
        other copies.

        Arguments:
            recs:  a list of Entry objects
        '''
        for obj in recs:
            logging.debug(f'save {obj}')
            desc = obj.description
            obj.tags.append(Tag.U)
            n = 0
            while n < DB.MAX_DUPS:
                try:
                    obj.save()
                    break
                except NotUniqueError:
                    n += 1
                    obj.description = f'{desc} ({n})'
                    logging.debug(f'add: dup ({n}) for {obj}')
            else:
                logging.error(f'add: max {DB.MAX_DUPS} copies exceeded for {obj}')

    @staticmethod
    def find_account(s: str):
        '''
        Return a list of account names that contain a string.

        Arguments:
            s:  the string to search for
        '''
        return Account.objects(name__contains=s)
    
    @staticmethod
    def account_name_parts(category=None):
        '''
        Return all the strings that appear as part of an account name.
        '''
        res = set()
        for acct in Account.objects:
            if category and acct.category.value != category:
                continue
            res |= set(acct.name.split(':'))
        return res
    
    @staticmethod
    def full_names(category=None):
        '''
        Return a dictionary that maps a partial account name to a list
        of full named that contain that part.
        '''
        dct = {}
        for acct in Account.objects:
            if category and acct.category.value != category:
                continue
            for part in acct.name.split(':'):
                lst = dct.setdefault(part, [])
                lst.append(acct.name)
        return dct
    
    # RegExp search.  The first version is a simple linear search.
    # TBD: implement an indexing scheme based on the first letter
    # in the string.

    @staticmethod
    def find_regexp(s: str):
        '''
        Return a list of RegExp objects that match a string.

        Arguments:
            s: the string to match.
        '''
        return [e for e in RegExp.objects if e.matches(s)]

    # Methods used when adding new records to make sure we don't
    # have duplicates

    @staticmethod
    def uids():
        '''
        Return the set of unique identifiers (uids) on all Entry
        documents in the database. 
        '''
        return {e.uid for e in Entry.objects}
    
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
        'tag': 'tags',
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

    @staticmethod
    def balances(date=None, category=None):
        '''
        Create a Pandas data frame with sums of credits and debits in accounts.

        Arguments:
            date:  use transactions up to and including this date
            category: if given use accounts in this group only
        '''
        all_categories = ['income', 'asset', 'liability', 'expense']
        if category is not None:
            if category not in all_categories:
                raise ValueError(f'balances: unknown category {category}')
            clist = [category]
        else:
            clist = all_categories
        logging.debug(f'balance: categories = {clist}')

        dct = {
            'category': [],
            'account':  [],
            'credit':   [],
            'debit':    [],
        }
        
        for acct in Account.objects:
            if acct.category.value not in clist:
                continue
            cons = {'account': acct.name}
            if date:
                cons['date__lte'] = date
            dct['category'].append(acct.category.value)
            dct['account'].append(acct.name)
            for col in ['credit', 'debit']:
                cons['column'] = col
                dct[col].append(Entry.objects(Q(**cons)).sum('amount'))

        df = pd.DataFrame(dct)
        df['balance'] = df['debit'] - df['credit']
        logging.debug(df)
        return df
    

