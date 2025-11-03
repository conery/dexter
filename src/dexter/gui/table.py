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
from dexter.repl import make_candidate, apply_regexp
from dexter.util import parse_date

# def format_flag(rec, col):
#     lst = rec[col]
#     sym = '🔴' if Tag.U.value in lst else ' '
#     return Text(sym, justify='center')

# def format_date(rec, col):
#     val = rec[col]
#     return Text(str(val))

# def format_account(rec, col):
#     return Text(rec[col])

# def format_account_abbrev(rec, col):
#     return Text(DB.abbrev(rec[col]))

# def format_string(rec, col):
#     return Text(rec[col] or '')

# def format_unsigned_amount(rec, col):
#     s = format_amount(rec[col], dollar_sign=True)
#     return Text(s, justify='right')

# def format_signed_amount(rec, col):
#     amount = rec[col]
#     style = ''
#     if rec['column'] == DBColumn.cr:
#         amount = -amount
#         style = 'red'
#     # s = format_amount(amount, dollar_sign=True, accounting=True)
#     s = format_amount(amount, dollar_sign=True)
#     return Text(s, justify='right',style=style)

# def format_tags(rec, col):
#     lst = rec[col]
#     if Tag.U.value in lst:
#         lst.remove(Tag.U.value)    
#     return Text(', '.join(lst))

# entry_columns = [
#     (' ', 3, format_flag, 'tags'),
#     ('Date', 10, format_date, 'date'),
#     ('Account', 30, format_account, 'account'),
#     ('Amount', 12, format_signed_amount, 'amount'),
#     ('Description', 40, format_string, 'description'),
#     ('Tags', 30, format_tags, 'tags'),
# ]

# transaction_columns = [
#     ('Date', 10, format_date, 'pdate'),
#     ('Credit', 15, format_account_abbrev, 'pcredit'),
#     ('Debit', 15, format_account_abbrev, 'pdebit'),
#     ('Amount', 12, format_unsigned_amount, 'pamount'),
#     ('Description', 40, format_string, 'description'),
#     ('Comment', 30, format_string, 'comment'),
#     ('Tags', 30, format_tags, 'tags'),
# ]

class ColSpec:
    '''
    Create an instance of this class for each column in a table.  The object
    has specifications for the column name and width and methods for converting
    data into strings to insert in the table and to convert data from the
    table back into its original form.
    '''

    def __init__(self, name:str, width:int, attr: str) -> None:
        '''
        Initialize a new object.

        Arguments:
            name:  the column name
            width:  column width
            attr:  data attribute to display in this column
        '''
        self._name = name
        self._width = width
        self._attr = attr

    @property
    def name(self):
        return self._name
    
    @property
    def width(self):
        return self._width

    @property
    def attr(self):
        return self._attr
        
    @property
    def key(self):
        return self._name
    
    def render(self, rec, x) -> str:
        '''
        Return the contents of field x (assumed to be a string)
        '''
        return rec[x]
    
    def value(self, x):
        '''
        In the base class items are stored as strings and the value
        returned is a string.
        '''
        return x or ''


class AccountSpec(ColSpec):
    '''
    A column that displays an abbreviated account name
    '''

    def render(self, rec, x) -> str:
        '''
        Convert a date to a string
        '''
        return DB.abbrev(rec[x])

class DateSpec(ColSpec):
    '''
    A column for displaying dates.
    '''

    def render(self, rec, x) -> str:
        '''
        Convert a date to a string
        '''
        return str(rec[x])

    def value(self, x:str):
        '''
        Parse a date string, return a date object.
        '''
        return parse_date(x)

class FlagSpec(ColSpec):
    '''
    Special purpose column for entry tables, displays a red dot if the
    tags field includes an 'unpaired' tag.
    '''

    def __init__(self, name:str, width:int) -> None:
        '''
        Initialize a new object.

        Arguments:
            name:  the column name
            width:  column width
        '''
        self._name = name
        self._width = width
        self._attr = None

    def render(self, rec, _):
        return '🔴' if Tag.U.value in rec.tags else ' '

