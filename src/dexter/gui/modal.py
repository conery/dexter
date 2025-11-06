#
# TUI widget for the modal window that displays a single transaction
#

from datetime import date

from rich.text import Text

from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.content import Content
from textual.containers import HorizontalGroup, VerticalGroup, VerticalScroll, Center, Right
from textual.screen import ModalScreen
from textual.widgets import Button, Label, TextArea, Static

from dexter.console import format_amount
from dexter.DB import DB, Tag, Transaction, Column as DBColumn

from dexter.gui.account import Accounts

class Amount(Label):
    '''
    A label for displaying a dollar amount.
    '''
   
    def __init__(self, a:float) -> None:
        super().__init__(format_amount(a, dollar_sign=True))

class ConstText(Label):
    '''
    A widget to display uneditable text.  Truncates the text to fit
    the width of the widget.
    '''

    def __init__(self, text: str, id: str) -> None:
        super().__init__(text, id=id)

    def on_show(self, event):
        '''
        Figure out how wide the widget is, truncate the text to fit.
        '''
        if len(self.content) > self.content_size.width:
            s = self.content[:self.content_size.width-2] + '…'
            self.content = Content(s)
        return super()._on_show(event)

class Date(Label):
    '''
    A label to display a date.
    '''
   
    def __init__(self, d:date) -> None:
        super().__init__(str(d))

class TextLine(TextArea):
    '''
    A widget that displays editable text, limited to a single line (it
    captures and ignores enter keys).  When the text is empty the placeholder
    is displayed, highlighted by a different style.
    '''

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

    # def on_mount(self):
    #     self.action_cursor_line_end()
    #     return super().on_mount()

    
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
        self.description = ConstText(self.rec.description, id='entry_description')
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
        self.account = Accounts(id='account_selection')
        self.amount = Amount(self.rec.amount)
        self.description = ConstText(self.rec.description, id='entry_description')
        yield self.unpaired
        yield self.date
        yield self.account
        yield self.amount
        yield self.description

    def on_show(self, event):
        self.description.focus()
        self.account.add_class('collapsed')
        return super()._on_show(event)
    
class ModalButton(Button):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.can_focus = False

class TransactionGroup(VerticalGroup):

    def __init__(self, rec):
        self.rec = rec
        super().__init__()

    def compose(self) -> ComposeResult:
        with VerticalGroup():
            yield THeader(self.rec)
            yield FixedEntry(self.rec.entries[0])
            yield Entry(self.rec.entries[1])
            yield Static('', id='message')
        with Center():
            with HorizontalGroup(id='button_group'):
                yield ModalButton('Cancel (⌃C)', id='cancel', variant='warning')
                yield ModalButton('Save (⌃S)', id='save', variant='success')


class TransactionScreen(ModalScreen):
    '''
    A modal dialog for editing a single transaction, which is displayed in Journal
    format (top line for transaction data, lines indented below that for each
    entry).
    '''

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

    def check_required_fields(self):
        errs = []
        account_widget = self.query_one(Accounts)
        if not account_widget.selection:
            errs.append(f'No account selected')
        header_widget = self.query_one(THeader)
        if len(header_widget.description.text) == 0:
            errs.append('Empty transaction description')
        return ', '.join(errs)

    def action_save_exit(self):
        if msg := self.check_required_fields():
            message_widget = self.query_one('#message')
            message_widget.content = Content(msg)
            return False
        res = {}
        for id in ['description', 'comment', 'tags']:
            widget = self.query_one(f'#{id}')
            if s := widget.text:
                res[id] = s
        tree = self.query_one(Accounts)
        res['account'] = tree.selection
        self.dismiss(res)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'cancel':
            self.action_cancel_exit()
        else:
            self.action_save_exit()

    def on_accounts_log_message(self, msg: Accounts.LogMessage) -> None:
        message_widget = self.query_one('#message')
        message_widget.content = Content(msg.text)
