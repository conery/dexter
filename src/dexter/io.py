#  Methods for reading and writing database contents

import csv
import logging
from pathlib import Path
import re

from .DB import DB, Account, Entry, Transaction, Category
from .config import Config
from .util import parse_date

###
#
# Methods for exporting and importing records from a text file.  
#

def export_records(args):
    '''
    The top level function, called from main when the command 
    is "export".  Writes records from all collections to a single
    text file.

    Arguments:
        args: Namespace object with command line arguments.
    '''
    logging.info(f'Exporting to {args.file}')
    logging.debug(f'export {vars(args)}')
    try:
        mode = 'w' if args.force else 'x'
        with open(args.file, mode) as f:
            DB.save_records(f)
    except FileExistsError as err:
        logging.error(f'file exists: {args.file}, use --force to overwrite')
        exit(1)

def import_records(args):
    '''
    The top level function, called from main when the command 
    is "import".  Redirects to the method that will load the data,
    using the file name extension or command line argument to 
    determine the input file format.

    Arguments:
        args: Namespace object with command line arguments.
    '''
    logging.debug(f'import {vars(args)}')

    p = Path(args.file)
    fmt = args.format or p.suffix[1:]
    match fmt:
        case 'docs': import_docs(p)
        case 'journal': import_journal(p)
        case _: logging.error(f'init: unknown file extension:{p.suffix}')

# Import records from a docs file (created by a previous call to
# export_records)

def import_docs(fn: Path):
    '''
    Read accounts and transactions from a docs file.  Erases any
    previous documents in the database.

    Arguments:
        fn: path to the input file
    '''
    logging.info(f'DB:importing docs file:{fn}')
    DB.erase_database()

    with open(fn) as f:
        for line in f:
            try:
                sep = line.find(':')
                collection = line[:sep]
                doc = line[sep+1:].strip()
                DB.add_record(collection, doc)
            except Exception as err:
                logging.error(err)

# Import records from a .journal file

def import_journal(fn: Path):
    '''
    Read accounts and transactions from a plain text accounting
    (.jorurnal) file.  Erases any previous documents in the database.

    Arguments:
        fn: path to the input file
    '''
    logging.info(f'DB:importing journal file:{fn}')
    DB.erase_database()
    for obj in JournalParser().parse_file(fn):
        obj.save()

def parse_amount(s):
    '''
    Convert a string with dollar signs, commas, and periods into a
    dollar amount.
    '''
    s = re.sub(r'[,$]','',s)
    return float(s)

