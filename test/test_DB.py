# Unit tests for the DB module

import pytest
import os

from dexter.DB import DB

print(os.getcwd())

def test_connection():
    DB.open('pytest')
    assert DB.dbname == 'pytest'

def test_import():
    DB.open('pytest')
    DB.import_journal('fixtures/mini.journal')
    db = DB.database
    assert sorted(db.list_collection_names()) == ['account', 'entry', 'transaction']
    assert db.command('count','account')['n'] == 7
    assert db.command('count','entry')['n'] == 38
    assert db.command('count','transaction')['n'] == 16
