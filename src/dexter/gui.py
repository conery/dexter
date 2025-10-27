#
# TUI (Terminal User Interface) implemented with Textual
#

from textual import log
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import Footer, Header, Input, Tree

# Main app calls this method to launch the GUI

def start_gui(recs, args):
    '''
    Create the Textual app and start it
    '''
    app = TUI()
    app.run()


class TUI(App):
    '''
    A Textual app for displaying and editing Dexter objects.
    '''

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

    def on_mount(self):
        self.title = '\nDexter'
        self.sub_title = 'Double Entry Expense Tracker'



