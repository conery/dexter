# Budget allocation

from datetime import date, datetime
import logging
from pathlib import Path
import tomllib

from .DB import DB, Transaction, Entry
from .config import Config, Tag
from .console import console

def fill(args):
    '''
    Read a TOML file with specifications of income sources and budget categories,
    add a transaction that implements the transfers.

    Arguments:
        args: command line arguments
    '''
    date = transaction_date(args)

    if not args.files:
        if spec := Config.Budget.specs:
            add_budget_transaction(date, spec)
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
                add_budget_transaction(date, cfg)

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

def add_budget_transaction(date, dct):
    console.print(date)
    console.print(dct['income'])
    console.print(dct['allocation'])
    console.print(dct['remainder'])
