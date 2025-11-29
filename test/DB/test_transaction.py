# Unit tests for the DB module

import pytest

from datetime import date
from dexter.DB import DB, Document, Account, Category, Entry, Transaction, Column, Tag

class TestTransaction:
    '''
    Test methods of the DB class using transactions from a file in
    the fixtures directory.
    '''

    def test_transaction_attributes(self, db):
        '''
        Test the computed attributes of the Transaction class
        '''
        lst = Transaction.objects(description='Safeway')
        t = lst[0]
        assert t.accounts == {'expenses:food:groceries','assets:bank:checking'}
        assert t.originals == 'assigned/read from CSV'
        assert len(t.debits) == len(t.credits) == 1
        assert t.pdate == date(2024,1,7)
        assert t.pcredit == 'assets:bank:checking'
        assert t.pdebit == 'expenses:food:groceries'
        assert t.pamount == 75.00

    def test_transaction_links(self, db):
        '''
        The tref attribute of each entry in a transaction should be a
        reference to the transaction.
        '''
        for t in Transaction.objects:
            for e in t.entries:
                assert e.tref == t
    
    def test_select_transactions(self, db):
        '''
        Test the select method, fetching transaction that match constraints
        '''
        # all transactions
        lst = DB.select(Transaction)
        assert len(lst) == 25

        # select by date
        lst = DB.select(Transaction, date=date(2024,1,21))
        assert len(lst) == 1
        assert lst[0].pdate == date(2024,1,21)

        lst = DB.select(Transaction, start_date=date(2024,1,21))
        assert len(lst) == 19
        assert all(t.pdate >= date(2024,1,21) for t in lst)

        lst = DB.select(Transaction, end_date=date(2024,1,21))
        assert len(lst) == 7
        assert all(t.pdate <= date(2024,1,21) for t in lst)

        # select by amount
        lst = DB.select(Transaction, amount=75)
        assert len(lst) == 3
        assert all(t.pamount == 75 for t in lst)

        lst = DB.select(Transaction, max_amount=75)
        assert len(lst) == 11
        assert all(t.pamount <= 75 for t in lst)

        lst = DB.select(Transaction, min_amount=75)
        assert len(lst) == 17
        assert all(t.pamount >= 75 for t in lst)

        # select by descriptiom
        lst = DB.select(Transaction, description = r'^s')
        assert len(lst) == 10
        assert all(t.description.startswith('S') for t in lst)

        lst = DB.select(Transaction, comment = r'budget')
        assert len(lst) == 2
        assert all('budget' in t.comment for t in lst)

        # select by account
        lst = DB.select(Transaction, credit='expenses:home')
        assert len(lst) == 3
        assert all('home' in t.pcredit for t in lst)

        lst = DB.select(Transaction, debit='expenses:home')
        assert len(lst) == 4
        assert all('home' in t.pdebit for t in lst)

    def test_select_transactions_multi(self, db):
        '''
        Test the select with multple constraints
        '''
        lst = DB.select(Transaction, description = r'^s', min_amount=100)
        assert len(lst) == 1
        assert lst[0].description.startswith('S')
        assert lst[0].pamount > 100

        lst = DB.select(Transaction, start_date = date(2024,2,1), credit='visa')
        assert len(lst) == 7
        assert all('visa' in t.pcredit and t.pdate >= date(2024,2,1) for t in lst)

    def test_transaction_audit(self, db):
        '''
        Test the method that checks for inconsistencies in Transaction objects.
        First make sure valid transactions pass the test, then edit transactions
        to introduce errors and make sure the method catches them.
        '''
        lst = Transaction.objects(description='Safeway')
        for t in lst:
            assert DB.validate_transaction(t) is None

        with pytest.raises(AssertionError) as err:
            t = lst[0]
            del t.entries[0]
            DB.validate_transaction(t)
        assert "fewer than two entries" in str(err.value)

        with pytest.raises(AssertionError) as err:
            t = lst[1]
            t.entries[0].amount = 200.0
            DB.validate_transaction(t)
        assert "unbalanced" in str(err.value)

