#
# TUI widget for the modal window that displays a single transaction
#

from datetime import date
import re

from rich.text import Text

from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.content import Content
from textual.containers import HorizontalGroup, VerticalGroup, VerticalScroll, Center, Right
from textual.screen import ModalScreen
from textual.widgets import Button, Label, TextArea, Static

from dexter.console import format_amount
from dexter.DB import DB, Tag, Transaction, Entry as DBEntry, Column as DBColumn, Category

from dexter.gui.account import Accounts

class ConstText(Label):
    '''
    A widget to display uneditable text.  Truncates the text to fit
    the width of the widget.
    '''

    def __init__(self, text: str) -> None:
        super().__init__(text)

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
        self.add_class('text_line')

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

class Amount(TextLine):
    '''
    A text area for displaying a dollar amount.
    '''
   
    # def __init__(self, a:float, col:DBColumn) -> None:
    def __init__(self, rec:DBEntry) -> None:
        self.entry = rec
        amount = rec.amount
        if rec.column == DBColumn.cr:
            amount = -amount
        super().__init__(None, 'amount', text=format_amount(amount, dollar_sign=True))
        self.prev = self.text
        self.edited = False

    def on_blur(self):
        if self.text != self.prev:
            self.add_class('flagged')
            group = self.screen.query_one(TransactionGroup)
            if group.add_split(self.text, self.entry):
                self.prev = self.text
                self.edited = True
            else:
                self.screen.set_focus(self)
            # e = self.trans.entries[-1]
            # e.description = 'cloned'
            # self.trans.entries.append(e)
            # self.screen.refresh(repaint=True, layout=True, recompose=True)
        else:
            self.remove_class('flagged')

    def on_key(self, event: events.Key) -> None:
        if event.character == '\r':
            event.prevent_default()
            self.blur()
            # group = self.screen.query_one(TransactionGroup)
            # i = len(group.entries)
            # group.mount(Entry(self.rec, i))

    # def on_key(self, event: events.Key) -> None:
    #     if len(self.text) == 0:
    #         self.add_class('placeholder')
    #     else:
    #         self.remove_class('placeholder')

    #     if event.character == '\r':
    #         event.prevent_default()


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

        self.original = {
            'description': self.description.text,
            'comment': self.comment.text,
            'tags': self.tags.text,
        }

        yield(self.date)
        yield(self.description)
        yield(self.comment)
        yield(self.tags)

    def check_required(self):
        errs = []
        if len(self.description.text) == 0:
            errs.append('Header: empty transaction description')
        return errs
    
    def edited_fields(self):
        res = {}
        for field in ['description', 'comment', 'tags']:
            if getattr(self,field).text != self.original[field]:
                res[field] = getattr(self,field).text
        return res

class Entry(HorizontalGroup):

    def __init__(self, rec:DBEntry, index:int) -> None:
        self.rec = rec
        self.index = index
        self.initial_account = None
        super().__init__()

    def compose(self) -> ComposeResult:
        # marker = '🔹' if self.rec.column == DBColumn.cr else ''
        # self.unpaired = Label(marker, id='marker')
        self.date = Date(self.rec.date)
        # self.amount = Amount(self.rec.amount, self.rec.column)
        self.amount = Amount(self.rec)
        self.description = ConstText(self.rec.description)
        self.description.add_class('entry_description')

        if acct := self.rec.account:
            if acct.startswith((Category.A.value, Category.L.value)):
                self.account = ConstText(self.rec.account)
                self.account.add_class('static_account')
                self.amount.disabled = True
            else:
                self.account = Accounts(id='account_selection')
                self.account.set_selection(acct)
                self.initial_account = acct
        else:
            self.account = Accounts(id='account_selection')
            self.initial_account = ''

        # yield self.unpaired
        yield Label(' ', id='hspace')
        yield self.date
        yield self.account
        yield self.amount
        yield self.description

    def check_required(self):
        errs = []
        if isinstance(self.account, Accounts) and not self.account.selection:
            errs.append(f'Entry #{self.index}: no account selected')
        return errs
    
    def edited_fields(self):
        lst = []
        if isinstance(self.account, Accounts) and self.account.selection != self.initial_account:
            lst.append(('account',self.account.selection))
        return lst

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
        self.header = THeader(self.rec)
        self.entries = [Entry(e,i) for i,e in enumerate(self.rec.entries)]

        yield self.header
        with VerticalScroll():
            for w in self.entries:
                yield w

    def check_required(self):
        errs = self.header.check_required()
        for w in self.entries:
            errs += w.check_required()
        return '; '.join(errs)
    
    def edited_fields(self):
        dct = self.header.edited_fields()
        for i, e in enumerate(self.entries):
            if lst := e.edited_fields():
                dct[i] = lst
        return dct
    
    def add_split(self, astring, entry):
        message_widget = self.screen.query_one('#message')
        try:
            amount = float(re.sub(r'[,$]','',astring))
            if amount >= entry.amount or amount < 0:
                raise ValueError(f'illegal amount: {astring}')
        except ValueError as err:
            message_widget.content = Content(str(err))
            return False
        diff = round(entry.amount-amount,2)
        e = DBEntry(
            date = entry.date,
            description = f'split @{entry.uid[:8]}',
            account = None,
            column = entry.column,
            amount = diff
        )
        w = Entry(e, len(self.entries))
        self.entries.append(w)
        self.mount(w)
        message_widget.content = Content(f'split {diff} {entry}')
        message_widget.add_class('flagged')
        return True

class TransactionPanel(VerticalGroup):

    def __init__(self, rec):
        self.rec = rec
        super().__init__()

    def compose(self) -> ComposeResult:
        yield TransactionGroup(self.rec)
        yield Static('', id='message')
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
        # self.event = None
        super().__init__()

    def compose(self) -> ComposeResult:
        yield TransactionPanel(self.rec)
        yield Label(f'rec with {len(self.rec.entries)} entries')

    def action_cancel_exit(self):
        self.dismiss(None)

    def action_save_exit(self):
        group = self.query_one(TransactionGroup)
        if msg := group.check_required():
            message_widget = self.query_one('#message')
            message_widget.content = Content(msg)
            return False
        res = group.edited_fields()

        # *** Uncomment these three lines to show the res dictionary in the message area ***
        # message_widget = self.query_one('#message')
        # message_widget.content = Content(str(res))
        # return False
        
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
