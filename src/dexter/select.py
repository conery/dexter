# Print or update transactions

from .DB import DB

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
    print('select transactions', vars(args))
    