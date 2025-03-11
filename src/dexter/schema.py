# Database Schema

from enum import Enum
from mongoengine import *

class AccountType(Enum):
    Q = 'Q'         # equity
    I = 'I'         # income
    A = 'A'         # assets
    E = 'E'         # expenses
    L = 'L'         # liabilities
    X = 'X'         # unknown

class EntryType(Enum):
    cr = 'credit'
    dr = 'debit'

class AcctQuerySet(QuerySet):

    def expense_accounts(self,prefix):
        return self.filter(name__startswith=prefix)

class Account(Document):
    name = StringField(required=True)
    group = EnumField(AccountType, required=True)
    comment = StringField()
    meta = {'queryset_class': AcctQuerySet}

    @queryset_manager
    def nominal_accounts(doc_cls, queryset):
        # return queryset.filter(Q(group='expenses') | Q(group='liabilities'))
        return queryset.filter(group__in=['expenses','liabilities'])

class Entry(Document):
    uid = StringField(required=True)
    date = DateField(required=True)
    description = StringField(required=True)
    account = StringField(required=True)
    etype = EnumField(EntryType, required=True) 
    amount = FloatField(required=True)

class Transaction(Document):
    description = StringField(required=True)
    comment = StringField()
    tags = ListField(StringField())
    entries = ListField(ReferenceField('Entry'))
    pdate = DateField()
    pdebit = StringField()
    pcredit = StringField()
    pamount = FloatField()

    @property
    def accounts(self):
        return { e.account for e in self.entries }

    @property
    def credits(self):
        return [ e for e in self.entries if e.etype == EntryType.cr ]
    
    @property
    def debits(self):
        return [ e for e in self.entries if e.etype == EntryType.dr ]

    @property
    def originals(self):
        return '/'.join(e.description for e in self.entries)

    def clean(self):
        self.pdate = min(e.date for e in self.entries)
        self.pamount = sum(e.amount for e in self.entries if e.etype == EntryType.cr)
        self.pcredit = '/'.join(a.account for a in self.credits)
        self.pdebit = '/'.join(a.account for a in self.debits)
