#  Methods for reading and writing database contents

import csv
import logging
import os
from pathlib import Path
import re

from .DB import DB, Account, Entry, Transaction, RegExp, Category, Tag
from .config import Config
from .console import print_records, print_grid, print_info_table
from .journal import JournalParser
from .util import parse_date

###
#
# Top level method for the info command
#

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

###
#
# Top level method for saving all documents to a JSON file
#

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
    DB.open(args.dbname)

    try:
        mode = 'w' if args.force else 'x'
        with open(args.file, mode) as f:
            DB.save_as_json(f)
    except FileExistsError as err:
        logging.error(f'file exists: {args.file}, use --force to overwrite')
        exit(1)

###
#
# Top level method for restoring a database from a JSON file
# created by a previous call to save
#

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

###
#
# Top level method for initializing a database
#

def init_database(args):
    '''
    The top level function, called from main when the command 
    is "init".  Initializes a new database using records from
    either a .journal file or a CSV file.

    Arguments:
        args: Namespace object with command line arguments.
    '''
    get_names_and_create_db(args)

    accts = Path(args.file)
    fmt = accts.suffix[1:]
    match fmt:
        case 'journal': parse_and_save_journal(accts, args.preview)
        case 'csv': init_from_csv(accts, args.preview)
        case _: logging.error(f'init_database: unknown file extension: {accts.suffix}')

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

    dbname = args.dbname or os.getenv('DEX_DB') or Config.dbname
    if dbname is None:
        raise ValueError(f'specify a database name')

    if not args.preview:
        if DB.exists(dbname) and not args.force:
            raise ValueError(f'database {dbname} exists; use --force to replace it')
        DB.create(dbname)    

def init_from_csv(fn: Path, preview: bool = False):
    '''
    Helper function for init_database.  Parses records from a CSV file.
    '''
    logging.info(f'importing CSV file: {fn}')
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
    if preview:
        print_records(accts)
        any(t.clean() for t in trans)
        print_grid([[t.description,str(t.pdate),str(t.pamount)] for t in trans])
    else:
        DB.save_records(accts)
        DB.save_records(trans)

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

###
#
# Top level method for parsing a file to import new records to a DB
#

def import_records(args):
    '''
    The top level function, called from main when the command 
    is "import".  Parses one or more files to create new Entry
    or Regexp documents

    Arguments:
        args: Namespace object with command line arguments.
    '''
    DB.open(args.dbname)
    if args.regexp:
        import_regexp(args)
    else:
        import_entries(args)

def import_entries(args):
    '''
    Helper function for import_records -- determine the type of each
    file (CSV or Journal), parse the file and save records
    '''
    for path in args.files:
        if not path.is_file():
            logging.error(f'import: no file named {path}')
            continue
        if path.suffix == '.journal':
            recs = import_journal(path, args.preview)
        elif path.suffix != '.csv':
            logging.error(f'import: unknown extension {path.suffix}')
        else:
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
            logging.debug(f'import_records: account {account} parser {parser}')
            if parser not in Config.colmaps.keys():
                logging.error(f'import: no parser for {account}')
                continue
            recs = parse_file(path, parser, account, args.start_date, args.end_date, DB.uids())
        if args.preview:
            print_records(recs)
        else:
            DB.assign_uids(recs)
            # for e in recs:
            #     e.save()
            DB.save_records(recs)

def import_regexp(args):
    '''
    Helper function for import_records -- import regular expression 
    records from CSV files
    '''
    DB.delete_regexps()
    for fn in args.files:
        lst = []
        with open(fn) as csvfile:
            reader = csv.DictReader(csvfile)
            for rec in reader:
                e = RegExp(**rec)
                lst.append(e)
        if args.preview:
            for e in lst:
                print(e)
        else:
            DB.save_records(lst)

def import_journal(fn: Path, preview: bool = False):
    '''
    Helper function for import_records.  Get a list of existing accounts,
    pass it to the function that parses the file and saves records.
    '''
    logging.info(f'importing journal file: {fn}')
    accts = set(DB.account_names(with_parts=False).keys())
    logging.debug(f'import_journal: accts {accts}')
    recs = JournalParser().parse_file(fn)
    if preview:
        for lst in recs.values():
            # print_records(lst)
            for obj in lst:
                obj.clean()
                print(obj)
    else:
        DB.assign_uids(recs['entries'])
        for lst in recs.values():
            DB.save_records(lst)

   
def parse_file(fn, pname, account, starting, ending, previous):
    '''
    Make a new Entry object for every record in a CSV file.

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
    logging.info(f'Parsing {fn}')
    logging.debug(f'  arguments: {pname} {account} {starting} {ending}')
    res = []
    cmap = Config.colmaps[pname]
    logging.debug(f'parser {pname} colmap {cmap}')
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
            logging.debug(f'record: {e}')
    return res

def parse_and_save_journal(fn: Path, preview: bool = False, accounts = None):
    '''
    Open a Journal file, parse the records, and (if preview is False) add
    them to the database

    Arguments:
        fn:         path to the Journal file
        preview:    if true print records but don't save them
        accoints:   optional list of account names from the database
    '''
    logging.info(f'parsing journal file: {fn}')

    jp = JournalParser()
    try:
        jp.parse_file(fn)
        jp.validate_entries()
    except Exception as err:
        logging.error(err)
        return

    if preview:
        for lst in [jp.account_list, jp.transaction_list, jp.entry_list]:
            for obj in lst:
                obj.clean()
                print(obj)
    else:
        DB.assign_uids(jp.entry_list)
        DB.save_records(jp.account_list)
        DB.save_records(jp.transaction_list)


###
#
# Top level method for exporting transactions
#

def export_records(args):
    '''
    The top level function, called from main when the command 
    is "export".

    Arguments:
        args: Namespace object with command line arguments.
    '''
    logging.error(f'export: not implemented')
