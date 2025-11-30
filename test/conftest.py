# Unit tests for the io module

import pytest

from dexter.DB import DB
from dexter.io import parse_journal

@pytest.fixture
def db(scope='session'):
    '''
    Connect to the MongoDB server running on localhost, initialize a
    database named "pytest", load the example data into the DB.
    '''
    DB.init()
    DB.create('pytest')
    accts, trans = parse_journal('test/fixtures/demo.journal', set(), set())
    DB.save_records(accts)
    DB.save_records(trans)
    return DB.database

