# Unit tests for the io module

import pytest

from dexter.io import init_from_journal
from dexter.DB import DB

@pytest.fixture
def iodb(scope='module'):
    '''
    Create a new database for the IO tests 
    '''
    DB.open('pytest', must_exist=False)
    DB.erase_database()
    init_from_journal('test/fixtures/mini.journal')
    return DB.database

class TestIO:
    '''
    Test methods that read and write files.
    '''

    def test_one(self, iodb):
        assert 6*7 == 42
