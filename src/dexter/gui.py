#
# TUI (Terminal User Interface) implemented with Textual
#

# from textual import log
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import Footer, Header, Log, Input, Tree

from .util import debugging

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

        yield header
        yield Footer()

        if debugging():
            yield Log()

    def add_message(self, message):
        if debugging():
            w = self.query_one(Log)
            w.write_line(message)

    def on_mount(self):
        self.title = '\nDexter'
        self.sub_title = 'Double Entry Expense Tracker'

    def on_ready(self):
        self.add_message(f'display {len(self.records)} records')
