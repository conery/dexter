# Database schema and API

from enum import Enum
from datetime import datetime
from hashlib import md5
import logging
import os
import re
import string

from mongoengine import *
import pandas as pd

from .config import Config, Tag

### Database Schema, defined using MongoEngine

class Category(Enum):
    Q =  'equity'
    I =  'income'
    A =  'assets'
    E =  'expenses'
    L =  'liabilities'

    def __str__(self):
        return self.value

class Column(Enum):
    cr = 'credit'
    dr = 'debit'

    # def __str__(self):
    #     return self.value
    
    def opposite(self):
        return Column.dr if self.value == 'credit' else Column.cr
    
class Action(Enum):
    A = 'apply'
    T = 'trans'
    X = 'xfer'

    def __str__(self):
        return self.value

class Dexter(Document):
    date = DateField(required=True)

    def __str__(self):
        return f'<DB created {self.date}>'

class Account(Document):
    name = StringField(required=True)
    category = EnumField(Category, required=True)
    abbrev = StringField()
    parser = StringField()
    comment = StringField()

    def __str__(self):
        return f'{self.abbrev or self.name} {self.category}'
    
    def row(self):
        return [
            'account',
            str(self.category),
            self.name.replace(':','.'),
            self.abbrev,
            self.parser,
            self.comment,
        ]

    @queryset_manager
    def nominal_accounts(doc_cls, queryset):
        return queryset.filter(category__in=['E','I'])

