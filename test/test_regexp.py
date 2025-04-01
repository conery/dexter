# Unit tests for regular expressions

import pytest

from dexter.io import import_journal, import_regexp
from dexter.DB import DB, RegExp, Action

@pytest.fixture
def redb(scope='module'):
    '''
    Create a new database for the regular expression tests 
    '''
    DB.open('pytest')
    DB.erase_database()
    import_journal('test/fixtures/mini.journal', False)
    import_regexp('test/fixtures/regexp.csv')
    return DB.database

@pytest.fixture
def descriptions():
    '''
    Define a list of strings that could be found in CSV files, organized
    so that string i should match regexp i in the test fixtures.
    '''
    return [
        'CHEVRON 0092601',
        'COSTCO WHSE #0017 00EUGENE',
        'Payment to Comcast',
        'Check # 161: Completed',
        'WSFERRIES-ANACORTES',
    ]

class TestRegExp:
    '''
    Test methods that work with regular expressions
    '''

    def test_import(self, redb):
        '''
        Verify the test expressions were imported
        '''
        assert redb.command('count','reg_exp')['n'] == 5

    def test_attributes(self, redb):
        '''
        Get the first regexp from the test set, verify its attributes
        '''
        e = RegExp.objects[0]
        assert e.action == Action.T
        assert e.expr == 'CHEVRON'
        assert e.repl == 'Chevron'
        assert e.acct == 'car'

    def test_matches(self, redb, descriptions):
        '''
        Test the matches method
        '''
        for i, s in enumerate(descriptions):
            e = RegExp.objects[i]
            assert e.matches(s)

    def test_find_regexp(self, redb, descriptions):
        '''
        Test the regexp search, look for expected matches.
        '''
        for i, s in enumerate(descriptions):
            lst = DB.find_regexp(s)
            assert len(lst) == 1
            e = lst[0]
            assert e.matches(s)

    def test_find_fail(self, redb):
        '''
        Verify a failed search returns an empty list.
        '''
        assert len(DB.find_regexp('MegaBox Store')) == 0

    def test_apply(self, redb, descriptions):
        '''
        Test the apply method.  Expect the description strings to be
        transformed into the values defined here, which are tuples with
        the new description, an action, and an account name.
        '''
        expected = [
            ('Chevron', Action.T, 'car'), 
            ('Costco',  Action.T, 'food:groceries'),
            ('Comcast', Action.T, 'utility'),
            ('Check #161 :', Action.T, ''),
            ('Ferry Anacortes', Action.T, 'travel'),
        ]
        for i, s in enumerate(descriptions):
            e = DB.find_regexp(s)[0]
            desc, action, acct = expected[i]
            assert e.apply(s) == desc
            assert e.action == action
            assert e.acct == acct

    
