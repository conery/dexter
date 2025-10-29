#
# TUI (Terminal User Interface) implemented with Textual
#

from rich.text import Text

from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import Footer, Header, Log, DataTable, Input, Tree

from .console import format_amount
from .DB import DB, Tag, Column as DBColumn
from .util import debugging

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

# Main app calls this method to launch the GUI

def start_gui(recs, args):
    '''
    Create the Textual app and start it
    '''
    app = TUI(recs, args)
    app.run()


class TUI(App):
    '''
    A Textual app for displaying and editing Dexter objects.
    '''

    def __init__(self, recs, args) -> None:
        '''
        Constructor for the top level app.

        Arguments:
            recs:  list of objects to display in the table
            args:  command line arguments
        '''
        self.records = recs
        self.args = args
        super().__init__()

    CSS_PATH = "dex.tcss"

    def compose(self) -> ComposeResult:
        '''
        Lay out the top level window with a header, footer, and content
        area
        '''
        header = Header()
        header.tall = True

        self.table = DataTable()
        self.table.cursor_type = 'row'
        self.table.cell_padding = 2
        self.table.header_height = 2

        yield header
        yield self.table
        yield Footer()

        if debugging():
            yield Log()

    def on_mount(self):
        self.title = '\nDexter'
        self.sub_title = 'Double Entry Expense Tracker'
        self.fill_table()

    def add_message(self, message):
        if debugging():
            w = self.query_one(Log)
            w.write_line(message)

    def fill_table(self):
        headers = entry_columns if self.args.entry else transaction_columns
        for spec in headers:
            self.table.add_column(spec[0], width=spec[1])
        for rec in self.records:
            row = []
            for spec in headers:
                row.append(spec[2](rec, spec[3]))
            self.table.add_row(*row)
            # self.add_message(f'{rec["date"]}')
