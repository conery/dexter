# Unit tests for the DB module

import pytest

from datetime import date
from dexter.DB import DB, Document, Account, Category, Entry, Transaction, Column, Tag

class TestDB:
    '''
    Test methods of the DB class using transactions from a file in
    the fixtures directory.
    '''

    def test_connection(self, db):
        '''
        Make sure the database is connected.
        '''
        assert db.command('ping')['ok'] == 1

    def test_open(self, db):
        '''
        After opening the connection the module saves the name of the
        database and the collections it contains.
        '''
        assert DB.dbname == 'pytest'
        assert set(DB.collections.keys()) == {'dexter', 'message', 'account', 'entry', 'transaction', 'reg_exp'}

    def test_import(self, db):
        '''
        Check the number of documents in each of the collections in the 
        test data.
        '''
        assert db.command('count','account')['n'] == 15
        assert db.command('count','entry')['n'] == 58
        assert db.command('count','transaction')['n'] == 25
