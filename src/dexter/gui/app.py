#
# TUI (Terminal User Interface) implemented with Textual
#

from rich.text import Text

from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Footer, Header, Log, DataTable, Input, Tree, Button

from dexter.console import format_amount
from dexter.DB import DB, Tag, Column as DBColumn
from dexter.util import debugging

from .table import TransactionTable
from .modal import TransactionScreen

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

        self.table = TransactionTable()

        yield header
        yield self.table
        yield Footer()

        if debugging():
            yield Log()

    def on_mount(self):
        self.title = '\nDexter'
        self.sub_title = 'Double Entry Expense Tracker'
        self.table.add_records(self.records, self.args)

    def add_message(self, message):
        if debugging():
            self.query_one(Log).write_line(message)

    def on_transaction_table_log_message(self, msg: TransactionTable.LogMessage) -> None:
        self.add_message(msg.text)

    def on_transaction_table_open_modal(self, msg: TransactionTable.OpenModal) -> None:
        self.push_screen(TransactionScreen(msg.rec), msg.cb)

# Main app calls this method to launch the GUI

def start_gui(recs, args):
    '''
    Create the Textual app and start it
    '''
    app = TUI(recs, args)
    app.run()

