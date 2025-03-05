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

class Account(Document):
    name = StringField(required=True)
    group = EnumField(AccountType)     
