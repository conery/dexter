#
# This file has functions that parse files to add records to the database
# or write records in a file.
#
# The code is organized with top level functions (called directly from main)
# are at the front of the file.  Parsers for specific formats come next,
# and miscellaneous helper functions are at the end.
#

import csv
import logging
import os
from pathlib import Path

from .DB import DB, Account, Entry, Transaction, RegExp, Tag
from .config import Config
from .console import print_records, print_grid, print_info_table
from .journal import JournalParser
from .util import parse_date

#######################
#
# Top level method for the info command
#
#######################


def print_info(args):
    '''
    The top level function, called from main when the command 
    is "info".  Get database descriptions from the server, print
    it in a table.

    Arguments:
        args: Namespace object with command line arguments.
    '''
    recs = DB.info()
    print_info_table(recs)

#######################
#
# Top level method for init command
#
#######################

def init_database(args):
    '''
    The top level function, called from main when the command is "init".  
    Initializes a new database using records from either a .journal file or a CSV file.

    Arguments:
        args: Namespace object with command line arguments.
    '''
    get_names_and_create_db(args)

    fn = Path(args.file)
    fmt = fn.suffix[1:]
    match fmt:
        case 'journal': 
            accts, trans = parse_journal(fn, set(), set())
        case 'csv': 
            accts, trans = parse_csv_accounts(fn)
        case _: 
            raise ValueError(f'init: unknown file extension: {fn.suffix}')
        
    if args.preview:
        for a in accts:
            print(a)
        for t in trans:
            t.clean()
            print(t)
    else:
        DB.save_records(accts)
        DB.save_records(trans)
    
#######################
#
# Top level method for import command
#
#######################


def import_records(args):
    '''
    The top level function, called from main when the command is "import".  
    
    If the regexp option was on the command line parse a single file, 
    erase old regexps, and replace them with the file contents.

    Otherwise there can be any number of files with transactions downloaded
    from a financial institution.  Create a new Entry object for each
    record and save it in the database.

    Arguments:
        args: Namespace object with command line arguments.
    '''
    open_db(args)
    paths = []

    for fn in args.files:
        p = Path(fn)
        if p.exists():
            paths.append(p)
        else:
            logging.error(f'import: file not found: {p}')

    if args.regexp:
        recs = parse_csv_regexp(paths[0])
        if not args.preview:
            DB.delete_regexps()
    else:
        anames = set(DB.account_names(with_parts=False).keys())
        recs = []
        for path in paths:
            match path.suffix:
                case '.journal':
                    _, new_recs = parse_journal(path, anames, DB.uids())
                case '.csv':
                    basename = args.account or path.stem
                    alist = DB.find_account(basename)
                    if len(alist) == 0:
                        logging.error(f'import: no account name matches {basename}')
                        continue
                    if len(alist) > 1:
                        logging.error(f'import: ambiguous account name {basename}')
                        continue
                    account = alist[0].name
                    parser = alist[0].parser
                    if parser not in Config.CSV.colmaps.keys():
                        logging.error(f'import: no parser for {account}')
                        continue
                    new_recs = parse_csv_transactions(path, parser, account, args.start_date, args.end_date, DB.uids())
                case _:
                    logging.error(f'import: unknown file type: {path.suffix}')
                    new_recs = []
            recs += new_recs

    if args.preview:
        print_records(recs)
    else:
        DB.save_records(recs)

#######################
#
# Top level method for export command
#
#######################

def export_records(args):
    '''
    The top level function, called from main when the command 
    is "export".

    Arguments:
        args: Namespace object with command line arguments.
    '''
    logging.error(f'export: not implemented')

#######################
#
# Top level method for save command
#
#######################


def save_records(args):
    '''
    The top level function, called from main when the command 
    is "save".  Writes records from all collections to a single
    text file.

    Arguments:
        args: Namespace object with command line arguments.
    '''
    logging.info(f'Saving to {args.file}')
    logging.debug(f'save {vars(args)}')

    open_db(args)
    
    try:
        mode = 'w' if args.force else 'x'
        with open(args.file, mode) as f:
            DB.save_as_json(f)
    except FileExistsError as err:
        logging.error(f'file exists: {args.file}, use --force to overwrite')
        exit(1)

#######################
#
# Top level method for restore command
#
#######################

def restore_records(args):
    '''
    The top level function, called from main when the command 
    is "restore".  Reads JSON records from a file previously
    created by a call to "save".

    Arguments:
        args: Namespace object with command line arguments.
    '''
    logging.debug(f'restore {vars(args)}')

    get_names_and_create_db(args)

    logging.info(f'DB:restoring dox file: {args.file}')
    DB.erase_database()

    with open(args.file) as f:
        for line in f:
            try:
                sep = line.find(':')
                collection = line[:sep]
                doc = line[sep+1:].strip()
                if args.preview:
                    print(doc)
                else:
                    DB.restore_from_json(collection, doc)
            except Exception as err:
                logging.error(err)

