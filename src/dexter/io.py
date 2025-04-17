#  Methods for reading and writing database contents

import csv
import logging
from pathlib import Path
import re

from .DB import DB, Account, Entry, Transaction, RegExp, Category
from .config import Config
from .console import print_records
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
            DB.export_as_json(f)
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
        case 'docs': import_docs(p, args.preview)
        case 'journal': import_journal(p, args.preview)
        case _: logging.error(f'init: unknown file extension:{p.suffix}')
    if args.regexp and not args.preview:
        import_regexp(args.regexp)

# Import records from a docs file (created by a previous call to
# export_records)

def import_docs(fn: Path, preview):
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
                DB.import_from_json(collection, doc)
            except Exception as err:
                logging.error(err)

# Import records from a .journal file

def import_journal(fn: Path, preview):
    '''
    Read accounts and transactions from a plain text accounting
    (.jorurnal) file.  Erases any previous documents in the database.

    Arguments:
        fn: path to the input file
        preview:  if True print documents instead of saving them
    '''
    logging.info(f'DB:importing journal file:{fn}')
    recs = JournalParser().parse_file(fn)
    if preview:
        print_records(recs)
    else:
        DB.erase_database()
        DB.save_records(recs['entries'])
        for obj in recs['accounts'] + recs['transactions']:
            try:
                logging.debug(f'save {obj}')
                obj.save()
            except Exception as err:
                logging.error(f'import: error saving {obj}')
                logging.error(err)

# Read regular expression descriptions from a CSV file

def import_regexp(fn):
    with open(fn) as csvfile:
        reader = csv.DictReader(csvfile)
        for rec in reader:
            e = RegExp(**rec)
            e.save()

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
        self.transaction_total = 0

    # def validate_account(self, acct):
    #     parts = acct.split(':')
    #     if parts[0] not in self.account_types:
    #         raise ValueError(f'unknown account type: {parts[0]}')

    def new_account(self, cmnd, tokens):
        '''
        Helper function to create an Account document from the current line.

        Arguments:
           cmnd:  a string with the 'account' command followed by the account name
           tokens:  list of strings with the remainder of the line

        Expected format of the command part
           account N C
        where N is the account name and C is a category name
        '''
        logging.debug(f'JournalParser.new_account: {cmnd} {tokens}')
        lst = cmnd.split()
        name = lst[1].strip()
        assert name not in self.account_names, f'  (duplicate account name: {name})'

        comment = tokens[0].strip() if tokens else ''
        if m := re.search(r'(.*?)type: (\w+)', comment):
            cat = m[2]
        else:            
            cat = name.split(':')[0]

        acct = Account(
            name=name, 
            category=cat,
            comment=comment,
        )
        self.accounts.append(acct)
        self.account_names.add(name)

    def new_transaction(self, date, tokens):
        '''
        Helper function to create a Transaction object from the current line.

        Arguments:
           date: the date from the front of the line
           tokens:  list of strings with the remainder of the line
        '''
        logging.debug(f'JournalParser.new_transaction {date} {tokens}')
        m = re.match(r'(\d{4}-\d{2}-\d{2})(.*)', date)
        self.transaction_date = m.group(1)
        self.transaction_total = 0
        trans = Transaction(
            description = m.group(2).strip(),
        )
        comment = tokens[0].strip() if tokens else ''
        trans.comment = comment
        self.transactions.append(trans)

    def new_entry(self, cmnd, tokens):
        '''
        Helper function to create a new Entry object.  Appends the
        new object to the entries list of the most recent Transaction
        (which means it raises an exception if there is no Transaction).

        Arguments:
           cmnd: a string with the account name and amount
           tokens:  list of strings with the remainder of the line
        '''
        logging.debug(f'JournalParser.new_entry {cmnd} {tokens}')
        parts = cmnd.strip().split()
        acct = parts[0]
        if acct not in self.account_names:
            raise ValueError(f'unknown account: {acct}')
        
        if len(parts) > 1:
            amount = parse_amount(parts[1])
            self.transaction_total += amount
        else:
            amount = -self.transaction_total

        desc = tokens[0].strip() if tokens else ''
        col = 'credit' if amount < 0 else 'debit'
        trans = self.transactions[-1]
        entry = Entry(
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

        # # return objects in the order we want them saved
        # return self.accounts + self.entries + self.transactions
        return {
            'accounts': self.accounts,
            'entries': self.entries,
            'transactions': self.transactions,
        }

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
    for path in args.files:
        logging.info(f'Add records from {path}')
        if not path.is_file():
            logging.error(f'add: no file named {path}')
            continue            
        basename = args.account or path.stem
        alist = DB.find_account(basename)
        if len(alist) == 0:
            logging.error(f'add: no account name matches {basename}')
            continue
        if len(alist) > 1:
            logging.error(f'add: ambiguous account name {basename}')
            continue
        account = alist[0].name
        parser = account.split(':')[0]
        if parser not in Config.colmaps.keys():
            logging.error(f'add: no parser for {account}')
            continue
        recs = parse_file(path, parser, account, args.start_date, args.end_date, DB.uids())
        if args.preview:
            print_records(recs)
        else:
            DB.save_records(recs)
    
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
    logging.debug(f'parsing {fn} {pname} {account} {starting} {ending}')
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
            }
            e = Entry(**desc)
            if e.hash in previous:
                continue
            res.append(e)
            logging.debug(f'record: {e}')
    return res
