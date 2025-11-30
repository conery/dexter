# Unit tests for the io module

import pytest

from dexter.io import parse_journal
from dexter.DB import DB

@pytest.fixture
def iodb(scope='module'):
    '''
    Create a new database for the IO tests 
    '''
    DB.init()
    DB.create('pytest')
    accts, trans = parse_journal('test/fixtures/demo.journal', set(), set())
    DB.save_records(accts)
    DB.save_records(trans)
    return DB.database

class TestIO:
    '''
    Test methods that read and write files.
    '''

    def test_one(self, iodb):
        assert 6*7 == 42
