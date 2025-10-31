#
# TUI widget for displaying tables of transactions
#

from rich.text import Text

from textual.app import App
from textual.binding import Binding
from textual.message import Message
from textual.widgets import DataTable

from dexter.console import format_amount
from dexter.DB import DB, Transaction, Entry, Tag, Column as DBColumn

def format_flag(rec, col):
    lst = rec[col]
    sym = '🔴' if Tag.U.value in lst else ' '
    return Text(sym, justify='center')

def format_date(rec, col):
    val = rec[col]
    return Text(str(val))

def format_account(rec, col):
    return Text(rec[col])

def format_account_abbrev(rec, col):
    return Text(DB.abbrev(rec[col]))

def format_string(rec, col):
    return Text(rec[col] or '')

def format_unsigned_amount(rec, col):
    s = format_amount(rec[col], dollar_sign=True)
    return Text(s, justify='right')

def format_signed_amount(rec, col):
    amount = rec[col]
    style = ''
    if rec['column'] == DBColumn.cr:
        amount = -amount
        style = 'red'
    # s = format_amount(amount, dollar_sign=True, accounting=True)
    s = format_amount(amount, dollar_sign=True)
    return Text(s, justify='right',style=style)

def format_tags(rec, col):
    lst = rec[col]
    if Tag.U.value in lst:
        lst.remove(Tag.U.value)    
    return Text(', '.join(lst))

entry_columns = [
    (' ', 3, format_flag, 'tags'),
    ('Date', 10, format_date, 'date'),
    ('Account', 30, format_account, 'account'),
    ('Amount', 12, format_signed_amount, 'amount'),
    ('Description', 40, format_string, 'description'),
    ('Tags', 30, format_tags, 'tags'),
]

transaction_columns = [
    ('Date', 10, format_date, 'pdate'),
    ('Credit', 15, format_account_abbrev, 'pcredit'),
    ('Debit', 15, format_account_abbrev, 'pdebit'),
    ('Amount', 12, format_unsigned_amount, 'pamount'),
    ('Description', 40, format_string, 'description'),
    ('Comment', 30, format_string, 'comment'),
    ('Tags', 30, format_tags, 'tags'),
]

class ColSpec:

    def __init__(self, header, width, justify='left', formatter=str):
        self.header = header
        self.width = width
        self.justify = justify
        self.formatter = formatter

    def render(self, value):
        s = self.formatter(value)
        return Text(s, justify=self.justify)
    
    def header(self):
        return self.header
    
    def width(self):
        return self.width
    
class TransactionTable(DataTable):
    '''
    Display entries or transactions in a data table
    '''

    BINDINGS = [
        Binding('ctrl+o,enter', 'open_editor', description='Open Editor', key_display='^O'),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.cursor_type = 'row'
        self.cell_padding = 2
        self.header_height = 2
        self.records = None

    def add_records(self, records, args):
        self.records = records
        headers = entry_columns if args.entry else transaction_columns
        for spec in headers:
            self.add_column(spec[0], width=spec[1])
        for rec in records:
            row = []
            for spec in headers:
                row.append(spec[2](rec, spec[3]))
            self.add_row(*row)
        self.log(f'added {len(records)} rows to table')

    def action_open_editor(self) -> None:
        rec = self.records[self.cursor_row]
        if isinstance(rec, Entry):
            self.log('coming soon...')
            return
        cb = self.validate_transaction
        self.post_message(self.OpenModal(rec, cb))

    def validate_transaction(self, resp: bool) -> None:
        self.log('done')

    class OpenModal(Message):

        def __init__(self, rec, cb):
            self.cb = cb
            self.rec = rec
            super().__init__()

    class LogMessage(Message):

        def __init__(self, msg: str) -> None:
            self.text = msg
            super().__init__()

    def log(self, msg):
        self.post_message(self.LogMessage(msg))
