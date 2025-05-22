#  Methods for reading and writing database contents

import csv
import logging
from pathlib import Path
import re

from .DB import DB, Account, Entry, Transaction, RegExp, Category, Tag
from .config import Config
from .console import print_records, print_grid, print_info_table
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

    fn = Path(args.file)
    logging.info(f'DB:restoring docs file:{fn}')
    DB.erase_database()

    with open(fn) as f:
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
    if not args.preview:
        if DB.exists(args.dbname) and not args.force:
            raise ValueError(f'init: database {args.dbname} exists; use --force to replace it')
        DB.create(args.dbname)    

    p = Path(args.file)
    if not p.exists():
        raise FileNotFoundError(f'init_database: no file named {p}')
    fmt = p.suffix[1:]
    match fmt:
        case 'journal': init_from_journal(p, args.preview)
        case 'csv': init_from_csv(p, args.preview)
        case _: logging.error(f'init_database: unknown file extension: {p.suffix}')

def init_from_csv(fn: Path, preview: bool = False):
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
        # print_records(trans)
        any(t.clean() for t in trans)
        print_grid([[t.description,str(t.pdate),str(t.pamount)] for t in trans])
    else:
        for obj in accts + trans:
            try:
                logging.debug(f'save {obj}')
                obj.save()
            except Exception as err:
                logging.error(f'import: error saving {obj}')
                logging.error(err)

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
    
def init_from_journal(fn: Path, preview: bool = False):
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
        for lst in recs.values():
            # print_records(lst)
            for obj in lst:
                obj.clean()
                print(obj)
    else:
        DB.save_entries(recs['entries'])
        for obj in recs['accounts'] + recs['transactions']:
            try:
                logging.debug(f'save {obj}')
                obj.save()
            except Exception as err:
                logging.error(f'import: error saving {obj}')
                logging.error(err)

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
        self.accounts = [ Account(name = 'equity', category = 'equity')]
        self.entries = []
        self.transactions = []

        self.account_types = list(Category.__members__.keys())
        self.account_names = { 'equity' }
        self.transaction_date = None
        self.transaction_total = 0

    # def validate_account(self, acct):
    #     parts = acct.split(':')
    #     if parts[0] not in self.account_types:
    #         raise ValueError(f'unknown account type: {parts[0]}')

    def new_account(self, cmnd, comment=''):
        '''
        Helper function to create an Account document from the current line.

        Arguments:
           cmnd:  a string with the 'account' command followed by the account name
           comment: the comment field from the line

        Expected format of the command part
           account N C
        where N is the account name and C is a category name
        '''
        logging.debug(f'JournalParser.new_account: {cmnd} {comment}')
        lst = cmnd.split()
        name = lst[1].strip()
        if name == 'equity':
            return
        assert name not in self.account_names, f'  (duplicate account name: {name})'

        tags = { }
        for seg in comment.split(','):
            if m := re.search(r'(\w+):(.*)', seg):
                tags[m[1]] = m[2].strip()
        if 'type' in tags:
            tags['category'] = tags['type']
        logging.debug(tags)

        acct = Account(
            name = name, 
            category = tags.get('category') or name.split(':')[0],
            abbrev = tags.get('abbrev'),
            parser = tags.get('parser') 
        )
        self.accounts.append(acct)
        self.account_names.add(name)

    def new_transaction(self, date, comment=''):
        '''
        Helper function to create a Transaction object from the current line.

        Arguments:
           date: the date from the front of the line
           comment: the comment field from the line
        '''
        logging.debug(f'JournalParser.new_transaction {date} {comment}')
        m = re.match(r'(\d{4}-\d{2}-\d{2})(.*)', date)
        self.transaction_date = m.group(1)
        self.transaction_total = 0
        trans = Transaction(
            description = m.group(2).strip(),
        )
        # comment = tokens[0].strip() if tokens else ''
        trans.comment = comment.strip()
        trans.tags = [f'#{s[:-1]}' for s in re.findall(r'\w+:', comment)]
        self.transactions.append(trans)

    def new_entry(self, cmnd, desc=''):
        '''
        Helper function to create a new Entry object.  Appends the
        new object to the entries list of the most recent Transaction
        (which means it raises an exception if there is no Transaction).

        Arguments:
           cmnd: a string with the account name and amount
           comment: the comment field from the line
        '''
        logging.debug(f'JournalParser.new_entry {cmnd} {desc}')
        parts = cmnd.strip().split()
        acct = parts[0]
        if acct not in self.account_names:
            raise ValueError(f'unknown account: {acct}')
        
        if len(parts) > 1:
            amount = parse_amount(parts[1])
            self.transaction_total += amount
        else:
            amount = -self.transaction_total

        # desc = tokens[0].strip() if tokens else ''
        tags = re.findall(r'\w+:', desc)
        col = 'credit' if amount < 0 else 'debit'
        trans = self.transactions[-1]
        if trans.isbudget:
            tags.append(Tag.B)
        entry = Entry(
            date = self.transaction_date,
            description = desc.strip(),
            account = acct,
            column = col,
            amount = abs(amount),
            tags = tags,
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
                            func(cmnd, *comment)
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
# Top level method for parsing a file to import new records to a DB
#

def import_records(args):
    '''
    The top level function, called from main when the command 
    is "import".  Parses one or more CSV files to create new Entry
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
    Parse CSV files downloaded from financial institutions
    '''
    for path in args.files:
        if not path.is_file():
            logging.error(f'import: no file named {path}')
            continue
        if path.suffix == '.journal':
            recs = import_from_journal(path)
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
            DB.save_entries(recs)

def import_regexp(args):
    '''
    Import regular expression records from CSV files
    '''
    DB.delete_regexps()
    for fn in args.files:
        with open(fn) as csvfile:
            reader = csv.DictReader(csvfile)
            for rec in reader:
                e = RegExp(**rec)
                logging.debug(f'import: {e}')
                if args.preview:
                    print(e)
                else:
                    e.save()

def import_from_journal(fn):
    logging.error(f'import:  journal format not implemented')
    return []
    
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
