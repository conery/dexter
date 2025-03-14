# Print or update transactions

import logging

from .schema import Transaction, Entry
from .DB import DB
from .console import print_transaction_table

def select_transactions(args):
   '''
   Display transactions in a table in the terminal window.  Command line
   options specify constraints:  dates, amounts, accounts, descriptions
   (use --help to see the full list).

   Use --entry to search for individual debit or credit entries, otherwise
   the search will look for full transactions.

   Use --update to update the matched transactions.  The same update will
   be applied to all matching items.

   Other options:
      --total will print the total amount of all items
      --csv will print items in CSV format
   '''

   # cmap = {
   #    'transactions': Transaction,
   #    'entries':  Entry
   # }

   # for cname, cls in cmap.items():
   #    if cname.startswith(args.collection.lower()):
   #       collection = cls
   #       logging.debug(f'select {cname}')
   #       break
   # else:
   #    logging.debug(f'unknown collection')

   logging.debug('select')

   if args.entry:
      dct = DB.entry_constraints
      cls = Entry
   else:
      dct = DB.transaction_constraints
      cls = Transaction

   kwargs = {}
   for name in dct:
      if val := vars(args).get(name):
         kwargs[name] = val
   
   logging.debug(f'select {cls} {kwargs}')
   print_transaction_table(DB.select(cls, **kwargs))

