# Unit tests for the DB module

import pytest

from datetime import date
from dexter.DB import DB
from dexter.schema import *

@pytest.fixture
def db():
    '''
    Connect to the MongoDB server running on localhost, initialize a
    database named "pytest", load the example data into the DB.
    '''
    DB.open('pytest')
    DB.import_journal('test/fixtures/mini.journal')
    return DB.database

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
        database.
        '''
        assert DB.dbname == 'pytest'

    def test_import(self, db):
        '''
        Check the number of documents in each of the collections in the 
        test data.
        '''
        assert sorted(db.list_collection_names()) == ['account', 'entry', 'transaction']
        assert db.command('count','account')['n'] == 9
        assert db.command('count','entry')['n'] == 38
        assert db.command('count','transaction')['n'] == 16

    def test_transaction_attributes(self, db):
        '''
        Test the computed attributes of the Transaction class
        '''
        lst = Transaction.objects(description='Safeway')
        p0 = lst[0]
        assert p0.date == date(2024,1,7)
        assert p0.amount == 75.00
        assert p0.accounts == {'expenses:groceries','assets:checking'}
        assert p0.originals == '/'
    