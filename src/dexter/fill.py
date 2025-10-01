# Budget allocation

from datetime import date, datetime
import logging
from pathlib import Path
import tomllib

from .DB import DB, Transaction, Entry, Column, Tag
from .config import Config
from .console import console, print_journal_transactions, print_csv_transactions

def fill(args):
    '''
    Read a TOML file with specifications of income sources and budget categories,
    add a transaction that implements the transfers.

    Arguments:
        args: command line arguments
    '''
    DB.open(args.dbname)
    tlist = []
    dlist = []

    date = transaction_date(args)

    if not args.files:
        if spec := Config.Budget.specs:
            t, d = budget_transaction(date, spec)
            if t is not None:
                tlist.append(t)
                dlist += d
        else:
            logging.error(f'fill: specify a budget file name or add a budget to the config file')
    else:
        for fn in args.files:
            p = Path(fn)
            if not p.exists():
                console.print(f'[red]fill: no such file: {fn}')
                continue
            with open(p, 'rb') as f:
                cfg = tomllib.load(f)
                t, d = budget_transaction(date, cfg)
                if t is not None:
                    tlist.append(t)
                    dlist += d

    if args.preview:
        print_journal_transactions(tlist)
        print_csv_transactions(dlist)
    else:
        for t in dlist:
            t.tags = [Tag.A.value]
            t.save()
        DB.save_records(tlist)

def transaction_date(args):
    '''
    If the user specified a date with --date use it.  Otherwise if a month was
    specified with --month the command line parser has saved the date in args.start_date.
    If neither was given use the start of the previous month.
    '''
    if args.date:
        res = args.date
    elif args.month:
        res = args.start_date
    else:
        today = date.today()
        m = (today.month - 2) % 12 + 1
        y = today.year if today.month > 1 else today.year - 1
        res = today.replace(year=y, month=m, day=1)
    return res

def budget_transaction(date, dct):
    '''
    Create a new transaction using the specs from a TOML file.

    Arguments:
        date:  the date to use for the new postings 
        dct:   the specs from the TOML file

    Returns:
        a new Transaction object
        a list of transactions used for deposits
    '''
    deposits = fetch_deposits(dct['income'])
    if len(deposits) == 0:
        console.print(f'[blue italic]fill: no deposits to allocate')
        return None, []
    trans = Transaction(
        description = 'fill envelopes',
    )
    available = sum(t.pamount for t in deposits)
    logging.debug(f'fill: available to distribute: {available}')
    add_debits(trans, deposits, date)
    dist = add_credits(trans, dct['allocation'], date, available)
    logging.debug(f'fill: distributed {dist}')
    if available > dist:
        spec = [{ 'category': dct['remainder'], 'amount': available-dist}]
        add_credits(trans, spec, date, available)
    return trans, deposits

def fetch_deposits(sources):
    '''
    Fetch the income transactions that will be used to fill the envelopes.
    Skips transactions that have already been used.

    Arguments:
        sources:  a list of patterns to look for; each pattern has an
                  income source and an account name

    Returns:
        a list of deposit transactions
    '''
    res = []
    for spec in sources:
        for rec in DB.select(Transaction, credit=spec['source'], debit=spec['account']):
            if Tag.A.value in rec.tags:
                continue
            logging.debug(f'fill: deposit: {rec}')
            res.append(rec)
    return res

def add_debits(trans, lst, date):
    '''
    Update the new transaction by adding a debit entry for each deposit.
    '''
    for rec in lst:
        e = Entry(
            date = date,
            description = f'deposit to {rec.pdebit} on {rec.pdate}',
            account =  rec.pcredit,
            column = Column.dr,
            amount = rec.pamount,
            tags = [Tag.B.value],
        )
        trans.entries.append(e)
        logging.debug(f'fill: debit: {e}')

def add_credits(trans, lst, date, avail):
    '''
    Update the new transaction by adding a credit entry for each expense
    category.  Returns the sum of the amounts allocated.    
    '''
    alloc = 0
    for rec in lst:
        if alloc + rec['amount'] > avail:
            console.print(f'[red]fill: allocation {rec} exceeds available {avail-alloc}, skipped')
            continue
        credit = DB.fullname(rec['category'])
        if credit is None:
            console.print(f'[red]fill: unknown account: {rec['category']}, skipped')
            continue            
        e = Entry(
            date = date,
            description = f'fill',
            account = credit,
            column = Column.cr,
            amount = rec['amount'],
            tags = [Tag.B.value],
        )
        trans.entries.append(e)
        alloc += rec['amount']
        logging.debug(f'fill: credit: {e}')
    return alloc
