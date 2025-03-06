# Database Schema

from enum import Enum
from mongoengine import *

class AccountType(Enum):
    Q = 'equity'
    I = 'income'
    A = 'assets'
    E = 'expenses'
    L = 'liabilities'
    X = 'unknown'

class EntryType(Enum):
    cr = 'credit'
    dr = 'debit'

class Account(Document):
    name = StringField(required=True)
    group = EnumField(AccountType, required=True)
    comment = StringField()

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
