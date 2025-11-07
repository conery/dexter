#
# TUI widget for displaying account names in a tree
#

from textual import events
from textual.message import Message
from textual.widgets import Tree

from pygtrie import CharTrie

from dexter.DB import DB, Category

def fetch_names(categories: list[str]) -> list[str]:
    '''
    Get a list of account names from the database.  For each category
    include the name of the category (e.g. 'expenses') followed by all the
    account names in that category (e.g. 'expenses:car', 'expenses:car:fuel', ...)

    Arguments:
        categories:  a list of Category objects

    Returns:
        a list of account names
    '''
    res =  []
    for cat in categories:
        res.append(cat.value)
        res += [a.name for a in DB.find_account(cat.value)]
    return res

class Completer:
    '''
    Manage keystrokes typed when account widget is active
    '''

    def __init__(self):
        self.buffer = []
        self.trie = CharTrie()
        self.name_chars = set()
        self.ring = []
        self.ring_index = None

    @property
    def token(self):
        return ''.join(self.buffer)

    def add_name(self, acct, row):
        lst = self.trie.setdefault(acct.lower(), [])
        lst.append(row)
        self.name_chars |= { ch.lower() for ch in acct }

    def process_keystroke(self, key):
        if key == 'escape' and self.ring:
            self.ring_index = (self.ring_index+1) % len(self.ring)
        else:
            if key.lower() in self.name_chars:
                self.buffer.append(key.lower())
            elif key == 'backspace' and len(self.buffer):
                self.buffer.pop()
            t = self.token
            if t and self.trie.has_node(t):
                self.ring = sorted(sum(self.trie[t:], []))
                self.ring_index = 0
            else:
                self.ring = []
        return key == 'backspace' or key == 'escape' or key in self.name_chars

    def selected(self):
        if self.ring:
            return self.ring[self.ring_index]
        else:
            return 0

class Accounts(Tree):
    '''
    Display list widgets
    '''

    def __init__(self, id='', root='category', categories=[Category.E, Category.I]) -> None:
        '''
        Create a tree widget populated by names of accounts.
        '''
        super().__init__(root, id=id)
        self.root_name = root
        self.auto_expand = True
        self.prev_line = None
        accts = fetch_names(categories)
        path = [self.root]
        self.fullname = []
        self.account_row = {}
        self.completer = Completer()
        for i, a in enumerate(accts):
            interior = (i < len(accts)-1) and accts[i+1].startswith(a)
            parts = a.split(':')
            label = parts[-1]
            self.fullname.append(a)
            self.account_row[a] = i+1
            self.completer.add_name(label, i)
            if interior:
                n = len(parts)
                if n == len(path):
                    node = path[-1].add(label,i)
                    path.append(node)
                else:
                    parent = path[n-1]
                    node = parent.add(label,i)
                    path[n] = node
            else:
                node = path[len(parts)-1].add_leaf(label,i)

    @property
    def selection(self):
        '''
        If the current node corresponds to a full account name return that
        name, otherwise return None
        '''
        # name = str(self.cursor_node.label)
        # return self.fullname.get(name)
        if isinstance(self.cursor_node.data, int):
            acct = self.fullname[self.cursor_node.data]
        elif self.root.label != self.root_name:
            acct = str(self.root.label)
        else:
            acct = None
        return acct
        
        
    def set_selection(self, account):
        # self.root.expand_all()
        # self.move_cursor_to_line(self.account_row[account])
        self.root.label = account
        self.prev_line = self.account_row[account]
        self.move_cursor_to_line(0)

    def on_blur(self, event) -> None:
        self.add_class('collapsed')
        if isinstance(self.cursor_node.data, int):
            self.root.label = self.fullname[self.cursor_node.data]
            self.prev_line = self.cursor_line
            self.move_cursor_to_line(0)
        if self.completer.token:
            self.post_message(self.LogMessage(f'hide'))

    def on_focus(self, event) -> None:
        self.remove_class('collapsed')
        if self.completer.token:
            self.post_message(self.LogMessage(f'reveal'))
        self.root.label = self.root_name
        if self.prev_line:
            self.root.expand_all()
            self.move_cursor_to_line(self.prev_line)

    def on_key(self, event: events.Key) -> None:
        # if event.character == '\r':
        #     self.screen.focus_next()
        if self.completer.process_keystroke(event.key):
            # self.post_message(self.LogMessage(f'{event.key} {self.completer.token} {self.completer.ring} {self.completer.ring_index}'))
            self.post_message(self.LogMessage(f'> {self.completer.token}'))
            if next := self.completer.selected():
                self.root.expand_all()
                self.move_cursor_to_line(next+1)
            else:
                self.root.collapse_all()
            # event.prevent_default()

    class LogMessage(Message):

        def __init__(self, msg: str) -> None:
            self.text = msg
            super().__init__()
