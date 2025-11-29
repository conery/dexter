# Unit tests for the DB module

import pytest

from datetime import date
from dexter.DB import DB, Document, Account, Category, Entry, Transaction, Column, Tag

class TestEntry:
    '''
    Test methods of the DB class using transactions from a file in
    the fixtures directory.
    '''

    def test_uids(self, db):
        '''
        Every entry should have a unique UID value
        '''
        uids = DB.uids()
        assert len(uids) == db.command('count','entry')['n']

    def test_select_entries(self, db):
        '''
        Test the select method, fetching individual entries that match constraints
        '''
        # all entries
        lst = DB.select(Entry)
        assert len(lst) == 58

        # select by date
        lst = DB.select(Entry, date=date(2024,1,5))
        assert len(lst) == 2
        assert all(e.date == date(2024,1,5) for e in lst)

        lst = DB.select(Entry, start_date=date(2024,1,5))
        assert len(lst) == 48
        assert all(e.date >= date(2024,1,5) for e in lst)

        lst = DB.select(Entry, end_date=date(2024,1,5))
        assert len(lst) == 12
        assert all(e.date <= date(2024,1,5) for e in lst)

        # select by amount
        lst = DB.select(Entry, amount=500)
        assert len(lst) == 12
        assert all(e.amount == 500 for e in lst)

        lst = DB.select(Entry, max_amount=500)
        assert len(lst) == 40
        assert all(e.amount <= 500 for e in lst)

        lst = DB.select(Entry, min_amount=500)
        assert len(lst) == 30
        assert all(e.amount >= 500 for e in lst)

        # select by account
        lst = DB.select(Entry, account='groceries')
        assert len(lst) == 6
        assert all(e.account == 'expenses:food:groceries' for e in lst)

        # select by column
        lst = DB.select(Entry, column='credit')
        assert len(lst) == 33
        assert all(e.column == Column.cr for e in lst)

        lst = DB.select(Entry, column='debit')
        assert len(lst) == 25
        assert all(e.column == Column.dr for e in lst)

    def test_select_entries_tagged(self, db):
        '''
        Test the select method when tags are constraints
        '''
        groceries = DB.select(Entry, account='groceries')
        for e in groceries:
            assert e.tags == []
        groceries[0].update(push__tags=Tag.U.value)
        lst = DB.select(Entry, account='groceries', tag='#unpaired')     # match complete tag string
        assert len(lst) == 1 and lst[0] == groceries[0]
        lst = DB.select(Entry, account='groceries', tag='unp')           # match partial string
        assert len(lst) == 1 and lst[0] == groceries[0]

    def test_select_entries_untagged(self, db):
        '''
        Test the select method to find objects that do not contain a tag
        '''
        groceries = DB.select(Entry, account='groceries')
        groceries[0].update(push__tags=Tag.U.value)
        lst = DB.select(Entry, account='groceries', tag='^#unpaired')     # match complete tag string
        assert len(lst) == 5 and groceries[0] not in lst
        lst = DB.select(Entry, account='groceries', tag='^unp')           # match partial string
        assert len(lst) == 5 and groceries[0] not in lst

    def test_entry_attributes(self, db):
        lst = DB.select(Entry, column='credit')
        e = lst[0]
        assert e.column == Column.cr
        assert e.column.opposite() == Column.dr
        assert e.column.opposite().opposite() == e.column

    def test_balance(self, db):
        '''
        The balance over all entries should be 0
        '''
        assert DB.balance('') == 0

    def test_food_balance(self, db):
        '''
        Test the balance of a specified account, with and without budget
        transactions and with and without dates
        '''
        assert DB.balance('expenses:food') == -525
        assert DB.balance('expenses:food', nobudget=True) == 475
        assert DB.balance('expenses:food', ending='2024-01-31') == -250
        assert DB.balance('expenses:food', ending='2024-01-31', nobudget=True) == 250

    def test_entry_audit(self, db):
        '''
        Test the method that checks for inconsistencies in Entry objects.
        First make sure valid entries pass the test, then edit objects
        to introduce errors and make sure the method catches them.
        '''
        lst = Transaction.objects(description='Safeway')
        for e in lst[0].entries:
            assert DB.validate_entry(e) is None

        with pytest.raises(AssertionError) as err:
            e = lst[0].entries[0]
            e.tags.append(Tag.U.value)
            DB.validate_entry(e)
        assert "tref in unpaired" in str(err.value)

        with pytest.raises(AssertionError) as err:
            e = lst[1].entries[0]
            e.tref = None
            DB.validate_entry(e)
        assert "missing tref" in str(err.value)

        with pytest.raises(AssertionError) as err:
            e = lst[2].entries[0]
            e.tref = lst[3].entries[0].tref
            DB.validate_entry(e)
        assert "not linked to parent" in str(err.value)