class ListSpec(ColSpec):
    '''
    A column for displaying tags (lists of strings).
    '''

    SEP = ', '

    def render(self, rec, x) -> str:
        '''
        Make a string with each tag
        '''
        return self.SEP.join(rec[x])

    def value(self, x:str):
        '''
        Turn a string back into a list
        '''
        return x.split(self.SEP)

class SignedAmountSpec(ColSpec):
    '''
    A column for displaying amounts, highlighting negative amunts.  Make a 
    string showing the amount value, wrap it in a Rich Text 
    object so it can be right-justified.
    '''

    def render(self, rec, x) -> str:
        '''
        Convert an amount to a string
        '''   
        amount = rec[x]
        style = ''
        if rec.column == DBColumn.cr:
            amount = -amount
            style = 'red'
        # s = format_amount(amount, dollar_sign=True, accounting=True)
        s = format_amount(amount, dollar_sign=True)
        return Text(s, justify='right', style=style)

    def value(self, x:str):
        '''
        An amount is stored in the table as a Text object.  Convert it 
        back into a float after stripping away the dollar sign and commas.
        '''
        s = x.plain
        return float(s.replace('$','').replace(',',''))
 
class UnsignedAmountSpec(ColSpec):
    '''
    A column for displaying amounts.  Make a string showing the amount
    value (formatted with dollar sign and commas), wrap it in a Rich Text 
    object so it can be right-justified.
    '''

    def render(self, rec, x) -> str:
        '''
        Convert an amount to a string
        '''
        s = format_amount(rec[x], dollar_sign=True)
        return Text(s, justify='right')

    def value(self, x:str):
        '''
        An amount is stored in the table as a Text object.  Convert it 
        back into a float after stripping away the dollar sign and commas.
        '''
        s = x.plain
        return float(s.replace('$','').replace(',',''))
    
entry_columns = [
    ColSpec('UID', 0, 'uid'),
    FlagSpec(' ', 3),
    DateSpec('Date', 10, 'date'),
    ColSpec('Account', 30, 'account'),
    SignedAmountSpec('Amount', 12, 'amount'),
    ColSpec('Description', 40, 'description'),
    ListSpec('Tags', 30, 'tags'),
]

transaction_columns = [
    # ColSpec('UID', 0, 'uid'),
    DateSpec('Date', 10, 'pdate'),
    AccountSpec('Credit', 15, 'pcredit'),
    AccountSpec('Debit', 15, 'pdebit'),
    UnsignedAmountSpec('Amount', 12, 'pamount'),
    ColSpec('Description', 40, 'description'),
    ColSpec('Comment', 30, 'comment'),
    ListSpec('Tags', 30, 'tags'),
]
    
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
        self.row_keys = []
        self.reversed = {}
        self.colspec = {}

    def add_records(self, records, args):
        self.records = records
        headers = entry_columns if args.entry else transaction_columns
        for spec in headers:
            self.add_column(spec.name, width=spec.width, key=spec.name)
            self.reversed[spec.name] = False
            self.colspec[spec.name] = spec
        for i, rec in enumerate(records):
            row = []
            for spec in headers:
                row.append(spec.render(rec, spec.attr))
            self.row_keys.append(self.add_row(*row))
        self.log(f'added {len(records)} rows to table')

    def on_data_table_header_selected(self, msg):
        col = msg.column_key
        self.sort(col, key=lambda c: self.colspec[col].value(c), reverse=self.reversed[col])
        self.reversed[col] = not self.reversed[col]

    def action_open_editor(self) -> None:
        obj = self.records[self.cursor_row]
        if isinstance(obj, Entry):
            if Tag.U.value in obj.tags:
                rec = make_candidate(obj, [])
                rec.pdate = rec.entries[0].date
                rec.description = apply_regexp(rec.entries[0].description)
            elif obj.tref:
                rec = obj.tref
            else:
                raise ValueError(f'TransactionTable: badly formed entry: {obj}')
        else:
            rec = obj
        cb = self.update_transaction
        self.post_message(self.OpenModal(rec, cb))

    def update_transaction(self, resp: bool) -> None:
        # col = 'Description'
        # new_content = 'Yay!'
        # rec = self.records[self.cursor_row]
        # spec = self.colspec[col]
        # val = self.colspec[col].render(rec, new_content)
        # self.update_cell(self.row_keys[self.cursor_row], col, val)
        pass

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