#######################
#
# Helper functions
#
#######################


def parse_journal(fn: Path, accounts: set, uids: set):
    '''
    Helper function for init and import commands.  Parses a Journal file,
    returns a list of account records and transaction records.

    Arguments:
        fn:        the name of the file to parse
        accounts:  set of account names in the DB (may be empty)
        uids:      ids of entries in the DB (may be empty)
    '''
    logging.info(f'importing journal file: {fn}')

    jp = JournalParser(accounts, uids)
    jp.parse_file(fn)
    DB.assign_uids(jp.entry_list)

    return jp.account_list, jp.transaction_list

def parse_csv_accounts(fn: Path):
    '''
    Helper function for init command.  Parses records from 
    a CSV file with account descriptions.

    Arguments:
        fn:        the name of the file to parse
    '''
    logging.info(f'importing account CSV file: {fn}')

    with(open(fn, newline='', encoding='utf-8-sig')) as csvfile:
        reader = csv.DictReader(csvfile)
        accts = [ Account(name='equity', category='equity') ]
        trans = []
        for rec in reader:
            if rec['fullname'] == 'equity':
                continue
            cat = rec['category'] or rec['fullname'].split(':')[0]
            a = Account(
                name = rec['fullname'],
                category = cat,
                abbrev = rec['abbrev'],
                parser = rec['parser']
            )
            accts.append(a)
            if rec['balance']:
                make_balance_transaction(rec, trans)

    return accts, trans

def parse_csv_regexp(fn: Path):
    '''
    Helper function for import command -- parses regular expression 
    records from a CSV file

    Arguments:
        fn:        the name of the file to parse
    '''
    with open(fn) as csvfile:
        reader = csv.DictReader(csvfile)
        # for rec in reader:
        #     e = RegExp(**rec)
        #     lst.append(e)
        res = [RegExp(**rec) for rec in reader]
    return res

def parse_csv_transactions(fn, pname, account, starting, ending, previous):
    '''
    Helper function for import command -- make a new Entry object for 
    every record in a CSV file.

    Arguments:
        fn:  the name of the CSV file
        pname:  the name of a parser (column mapping) that specifies
            which columns to use
        starting:  start date
        ending:  end date
        pevious:  set of UIDS of previously added entries

    Returns:
        a list of Entry objects
    '''
    logging.info(f'importing transaction CSV, file: {fn} account: {account}')
    res = []
    cmap = Config.CSV.colmaps[pname]
    logging.debug(f'  parser {pname} colmap {cmap}')
    with(open(fn, newline='', encoding='utf-8-sig')) as csvfile:
        reader = csv.DictReader(csvfile)
        for rec in reader:
            if list(rec.values()) == reader.fieldnames:
                continue
            rec_date = parse_date(cmap['date'](rec))
            if starting and rec_date < starting:
                continue
            if ending and rec_date > ending:
                continue
            desc = {
                'date': rec_date,
                'description': cmap['description'](rec),
                'amount': cmap['amount'](rec),
                'column': 'credit' if cmap['credit'](rec) else 'debit',
                'account': account,
                'tags': [Tag.U],
            }
            e = Entry(**desc)
            if e.hash in previous:
                continue
            res.append(e)
            logging.debug(f'  new entry: {e}')

    DB.assign_uids(res)
    return res


def get_names_and_create_db(args):
    '''
    Helper function used by restore_records and create_database.  Gets
    the database name from known locations, creates the database.

    Arguments:
        args: Namespace object with command line arguments.
    '''
    p = Path(args.file)
    if not p.exists():
        raise FileNotFoundError(f'no such file: {args.file}')

    dbname = args.dbname or os.getenv('DEX_DB') or Config.DB.name
    if dbname is None:
        raise ValueError(f'specify a database name')

    if not args.preview:
        if DB.exists(dbname) and not args.force:
            raise ValueError(f'database {dbname} exists; use --force to replace it')
        DB.create(dbname)    

def open_db(args):
    '''
    Helper function used by import and restore.  Gets database name,
    opens database.
    '''
    dbname = args.dbname or os.getenv('DEX_DB') or Config.DB.name
    if dbname is None:
        raise ValueError(f'specify a database name')
    DB.open(dbname)

def make_balance_transaction(rec, lst):
    '''
    Helper function for init_from_csv.  If a records has a
    value in the balance column make a transaction that 
    initializes the account balance.  Append the new transaction
    to lst.
    '''
    if not rec['date']:
        logging.error(f'init_database: missing date in {rec}')
        return
    debit = Entry(
        date = rec['date'],
        account = rec['fullname'],
        column = 'debit',
        amount = rec['balance'],
    )
    credit = Entry(
        date = rec['date'],
        account = 'equity',
        column = 'credit',
        amount = rec['balance'],
    )
    trans = Transaction(
        description = 'initial balance',
        entries = [debit,credit]
    )
    lst.append(trans)