class Entry(Document):
    uid = StringField(required=True, unique=True)
    date = DateField(required=True)
    description = StringField()
    account = StringField(required=True)
    column = EnumField(Column, required=True) 
    amount = FloatField(required=True)
    tags = ListField(EnumField(Tag))

    meta = {'strict': False}

    def __str__(self):
        e = '+' if self.column == Column.dr else '-'
        return f'<En {self.date} {self.account} {e}${self.amount} {self.tags}>'
    
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
    def value(self):
        return self.amount if self.column == Column.dr else -self.amount

    @property
    def hash(self):
        s = f'{self.account}{self.date}{self.amount}{self.description}'
        return md5(bytes(s, 'utf-8')).hexdigest()
    
    def clean(self):
        logging.debug(f'uid: {self.hash}')
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
        return f'<Tr {self.pdate} {self.pcredit} -> {self.pdebit} ${self.pamount} {self.description} {self.tags}>'

    def row(self):
        return [
            'transaction',
            str(self.pdate),
            f'{self.pcredit} -> {self.pdebit}',
            self.description,
            self.comment,
            str(self.tags),
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

    @property
    def isbudget(self):
        return Tag.B.value in self.tags

    def clean(self):
        self.pdate = min(e.date for e in self.entries)
        self.pamount = sum(e.amount for e in self.entries if e.column == Column.cr)
        self.pcredit = '/'.join(a.account for a in self.credits)
        self.pdebit = '/'.join(a.account for a in self.debits)

    def save(self):
        '''
        Extend the base class save method.  Save each entry, then call
        the base class method.
        '''
        for e in self.entries:
            e.save()
        super().save()

class RegExp(Document):
    action = EnumField(Action, required=True) 
    expr = StringField(required=True)
    repl = StringField(required=True)
    acct = StringField(required=True)

    def __str__(self):
        return f'<RE {self.action} {self.expr} {self.repl} {self.acct}>'

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
        return bool(re.search(self.expr, s, re.I))

    def apply(self, s: str):
        '''
        If this regular expression matches the string s return the 
        result (after substituting parts), otherwise return None

        Arguments:
            s: the string to match
        '''
        repl = None

        if m := re.search(self.expr, s, re.I):
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

    dexters = set()
    server = None
    connection = None
    database = None
    dbname = None

    @staticmethod
    def info():
        '''
        Return information about the databases on the server.
        '''
        dct = {}
        for db in DB.server.list_database_names():
            if db not in DB.dexters:
                continue
            dct[db] = { }
            for tbl in DB.server[db].list_collection_names():
                n = DB.server[db][tbl].count_documents({})
                dct[db][tbl] = n
        return dct

    @staticmethod
    def init():
        '''
        Connect to the MongoDB server, make a list of Dexter databases.
        '''
        pm = connect(alias = 'pm')
        for dbname in pm.list_database_names():
            if 'dexter' in pm[dbname].list_collection_names():
                coll = pm[dbname].dexter
                n = coll.count_documents({})
                obj = coll.find_one()
                if n == 1 and 'date' in obj:
                    DB.dexters.add(dbname)
        DB.server = pm

    @staticmethod
    def exists(dbname):
        '''
        Return True if dbname is the name of a Dexter database on the server.
        '''
        return dbname in DB.dexters
    
    @staticmethod
    def open(dbname: str):
        '''
        Connect to a Dexter database, making sure the database exists.  Saves 
        the connection info in static variables that are accessible outside the
        class.

        If `dbname` is None use the name in the envionment variable DEX_DB.

        Arguments:
            dbname:  name of the database
        '''
        dbname = dbname or os.getenv('DEX_DB')
        if dbname is None:
            raise ValueError('DB.open: specify a database name with --db or DEX_DB')   
        if dbname not in DB.dexters:
            raise ValueError(f'DB.open: no Dexter database named {dbname} on the server')
        logging.debug(f'DB: open {dbname}')

        DB.connection = connect(dbname, UuidRepresentation='standard')
        DB.database = DB.connection[dbname]

        clist = [x['name'] for x in DB.database.list_collections()]
        logging.debug(f'DB.open: collections: {clist}')

        if not all(cls in clist for cls in ['account','entry','transaction']):
            raise ValueError(f'DB.open: database missing Dexter collections')

        DB.dbname = dbname
        DB.models = [cls for cls in Document.__subclasses__() if hasattr(cls, 'objects')]
        DB.collections = { cls._meta["collection"]: cls for cls in DB.models }

    @staticmethod
    def create(dbname: str):
        ''''
        Open a connection to a new database.  

        Arguments:
            dbname:  name of the database
        '''
        DB.connection = connect(dbname, UuidRepresentation='standard')
        if dbname in DB.dexters:
            DB.connection.drop_database(dbname)
        DB.database = DB.connection[dbname]

        rec = Dexter(date = datetime.now())
        rec.save()

    @staticmethod
    def erase_database():
        '''
        Erase the database.
        '''
        DB.connection.drop_database(DB.dbname)

    @staticmethod
    def restore_from_json(collection: str, doc: str):
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
    def save_as_json(f):
        '''
        Iterate over collections, write each record along with its 
        collection name.

        Arguments:
            f: file object for the output
        '''

        for collection, cls in DB.collections.items():
            logging.debug(f'saving {collection}')
            for obj in cls.objects:
                print(f'{collection}: {obj.to_json()}', file=f)


    MAX_DUPS = 10

    def save_entries(recs):
        '''
        Save new Entry documents created by parsing a file.  Handle duplicates in 
        new records by modifying the description so the UID is different from the
        other copies.

        Arguments:
            recs:  a list of Entry objects
        '''
        # for obj in recs:
        #     logging.debug(f'save {obj}')
        #     desc = obj.description
        #     obj.tags.append(Tag.U)
        #     n = 0
        #     while n < DB.MAX_DUPS:
        #         try:
        #             obj.save()
        #             break
        #         except NotUniqueError:
        #             n += 1
        #             obj.description = f'{desc} ({n})'
        #             logging.debug(f'add: dup ({n}) for {obj}')
        #     else:
        #         logging.error(f'add: max {DB.MAX_DUPS} copies exceeded for {obj}')

        uids = set()
        for obj in recs:
            logging.debug(f'save {obj}')
            desc = obj.description
            n = 0
            while obj.hash in uids:
                n += 1
                if n > DB.MAX_DUPS:
                    logging.error(f'add: max {DB.MAX_DUPS} copies exceeded for {obj}')
                    raise ValueError(f'save_records: no uid: {obj}')
                obj.description = f'{desc} ({n})'
                logging.debug(f'  {obj.description}')
            # obj.tags.append(Tag.U)
            obj.save()
            uids.add(obj.hash)

    @staticmethod
    def fullname(s: str):
        '''
        The argument s is an account name that could be a full name or abbreviated
        name.  Return the full account name or None if the name isn't defined.
        '''
        if lst := Account.objects(name__exact=s) or Account.objects(abbrev__exact=s):
            return lst[0].name
        return None

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
    def account_names(category=None):
        '''
        Return a dictionary that maps a partial account name to a list
        of full account names that contain that part.
        '''
        dct = {}
        for acct in Account.objects:
            if category and acct.category.value != category:
                continue
            for part in acct.name.split(':'):
                lst = dct.setdefault(part, [])
                lst.append(acct.name)
        return dct

    @staticmethod
    def account_groups(specs=[]):
        '''
        Convert a list of account name specs from the command line into
        a list of account groups to use in reports.  
        
        Specs are strings that correspond to nodes in the account hierarchy,
        optionally followed by a colon and level number.

        Arguments:
            specs:  the list of strings from the command line
        '''
        if len(specs) == 0:
            res = [a.name for a in Account.objects]
        else:
            res = []
            for s in specs:
                grp = []
                parts = s.split(':')
                logging.debug(f'account_groups: {parts}')
                if re.match(r'\d+', parts[-1]):
                    level = int(parts[-1])
                    pre = ':'.join(parts[:-1])
                    logging.debug(f'account groups: find accounts that start with "{pre}"')
                    for acct in Account.objects(name__startswith=pre):
                        if len(acct.name.split(':')) < level:
                            grp.append(acct.name)
                        elif len(acct.name.split(':')) == level:
                            grp.append(f'{acct.name}.*')
                    logging.debug(f'account groups: found {grp}')
                    if len(grp) == 0:
                        grp.append(f'{pre}.*')
                        logging.debug(f'account groups: grp = {grp}')
                else:
                    logging.debug(f'account_groups: find all accounts below {s}')
                    grp += [a.name for a in Account.objects(name__startswith=s)]
                res += grp
        return res
    
    @staticmethod
    def balance(acct, ending=None, budgets=True):
        '''
        Compute the balance of an account, with or without budget transactions.

        Arguments:
            acct: the name of the account
            budgets: if False ignore budget transactions
        '''
        kwargs = {'account': acct}
        if ending:
            kwargs['end_date'] = ending
        res = sum(e.value for e in DB.select(Entry, **kwargs))
        if not budgets:
            kwargs['tag'] = Tag.B
            res -= sum(e.value for e in DB.select(Entry, **kwargs))
        return res
    
    # RegExp management -- delete old records so new ones can be
    # imported

    @staticmethod
    def delete_regexps():
        '''
        Delete all the RegExp documents
        '''
        res = RegExp.objects.delete()
        logging.debug(f'DB: deleted {res} existing regular expressions')

    # RegExp search.  The first version is a simple linear search.
    # TBD: implement an indexing scheme based on the first letter
    # in the string.

    @staticmethod
    def find_first_regexp(s: str):
        '''
        Return the first RegExp with an X or T action that matches
        a string.

        Arguments:
            s: the string to match.
        '''
        for e in RegExp.objects:
            if e.action == Action.A:
                continue
            if e.matches(s):
                return e
        return None

    @staticmethod
    def find_all_regexp(s: str):
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
        logging.debug(f'select: {constraints}')
        if collection not in [Entry, Transaction]:
            raise ValueError('select: collection must be Entry or Transaction')
        mapping = DB.transaction_constraints if collection == Transaction else DB.entry_constraints
        dct = {}
        for field, value in constraints.items():
            if field not in mapping:
                raise ValueError(f'select: unknown constraint: {field}')
            dct[mapping[field]] = value
        return collection.objects(Q(**dct))


