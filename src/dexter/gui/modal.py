#
# TUI widget for the modal window that displays a single transaction
#

from datetime import date

from rich.text import Text

from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.content import Content
from textual.containers import HorizontalGroup, VerticalScroll, Center, Right
from textual.screen import ModalScreen
from textual.widgets import Button, Label, TextArea, Static

from dexter.console import format_amount
from dexter.DB import DB, Tag, Transaction, Column as DBColumn

from dexter.gui.account import Accounts

class Amount(Label):
   
    def __init__(self, a:float) -> None:
        super().__init__(format_amount(a, dollar_sign=True))

class ConstText(Label):

    def __init__(self, text: str, id: str) -> None:
        super().__init__(text, id=id)

    def on_show(self, event):
        if len(self.content) > self.content_size.width:
            s = self.content[:self.content_size.width-2] + '…'
            self.content = Content(s)
        return super()._on_show(event)

class Date(Label):
   
    def __init__(self, d:date) -> None:
        super().__init__(str(d))

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

class FixedEntry(HorizontalGroup):

    def __init__(self, rec):
        self.rec = rec
        super().__init__()

    def compose(self) -> ComposeResult:
        marker = '🔴' if Tag.U.value in self.rec.tags else ' '
        self.unpaired = Label(marker, id='unpaired')
        self.date = Date(self.rec.date)
        self.account = ConstText(self.rec.account, id='account')
        self.amount = Amount(self.rec.amount)
        self.description = ConstText(self.rec.description, id='description')
        yield self.unpaired
        yield self.date
        yield self.account
        yield self.amount
        yield self.description

class Entry(HorizontalGroup):

    def __init__(self, rec):
        self.rec = rec
        super().__init__()

    def compose(self) -> ComposeResult:
        self.unpaired = Label(' ', id='unpaired')
        self.date = Date(self.rec.date)
        self.account = Accounts()
        self.amount = Amount(self.rec.amount)
        self.description = ConstText(self.rec.description, id='description')
        yield self.unpaired
        yield self.date
        yield self.account
        yield self.amount
        yield self.description

    def on_show(self, event):
        self.account.focus()
        return super()._on_show(event)
    
class ModalButton(Button):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.can_focus = False

class TransactionGroup(VerticalScroll):

    def __init__(self, rec):
        self.rec = rec
        super().__init__()

    def compose(self) -> ComposeResult:
        yield THeader(self.rec)
        yield FixedEntry(self.rec.entries[0])
        yield Entry(self.rec.entries[1])
        yield Static('', id='message')
        with Center():
            with HorizontalGroup(id='button_group'):
                yield ModalButton('Cancel (⌃C)', id='cancel', variant='warning')
                yield ModalButton('Save (⌃S)', id='save', variant='success')


class TransactionScreen(ModalScreen):

    BINDINGS = [
        Binding('ctrl+c', 'cancel_exit'),
        Binding('ctrl+s', 'save_exit'),
    ]

    def __init__(self, rec):
        self.rec = rec
        self.event = None
        super().__init__()

    def compose(self) -> ComposeResult:
        yield TransactionGroup(self.rec)

    def action_cancel_exit(self):
        self.dismiss(None)

    def action_save_exit(self):
        self.dismiss({'account': 'expenses:car:fuel', 'description': 'Fuel!'})

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'cancel':
            self.action_cancel_exit()
        else:
            self.action_save_exit()

