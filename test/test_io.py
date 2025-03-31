# Unit tests for the io module

import pytest

from dexter.io import import_journal, add_records
from dexter.DB import DB

@pytest.fixture
def iodb(scope='module'):
    '''
    Create a new database for the IO tests 
    '''
    DB.open('pytest')
    DB.erase_database()
    import_journal('test/fixtures/mini.journal', False)
    return DB.database

class TestIO:
    '''
    Test methods that read and write files.
    '''

    def test_one(self, iodb):
        assert 6*7 == 42
