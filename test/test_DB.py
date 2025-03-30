# Unit tests for the DB module

import pytest

from datetime import date
from dexter.DB import DB, Document, Account, Entry, Transaction, Column
# from dexter.schema import *
from dexter.io import import_journal

@pytest.fixture
def db():
    '''
    Connect to the MongoDB server running on localhost, initialize a
    database named "pytest", load the example data into the DB.
    '''
    DB.open('pytest')
    DB.erase_database()
    import_journal('test/fixtures/mini.journal', False)
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
        database and the collections it contains.
        '''
        assert DB.dbname == 'pytest'

    def test_import(self, db):
        '''
        Check the number of documents in each of the collections in the 
        test data.
        '''
        assert len(DB.models) == 3
        assert set(DB.collections.keys()) == {'account', 'entry', 'transaction'}
        assert db.command('count','account')['n'] == 10
        assert db.command('count','entry')['n'] == 38
        assert db.command('count','transaction')['n'] == 16

    def test_uids(self, db):
        '''
        Every entry should have a unique UID value
        '''
        uids = DB.uids()
        assert len(uids) == db.command('count','entry')['n']

    def test_transaction_attributes(self, db):
        '''
        Test the computed attributes of the Transaction class
        '''
        lst = Transaction.objects(description='Safeway')
        p0 = lst[0]
        assert p0.accounts == {'groceries','checking'}
        assert p0.originals == 'weekly/Safeway'
        assert len(p0.debits) == len(p0.credits) == 1
        assert p0.pdate == date(2024,1,7)
        assert p0.pcredit == 'checking'
        assert p0.pdebit == 'groceries'
        assert p0.pamount == 75.00
    
    def test_select_transactions(self, db):
        '''
        Test the select method, fetching transaction that match constraints
        '''
        # all transactions
        lst = DB.select(Transaction)
        assert len(lst) == 16

        # select by date
        lst = DB.select(Transaction, date=date(2024,1,21))
        assert len(lst) == 1
        assert lst[0].pdate == date(2024,1,21)

        lst = DB.select(Transaction, start_date=date(2024,1,21))
        assert len(lst) == 10
        assert all(t.pdate >= date(2024,1,21) for t in lst)

        lst = DB.select(Transaction, end_date=date(2024,1,21))
        assert len(lst) == 7
        assert all(t.pdate <= date(2024,1,21) for t in lst)

        # select by amount
        lst = DB.select(Transaction, amount=75)
        assert len(lst) == 3
        assert all(t.pamount == 75 for t in lst)

        lst = DB.select(Transaction, max_amount=75)
        assert len(lst) == 7
        assert all(t.pamount <= 75 for t in lst)

        lst = DB.select(Transaction, min_amount=75)
        assert len(lst) == 12
        assert all(t.pamount >= 75 for t in lst)

        # select by descriptiom
        lst = DB.select(Transaction, description = r'^s')
        assert len(lst) == 6
        assert all(t.description.startswith('S') for t in lst)

        lst = DB.select(Transaction, comment = r'budget')
        assert len(lst) == 2
        assert all('budget' in t.comment for t in lst)

        # select by account
        lst = DB.select(Transaction, credit='mortgage')
        assert len(lst) == 2
        assert all('mortgage' in t.pcredit for t in lst)

        lst = DB.select(Transaction, debit='mortgage')
        assert len(lst) == 2
        assert all('mortgage' in t.pdebit for t in lst)

    def test_select_transactions_multi(self, db):
        '''
        Test the select with multple constraints
        '''
        lst = DB.select(Transaction, description = r'^s', min_amount=100)
        assert len(lst) == 1
        assert lst[0].description.startswith('S')
        assert lst[0].pamount > 100

        lst = DB.select(Transaction, start_date = date(2024,2,1), credit='visa')
        assert len(lst) == 2
        assert all('visa' in t.pcredit and t.pdate >= date(2024,2,1) for t in lst)

    def test_select_entries(self, db):
        '''
        Test the select method, fetching individual entries that match constraints
        '''
        # all entries
        lst = DB.select(Entry)
        assert len(lst) == 38

        # select by date
        lst = DB.select(Entry, date=date(2024,1,5))
        assert len(lst) == 2
        assert all(e.date == date(2024,1,5) for e in lst)

        lst = DB.select(Entry, start_date=date(2024,1,5))
        assert len(lst) == 29
        assert all(e.date >= date(2024,1,5) for e in lst)

        lst = DB.select(Entry, end_date=date(2024,1,5))
        assert len(lst) == 11
        assert all(e.date <= date(2024,1,5) for e in lst)

        # select by amount
        lst = DB.select(Entry, amount=900)
        assert len(lst) == 2
        assert all(e.amount == 900 for e in lst)

        lst = DB.select(Entry, max_amount=900)
        assert len(lst) == 24
        assert all(e.amount <= 900 for e in lst)

        lst = DB.select(Entry, min_amount=900)
        assert len(lst) == 16
        assert all(e.amount >= 900 for e in lst)

        # select by account
        lst = DB.select(Entry, account='groceries')
        assert len(lst) == 6
        assert all(e.account == 'groceries' for e in lst)

        # select by column
        lst = DB.select(Entry, column='credit')
        assert len(lst) == 22
        assert all(e.column == Column.cr for e in lst)

        lst = DB.select(Entry, column='debit')
        assert len(lst) == 16
        assert all(e.column == Column.dr for e in lst)


