#
# TUI widget for the modal window that displays a single transaction
#
from datetime import date

from rich.text import Text

from textual import events
from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, TextArea

from dexter.console import format_amount
from dexter.DB import DB, Tag, Transaction, Column as DBColumn

class Date(TextArea):
   
    def __init__(self, d:date) -> None:
        self.date = str(d)
        super().__init__()
        self.text = self.date
        self.disabled = True

    def allow_focus(self):
        super().allow_focus()
        return False

    # def on_mount(self):
    #     self.disabled = True

class TextLine(TextArea):

    def __init__(self, rec:Transaction, field:str) -> None:
        super().__init__()
        self.rec = rec
        self.id = field
        self.placeholder = field
        self.text = rec[field] if rec[field] else ''
        if len(self.text) == 0:
            self.add_class('placeholder')

    def on_key(self, event: events.Key) -> None:
        if len(self.text) == 0:
            self.add_class('placeholder')
        else:
            self.remove_class('placeholder')

        if event.character == '\r':
            event.prevent_default()

    def on_mount(self):
        self.action_cursor_line_end()
        return super().on_mount()
    
class TagLine(TextLine):

    def __init__(self, rec:Transaction):
        super().__init__(rec, 'tags')
        self.text = ' ,'.join(rec.tags) if rec.tags else ''

class THeader(HorizontalGroup):

    def __init__(self, rec):
        self.rec = rec
        super().__init__()

    def compose(self) -> ComposeResult:
        self.date = Date(self.rec.pdate)
        self.description = TextLine(self.rec, 'description')
        self.comment = TextLine(self.rec, 'comment')
        self.tags = TagLine(self.rec)

        yield(self.date)
        yield(self.description)
        yield(self.comment)
        yield(self.tags)

class TransactionGroup(VerticalScroll):

    def __init__(self, rec):
        self.rec = rec
        super().__init__()

    def compose(self) -> ComposeResult:
        yield THeader(self.rec)
        yield Button('Aloha!')


class TransactionScreen(ModalScreen):

    def __init__(self, rec):
        self.rec = rec
        super().__init__()

    def compose(self) -> ComposeResult:
        yield TransactionGroup(self.rec)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(True)

