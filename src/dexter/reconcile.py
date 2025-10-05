# Reconcile credit card statements

from curses.ascii import ESC, ctrl
import logging

import click
from rich.table import Table, Row, Column as TableColumn

from .DB import DB, Entry, Tag, Column
from .console import console, format_amount
from .subset_sum import find_subset
from .util import debugging

####
#
# Fetch and organize the pending transactions (both purchases and payments)
#

def collect_card_transactions(cardname):
    '''
    Find pending transactions for cards.  Returns two items for each card:  
    the earliest pending card payment and a list of entries (either credits
    or debits) with dates earlier than the payment.  
    
    Note: if a transaction is a return it is put at the front of the list
    of purchases (card companies process these immedediately).
    '''
    kwargs = {'tag': Tag.P.value}
    if cardname is not None:
        kwargs['account'] = cardname
        
    res = { c.name: {'payment': list(), 'entries': list()} for c in DB.card_accounts() }
    for e in DB.select(Entry, **kwargs):
        dct = res[e.account]
        if Tag.Z.value in e.tags:
            dct['payment'].append(e)
        elif e.column == Column.dr:
            dct['entries'].insert(0,e)
        else:
            dct['entries'].append(e)

    empty = []
    for card, dct in res.items():
        if not (dct['payment'] and dct['entries']):
            empty.append(card)
        else:
            dct['payment'].sort(key = lambda e: e.date)
            dct['entries'] = [e for e in dct['entries'] if e.date < dct['payment'][0].date]

    for c in empty:
        del res[c]

    return res

def subset_sum(card):
    '''
    Convert transaction amounts to integer number of cents, call the subset sum
    method to find a subset of purchases that total to the sum of payments.

    To prevent roundoff errors, all amounts are rounded to the nearest integer
    and converted to an integer number of cents.
    '''
    logging.debug(f'subset sum {card}')
    target = int(round(100*card['payment'][0].amount))
    purchases = [int(round(-100*e.value)) for e in card['entries']]
    logging.debug(f'{target} {purchases}')
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
    '''
    Called when the --repl option is specified on the command line.  Displays
    one card at a time, showing the payment and the pending transactions.  Uses
    the subset sum algorithm to identify a set of transactions that were covered
    by the payment.
    '''

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
            g.add_row(str(e.date), desc, format_amount(e.value, dollar_sign=True), style=style)
        console.print(g)
        console.print()

    def display_card_recs(account, card, selected):
        console.clear()
        console.print(account, style='table_header')
        console.print()
        print_grid('Payment', card['payment'], [])
        print_grid('Purchases', card['entries'], selected)

    def display_no_transactions(account):
        console.clear()
        console.print(account, style='table_header')
        console.print()
        console.print(f'[red]No transactions for {account}')

    card_names = sorted(recs.keys())
    row = 0

    try:
        if not debugging():
            console.set_alt_screen(True)
        while len(card_names) > 0:
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
                    remove_tags(card, selected)
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

def reconcile_and_apply(recs):
    '''
    Called when --apply is specified on the command line.  Use the subset
    sum algorithm on each card.  If the selected entries are in a 
    concecutive block at the start of the list reconcile the card (remove
    the pending tag from the payment and the selected transactions).
    '''
    for card, dct in recs.items():
        row = [card]
        if lst := dct['payment']:
            selected = subset_sum(dct)
            if selected == set(range(len(selected))):
                logging.info(f'reconcile: remove tags from {card}')
                remove_tags(dct, selected)

def print_csv_rec(e):
    '''
    Helper for --csv option -- print comma-separated fields for a single
    entry
    '''
    desc = e.tref.description if e.tref else ''
    print(','.join([str(e.date), desc, str(e.value)]))

def print_preview(recs):
    '''
    Called if no action specified.  Print a table with one row for each
    card, showing the result of applying the subset sum algorithm.
    '''
    tbl = Table(
        TableColumn('Card', width=35),
        TableColumn('Statement Date', width=20),
        TableColumn('#Pending', width=11, justify='right'),
        TableColumn('Reconciled', justify='center'),
        title = 'Card Reconciliation Status',
        title_justify = 'left',
        title_style = 'table_header',
    )
    for card, dct in recs.items():
        row = [card]
        if lst := dct['payment']:
            row.append(str(lst[0].date))
            row.append(str(len(dct['entries'])))
            selected = subset_sum(dct)
            if selected == set(range(len(selected))):
                row.append('✅')
        else:
            row += ['','']
        tbl.add_row(*row)
    console.print(tbl)

def remove_tags(card, selected):
    '''
    Called from the command line or from the repl after the user decides
    the transactions identified by the subset sum algorithm are the
    purchases that were part of a payment.  Remove the #pending tags from
    the payment and the selected purchases.

    Note: the objects are updated in the DB but not reloaded (assuming
    we don't refer to them again after this update)

    TODO:  add method to DB class API to remove the tags
    '''
    logging.debug(f'remove tag from {card['payment'][0]}')
    card['payment'][0].update(pull__tags=Tag.Z.value)
    for i in selected:
        card['entries'][i].update(pull__tags=Tag.P.value)

def reconcile_statements(args):
    '''
    Find card payment transactions, match them with pending purchases and
    returns.

    Arguments:
        args:  command line arguments
    '''
    if args.preview:
        raise ValueError(f'reconcile: --preview not defined')

    DB.open(args.dbname)    
    logging.debug(f'reconcile {vars(args)}')

    card_names = [c.name for c in DB.card_accounts()]
    logging.debug(f'card names {card_names}')

    if args.card:
        alist = DB.find_account(args.card)
        if len(alist) == 0:
            raise ValueError(f'reconcile: no card matching {args.card}')
        if len(alist) > 1:
            raise ValueError(f'reconcile: ambiguous account, specify one of {[a.name for a in alist if a.name in card_names]} ')
        if alist[0].name not in card_names:
            raise ValueError(f'reconcile: {args.card} => {alist[0].name} does not match a credit card account name')

    recs = collect_card_transactions(args.card)

    if args.csv:
        for c, dct in recs.items():
            print(c)
            for e in dct['payment']:
                print_csv_rec(e)
            for e in dct['entries']:
                print_csv_rec(e)
            print()
    elif args.repl:
        reconcile_main_loop(recs)
    elif args.apply:
        reconcile_and_apply(recs)
    else:
        print_preview(recs)

