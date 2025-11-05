#
# TUI widget for displaying account names in a tree
#

from textual.binding import Binding
from textual.widgets import Tree

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
        for i, a in enumerate(accts):
            interior = (i < len(accts)-1) and accts[i+1].startswith(a)
            parts = a.split(':')
            label = parts[-1]
            self.fullname.append(a)
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
        name = str(self.cursor_node.label)
        return self.fullname.get(name)

    def on_blur(self, event):
        self.add_class('collapsed')
        if isinstance(self.cursor_node.data, int):
            self.root.label = self.fullname[self.cursor_node.data]
            self.prev_line = self.cursor_line
            self.move_cursor_to_line(0)

    def on_focus(self, event):
        self.remove_class('collapsed')
        self.root.label = self.root_name
        if self.prev_line:
            self.move_cursor_to_line(self.prev_line)
