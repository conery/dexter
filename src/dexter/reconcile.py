# Reconcile credit card statements

from curses.ascii import ESC, ctrl
import logging

import click
from rich.table import Table, Row

from .DB import DB, Entry, Tag
from .console import console, format_amount
from .subset_sum import find_subset
from .util import debugging

####
#
# Fetch and organize the pending transactions (both purchases and payments)
#

def collect_card_transactions(cardname):
    '''
    Find all the Entry objects tagged `#pending`, organize them by account
    name with separate lists for debits and credits.
    '''
    kwargs = {'tag': Tag.P.value}
    if cardname is not None:
        kwargs['account'] = cardname
    res = { }
    for e in DB.select(Entry, **kwargs):
        dct = res.setdefault(e.account, {'debit': [], 'credit': []})
        dct[e.column.value].append(e)

    for card in res:
        cutoff = max(e.date for e in res[card]['debit'])
        res[card]['credit'] = [e for e in res[card]['credit'] if e.date <= cutoff]

    return res

def subset_sum(card):
    '''
    Convert transaction amounts to integer number of cents, call the subset sum
    method to find a subset of purchases that total to the sum of payments.
    '''
    target = int(100 * sum(e.amount for e in card['debit']))
    purchases = [int(100*e.amount) for e in card['credit']]
    node = find_subset(purchases, target)
    return node.members() if node else []

####
#
#  To reconcile a card we need to find all pending transactions with dates 
#  earlier than the card payment transaction, then find the subset which
#  has a total amount equal to the payment amount.  
#
#  Use a REPL that shows the card payments, and then when a card is selected,
#  show the subset of transactions that were identified (so the user can verify
#  the correct subset was found).
#

class KEY:
    PREV = chr(ESC) + '[' + 'A'
    NEXT = chr(ESC) + '[' + 'B'
    ACCEPT = ctrl('A')
    REFRESH = ctrl('R')

def reconcile_main_loop(recs):

    def print_grid(title, data, selected):
        console.print(f'[blue italic]{title}')
        g = Table.grid(padding=[0,2,0,1])
        g.add_column()
        g.add_column(width=60, no_wrap=True)
        g.add_column(justify='right')
        for i, e in enumerate(data):
            desc = e.tref.description if e.tref else '[red]missing tref; run "dex audit" to fix'
            # if i in selected:
            #     desc = '[blue]' + desc
            style = 'highlight' if i in selected else ''
            g.add_row(str(e.date), desc, format_amount(e.amount, dollar_sign=True), style=style)
        console.print(g)
        console.print()

    def display_card_recs(account, card, selected):
        console.clear()
        console.print(account, style='table_header')
        # tsum = sum(purchases[i].amount for i in selected)
        # g.add_row('payment amount', format_amount(rec.amount,dollar_sign=True))
        # if round(tsum,2) == round(rec.amount,2):
        #     g.add_row('purchases and credits', format_amount(round(tsum,2),dollar_sign=True),'✅')
        # else:
        #     delta = round(tsum-rec.amount,2)
        #     g.add_row('difference', format_amount(delta,dollar_sign=True),'❌')
        console.print()
        print_grid('Payments and Returns', card['debit'], [])
        print_grid('Purchases', card['credit'], selected)

    card_names = sorted(recs.keys())
    row = 0

    try:
        if not debugging():
            console.set_alt_screen(True)
        while len(recs) > 0:
            account = card_names[row]
            card = recs[account]
            selected = subset_sum(card)
            display_card_recs(account, card, selected)
            key = click.getchar()
            match key:
                case KEY.PREV:
                    row = (row - 1) % len(card_names)
                case KEY.NEXT:
                    row = (row + 1) % len(card_names)
                case KEY.ACCEPT:
                    # reconcile_payment(rec, purchases, selected, statement)
                    del card_names[row]
                    if card_names:
                        row = row % len(card_names)
                case _:
                    continue
    except KeyboardInterrupt:
        pass
    except EOFError:
        pass
    except Exception as err:
        console.print(f'[bold red]{err}')

    console.set_alt_screen(False)

def print_csv_rec(e):
    desc = e.tref.description if e.tref else ''
    print(','.join([str(e.date), desc, str(e.value)]))

def reconcile_statements(args):
    '''
    Find card payment transactions, match them with pending purchases and
    returns.

    Arguments:
        args:  command line arguments
    '''

    DB.open(args.dbname)
    logging.debug(f'reconcile {vars(args)}')

    recs = collect_card_transactions(args.card)

    if args.preview:
        for c, dct in recs.items():
            print(c)
            for e in dct['debit']:
                print_csv_rec(e)
            for e in dct['credit']:
                print_csv_rec(e)
    else:
        reconcile_main_loop(recs)

