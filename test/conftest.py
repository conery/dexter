# Unit tests for the io module

import pytest

from dexter.DB import DB
from dexter.io import import_journal

@pytest.fixture
def db(scope='session'):
    '''
    Connect to the MongoDB server running on localhost, initialize a
    database named "pytest", load the example data into the DB.
    '''
    DB.open('pytest')
    DB.erase_database()
    import_journal('test/fixtures/mini.journal', False)
    return DB.database

