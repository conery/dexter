# Unit tests for the io module

import pytest

from dexter.DB import DB
from dexter.io import init_from_journal

@pytest.fixture
def db(scope='session'):
    '''
    Connect to the MongoDB server running on localhost, initialize a
    database named "pytest", load the example data into the DB.
    '''
    DB.init()
    DB.create('pytest')
    init_from_journal('test/fixtures/mini.journal')
    return DB.database

