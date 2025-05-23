# Print or update transactions

import logging

from .DB import DB, Transaction, Entry
from .config import Config
from .console import print_transaction_table, print_journal_transactions

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
   DB.open(args.dbname)

   if args.entry:
      dct = DB.entry_constraints
      order = DB.entry_order
      cls = Entry
   else:
      dct = DB.transaction_constraints
      order = DB.transaction_order
      cls = Transaction
   logging.debug(f'select {cls}')

   kwargs = {}
   for name in dct:
      if val := vars(args).get(name):
         kwargs[name] = val
         logging.debug(f'  {name} = {val}')

   if 'start_date' not in kwargs:
      kwargs['start_date'] = Config.start_date
   
   recs = DB.select(cls, **kwargs)

   if args.journal:
      if args.entry:
         logging.error("select:  journal format not valid for entries")
         return
      print_journal_transactions(
         recs,
         abbrev = not args.fullname,
         order_by = order[args.order_by],
      )
   else:
      print_transaction_table(
         recs, 
         name='Entries' if args.entry else 'Transactions',
         order_by = order[args.order_by],
         abbrev = not args.fullname,
         as_csv = args.csv,
      )

