#
# TUI widget for the modal window that displays a single transaction
#

from rich.text import Text

from textual.app import ComposeResult
from textual.widgets import ModalScreen, Button

from dexter.console import format_amount
from dexter.DB import DB, Tag, Column as DBColumn

class TransactionScreen(ModalScreen):

    def compose(self) -> ComposeResult:
        yield Button('Aloha!')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(True)

