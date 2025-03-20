# Database Schema

from enum import Enum
from mongoengine import *

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

    @queryset_manager
    def nominal_accounts(doc_cls, queryset):
        # return queryset.filter(Q(group='expenses') | Q(group='liabilities'))
        return queryset.filter(category__in=['E','L'])

class Entry(Document):
    uid = StringField(required=True)
    date = DateField(required=True)
    description = StringField(required=True)
    account = StringField(required=True)
    column = EnumField(Column, required=True) 
    amount = FloatField(required=True)

    def __str__(self):
        e = '+' if self.column == Column.dr else '-'
        return f'<En {self.date} {self.account} {e}${self.amount}>'

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