class JournalParser:
    '''
    Translate statements in a .journal file (the format used by
    hldeger and other "plain text accounting") apps.

    The algorithm creates one DB document (an Account, a Transaction,
    or an Entry) for each line in the file.  It assumes that when it
    sees a line for an Entry it can append it to the current Transaction.
    '''

    def __init__(self):
        '''
        Initialize the data structures that will hold the records
        to insert.
        '''
        self.accounts = []
        self.entries = []
        self.transactions = []

        self.account_types = list(Category.__members__.keys())
        self.account_names = set()
        self.transaction_date = None

    # def validate_account(self, acct):
    #     parts = acct.split(':')
    #     if parts[0] not in self.account_types:
    #         raise ValueError(f'unknown account type: {parts[0]}')

    def new_account(self, cmnd, comment):
        '''
        Helper function to create an Account document from the current line.

        Expected format:
           account G N
        where G is a single-letter account type and N is the account name.
        '''
        logging.debug(f'JournalParser.new_account "{cmnd}"')
        _, cat, spec = cmnd.split()
        assert cat in self.account_types, f'  (unknown category: {cat})'
        assert spec not in self.account_names, f'  (duplicate account name: {spec})'
        acct = Account(
            name=spec, 
            category=cat,
        )
        if len(comment) > 0:
            acct.note = comment[0].strip()
        self.accounts.append(acct)
        self.account_names.add(spec)

    def new_transaction(self, cmnd, comment):
        '''
        Helper function to create a Transaction object from the current line.
        '''
        logging.debug(f'JournalParser.new_transaction "{cmnd}"')
        m = re.match(r'(\d{4}-\d{2}-\d{2})(.*)', cmnd)
        self.transaction_date = m.group(1)
        trans = Transaction(
            description = m.group(2).strip(),
        )
        if len(comment) > 0:
            trans.comment = comment[0].strip()
        self.transactions.append(trans)

    def new_entry(self, cmnd, comment):
        '''
        Helper function to create a new Entry object.  Appends the
        new object to the entries list of the most recent Transaction
        (which means it raises an exception if there is no Transaction).
        '''
        logging.debug(f'JournalParser.new_entry {cmnd}')
        acct, amt = cmnd.split()
        # self.validate_account(acct)
        if acct not in self.account_names:
            raise ValueError(f'unknown account: {acct}')
        amount = parse_amount(amt)
        desc = comment[0].strip() if comment else ''
        col = 'credit' if amount < 0 else 'debit'
        trans = self.transactions[-1]
        entry = Entry(
            uid = '',               # UIDs not needed in .journal files
            date = self.transaction_date,
            description = desc,
            account = acct,
            column = col,
            amount = abs(amount),
        )
        trans.entries.append(entry)
        self.entries.append(entry)

    def parse_file(self, fn):
        '''
        Parse a file, saving account names and transactions in
        instance variables.

        Arguments:
            fn: path to the input file
        '''
        patterns = [
            (r'account', self.new_account),
            (r'\d{4}-\d{2}-\d{2}', self.new_transaction),
            (r'\s+\w+', self.new_entry),
        ]
        with open(fn) as f:
            while line := f.readline():
                cmnd, *comment = re.split(r'[;#]', line.rstrip())
                if len(cmnd) == 0:
                    continue
                try:
                    for pat, func in patterns:
                        if re.match(pat,cmnd):
                            func(cmnd,comment)
                            break
                    else:
                        raise ValueError('unknown statement')
                except Exception as err:
                    logging.error(f'JournalParser: error in {cmnd}')
                    logging.error(err)
            logging.debug(f'End of file')

        # return objects in the order we want them saved
        return self.accounts + self.entries + self.transactions

###
#
# Top level method for parsing a CSV file to add new records to a DB
#

def add_records(args):
    '''
    The top level function, called from main when the command 
    is "add".  Parses one or more CSV files to create new Entry
    documents.

    Arguments:
        args: Namespace object with command line arguments.
    '''
    p = Path(args.path)
    if p.is_dir():
        files = collect_all(p) 
    elif p.is_file():
        files = collect_one(p, args.account)
    else:
        raise FileNotFoundError(f'add_records: no such file or directory: {args.path}')
    for fn, parser in files:
        parse_file(fn, parser, args.start_date, args.end_date)
    
def collect_all(dirname):
    '''
    Helper function for add_records.  Find all CSV files in a
    directory, make sure there is a parser for each file.

    Arguments:
        dirname:  the name of the directory to scan

    Returns:
        a list of tuples containing the name of a file and the
        name of the parser to use for that file.
    '''
    files = [ ]
    for path in dirname.iterdir():
        if path.suffix not in ['.csv','.CSV']:
            continue
        if path.stem not in Config.parsers.keys():
            logging.error(f'collect_all: no parser for {path.stem}')
            continue
        files.append((path, Config.parsers[path.stem]))
    return files

def collect_one(path, account):
    '''
    Helper function for add_records.  Ensure the file is a CSV
    file and there is a parser for the file.

    Arguments:
        path:  the name of the file
        account:  the name of the account (optional)
    '''
    if path.suffix not in ['.csv','.CSV']:
        raise ValueError(f'collect_one: expected CSV file, not {path}')
    parser = account or path.stem
    if parser not in Config.parsers.keys():
        raise ValueError(f'collect_one: no parser for {parser}')
    return [(path,Config.parsers[parser])]

def parse_file(fn, pname, starting, ending):
    '''
    Make a new Entry object for every record in a CSV file.

    Arguments:
        fn:  the name of the CSV file
        pname:  the name of a parser (column mapping) that specifies
            which columns to use
        starting:  start date
        ending:  end date

    Returns:
        a list of Entry objects
    '''
    res = []
    cmap = Config.colmaps[pname]
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
                'account': pname,
            }
            e = Entry(**desc)
            logging.debug(e)
    return res
