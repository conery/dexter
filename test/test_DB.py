# Unit tests for the DB module

from datetime import date
from dexter.DB import DB, Document, Account, Category, Entry, Transaction, Column

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
        assert len(DB.models) == 5
        assert set(DB.collections.keys()) == {'dexter', 'account', 'entry', 'transaction', 'reg_exp'}

    def test_import(self, db):
        '''
        Check the number of documents in each of the collections in the 
        test data.
        '''
        assert db.command('count','account')['n'] == 15
        assert db.command('count','entry')['n'] == 40
        assert db.command('count','transaction')['n'] == 16

    def test_uids(self, db):
        '''
        Every entry should have a unique UID value
        '''
        uids = DB.uids()
        assert len(uids) == db.command('count','entry')['n']

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

    def test_account_groups(self, db):
        '''
        Test the account_groups method.
        '''
        grp = DB.account_groups()
        assert len(grp) == len(Account.objects)

        # !! Add more tests after adding new accounts to test fixture

        # grp = DB.account_groups(['expenses'])
        # assert len(grp) == 6
        # assert all(lambda s: s.startswith('expenses') for s in grp)

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
        lst = DB.select(Transaction, credit='expenses:home')
        assert len(lst) == 3
        assert all('home' in t.pcredit for t in lst)

        lst = DB.select(Transaction, debit='expenses:home')
        assert len(lst) == 3
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
        assert len(lst) == 3
        assert all('visa' in t.pcredit and t.pdate >= date(2024,2,1) for t in lst)

    def test_select_entries(self, db):
        '''
        Test the select method, fetching individual entries that match constraints
        '''
        # all entries
        lst = DB.select(Entry)
        assert len(lst) == 40

        # select by date
        lst = DB.select(Entry, date=date(2024,1,5))
        assert len(lst) == 2
        assert all(e.date == date(2024,1,5) for e in lst)

        lst = DB.select(Entry, start_date=date(2024,1,5))
        assert len(lst) == 30
        assert all(e.date >= date(2024,1,5) for e in lst)

        lst = DB.select(Entry, end_date=date(2024,1,5))
        assert len(lst) == 12
        assert all(e.date <= date(2024,1,5) for e in lst)

        # select by amount
        lst = DB.select(Entry, amount=500)
        assert len(lst) == 10
        assert all(e.amount == 500 for e in lst)

        lst = DB.select(Entry, max_amount=500)
        assert len(lst) == 26
        assert all(e.amount <= 500 for e in lst)

        lst = DB.select(Entry, min_amount=500)
        assert len(lst) == 24
        assert all(e.amount >= 500 for e in lst)

        # select by account
        lst = DB.select(Entry, account='groceries')
        assert len(lst) == 4
        assert all(e.account == 'expenses:food:groceries' for e in lst)

        # select by column
        lst = DB.select(Entry, column='credit')
        assert len(lst) == 24
        assert all(e.column == Column.cr for e in lst)

        lst = DB.select(Entry, column='debit')
        assert len(lst) == 16
        assert all(e.column == Column.dr for e in lst)

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
        assert DB.balance('food') == -600
        assert DB.balance('food', budgets=False) == 400
        assert DB.balance('food', ending='2024-01-31') == -250
        assert DB.balance('food', ending='2024-01-31', budgets=False) == 250
