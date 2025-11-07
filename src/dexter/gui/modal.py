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
from dexter.DB import DB, Tag, Transaction, Column as DBColumn, Category

from dexter.gui.account import Accounts

class Amount(Label):
    '''
    A label for displaying a dollar amount.
    '''
   
    def __init__(self, a:float, col:DBColumn) -> None:
        if col == DBColumn.cr:
            a = -a
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

    def __init__(self, rec:Transaction, field:str, text=None) -> None:
        super().__init__()
        self.rec = rec
        self.id = field
        self.placeholder = field
        self.text = text or rec[field] or ''
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
        text = ' ,'.join(rec.tags) if rec.tags else ''
        super().__init__(rec, 'tags', text)

class THeader(HorizontalGroup):

    def __init__(self, rec):
        self.rec = rec
        super().__init__()

    def compose(self) -> ComposeResult:
        self.date = Date(self.rec.pdate)
        self.description = TextLine(self.rec, 'description')
        self.comment = TextLine(self.rec, 'comment')
        self.tags = TagLine(self.rec)

        self.original_description = self.description.text
        self.original_comment = self.comment.text
        self.original_tags = self.tags.text

        yield(self.date)
        yield(self.description)
        yield(self.comment)
        yield(self.tags)

class FixedEntry(HorizontalGroup):

    def __init__(self, rec):
        self.rec = rec
        super().__init__()

    def compose(self) -> ComposeResult:
        marker = '🚩' if Tag.U.value in self.rec.tags else ' '
        self.unpaired = Label(marker, id='marker')
        self.date = Date(self.rec.date)
        self.account = ConstText(self.rec.account, id='account')
        self.amount = Amount(self.rec.amount, self.rec.column)
        self.description = ConstText(self.rec.description, id='entry_description')
        yield self.unpaired
        yield self.date
        yield self.account
        yield self.amount
        yield self.description

class Entry(HorizontalGroup):

    def __init__(self, rec):
        self.rec = rec
        self.initial_account = None
        super().__init__()

    def compose(self) -> ComposeResult:
        marker = '🔹' if self.rec.column == DBColumn.cr else ''
        self.unpaired = Label(marker, id='marker')
        self.date = Date(self.rec.date)
        self.amount = Amount(self.rec.amount, self.rec.column)
        self.description = ConstText(self.rec.description, id='entry_description')

        if acct := self.rec.account:
            if acct.startswith((Category.A.value, Category.L.value)):
                self.account = ConstText(self.rec.account, id='fixed_account')
            else:
                self.account = Accounts(id='account_selection')
                self.account.set_selection(acct)
                self.initial_account = acct
        else:
            self.account = Accounts(id='account_selection')

        yield self.unpaired
        yield self.date
        yield self.account
        yield self.amount
        yield self.description

    def on_show(self, event):
        if self.account.id == 'account_selection':
            self.account.add_class('collapsed')
        self.description.focus()
        return super()._on_show(event)
    
    def account_changed(self):
        acct = self.account.selection
        return acct != self.initial_account and acct
    
class ModalButton(Button):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.can_focus = False

class ButtonGroup(HorizontalGroup):

    def compose(self) -> ComposeResult:
        yield ModalButton('Cancel (⌃C)', id='cancel', variant='warning')
        yield ModalButton('Save (⌃S)', id='save', variant='success')

class TransactionGroup(VerticalGroup):

    def __init__(self, rec):
        self.rec = rec
        super().__init__()

    def compose(self) -> ComposeResult:
        yield THeader(self.rec)
        yield FixedEntry(self.rec.entries[0])
        yield Entry(self.rec.entries[1])
        yield Static('', id='message')

class TransactionPanel(VerticalGroup):

    def __init__(self, rec):
        self.rec = rec
        super().__init__()

    def compose(self) -> ComposeResult:
        yield TransactionGroup(self.rec)
        with Center():
            yield ButtonGroup()

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
        yield TransactionPanel(self.rec)

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
        # TODO:  🤢 rewrite, passing name of field to method in THeader class
        widget = self.query_one(THeader)
        if widget.description.text != widget.original_description:
            res['description'] = widget.description.text
        if widget.comment.text != widget.original_comment:
            res['comment'] = widget.comment.text
        if widget.tags.text != widget.original_tags:
            res['tags'] = widget.tags.text
        widget = self.query_one(Entry)
        if acct := widget.account_changed():
            res['account'] = acct
        self.dismiss(res)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'cancel':
            self.action_cancel_exit()
        else:
            self.action_save_exit()

    def on_accounts_log_message(self, msg: Accounts.LogMessage) -> None:
        message_widget = self.query_one('#message')
        if msg.text == 'hide':
            message_widget.visible = False
        elif msg.text == 'reveal':
            message_widget.visible = True
        else:
            message_widget.content = Content(msg.text)
