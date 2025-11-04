#
# TUI widget for displaying tables of transactions
#

import re

from rich.text import Text

from textual.app import App
from textual.binding import Binding
from textual.message import Message
from textual.widgets import DataTable

from dexter.console import format_amount
from dexter.DB import DB, Transaction, Entry, Tag, Column as DBColumn
from dexter.repl import make_candidate, apply_regexp
from dexter.util import parse_date

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

class MarkerSpec(ColSpec):
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

    @property
    def key(self):
        return 'marker'
        
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
    MarkerSpec(' ', 3),
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
            self.add_column(spec.name, width=spec.width, key=spec.key)
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
                self.mode = 'unpaired'
            elif obj.tref:
                rec = obj.tref
                self.mode = 'entry'
            else:
                raise ValueError(f'TransactionTable: badly formed entry: {obj}')
        else:
            rec = obj
            self.mode = 'transaction'
        self.log(f'edit mode {self.mode}')
        self.editing = rec
        cb = self.update_transaction
        self.post_message(self.OpenModal(rec, cb))

    def update_transaction(self, resp: dict) -> None:
        self.log(f'response: {resp}')
        if resp is not None:
            self.update_DB_transaction(resp)
            self.update_table_row(resp)

        # col = 'Description'
        # new_content = 'Yay!'
        # rec = self.records[self.cursor_row]
        # spec = self.colspec[col]
        # val = self.colspec[col].render(rec, new_content)
        # self.update_cell(self.row_keys[self.cursor_row], col, val)

    def update_DB_transaction(self, resp) -> None:
        obj = self.editing
        obj.entries[1].account = resp['account']
        obj.description = resp['description']
        obj.comment = resp.get('comment')
        if tag_string := resp.get('tags'):
            obj.tags = [s if s.startswith('#') else f'#{s}' for s in re.split(r'[\s,]+', tag_string)]
        obj.entries[0].tags.remove(Tag.U.value)
        DB.save_records([obj])

    def update_table_row(self, resp) -> None:
        i = self.row_keys[self.cursor_row]
        if self.mode == 'unpaired':
            self.update_cell(i, 'marker', ' ')
            if self.cursor_row < len(self.records):
                self.move_cursor(row = self.cursor_row + 1)

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
