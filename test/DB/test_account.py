# Unit tests for the DB module

import pytest

from datetime import date
from dexter.DB import DB, Document, Account, Category, Entry, Transaction, Column, Tag

class TestAccount:
    '''
    Test methods of the DB class using transactions from a file in
    the fixtures directory.
    '''

    def test_fullname(self, db):
        '''
        Test the fullname method
        '''
        assert DB.fullname('expenses:food:groceries') == 'expenses:food:groceries'
        assert DB.fullname('groceries') == 'expenses:food:groceries'
        assert DB.fullname('groc') is None

    def test_abbrev(self, db):
        '''
        Test the abbrev method
        '''
        assert DB.abbrev('expenses:food:groceries') == 'groceries'
        assert DB.abbrev('expenses:car:payment') == 'expenses:car:payment'

    def test_find_one_account(self, db):
        '''
        Call find_account with a string that matches one name
        '''
        lst = DB.find_account("yoyo")
        assert len(lst) == 1 and lst[0].name == 'income:yoyodyne'


    def test_find_no_account(self, db):
        '''
        Call find_account with a string that does matche an account name
        '''
        lst = DB.find_account("trust")
        assert len(lst) == 0       


    def test_many_accounts(self, db):
        '''
        Call find_account with a string that matches several names
        '''
        lst = DB.find_account("assets")
        assert len(lst) == 2

    def test_all_name_parts(self, db):
        '''
        Test the method that separates names into parts
        '''
        names = DB.account_name_parts()
        assert len(names) == 21
        assert 'yoyodyne' in names
        assert 'chase' in names
        assert 'visa' in names

    def test_name_parts(self, db):
        '''
        Test the method that separates names into parts
        '''
        names = DB.account_name_parts(Category.A)
        assert len(names) == 4
        assert 'checking' in names
        assert 'savings' in names

    def test_all_account_names(self, db):
        '''
        Test the method that maps a partial name to the full name
        in the account hierarchy
        '''
        dct = DB.account_names()
        assert len(dct) == 36
        assert dct['assets'] == {'assets:bank:checking', 'assets:bank:savings'}
        assert len(dct['expenses']) == 10

    def test_account_names(self, db):
        '''
        Test the method that maps a partial name to the full name
        in the account hierarchy
        '''
        dct = DB.account_names(Category.E)
        assert len(dct) == 22
        assert dct['car'] == {'expenses:car', 'expenses:car:payment', 'expenses:car:fuel'}

    def test_account_name_abbrev(self, db):
        '''
        Make sure abbreviations are included in account name map
        '''
        dct = DB.account_names(Category.E)
        assert dct['dining'] == {'expenses:food:restaurant'}

    def test_account_glob(self, db):
        '''
        Test the account_glob method.  Adds some new Account objects with
        extra name parts to test the pattern that has levels.
        '''
        Account(name='expenses:car:fuel:gas', category=Category.E).save()
        Account(name='expenses:car:fuel:electric', category=Category.E).save()

        # Expand the top level expense categories
        expenses = DB.expand_node('expenses:1')
        assert len(expenses) == 4
        assert 'expenses:car' in expenses
        assert 'expenses:travel' in expenses
        assert 'expenses:car:fuel' not in expenses

        # Expand car categories
        expenses = DB.expand_node('car:1')
        assert len(expenses) == 3
        assert r'expenses:car$' in expenses
        assert 'expenses:car:fuel' in expenses
        assert 'expenses:car:fuel:electric' not in expenses

        # Expand car categories two levels down
        expenses = DB.expand_node('car:2')
        assert len(expenses) == 5
        assert r'expenses:car$' in expenses
        assert r'expenses:car:fuel$' in expenses
        assert 'expenses:car:fuel:electric' in expenses

