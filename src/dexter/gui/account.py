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
        self.auto_expand = True
        accts = fetch_names(categories)
        path = [self.root]
        self.fullname = {}
        # self.nodes = {}
        for i, a in enumerate(accts):
            interior = (i < len(accts)-1) and accts[i+1].startswith(a)
            parts = a.split(':')
            label = parts[-1]
            if DB.fullname(a):
                self.fullname[label] = a
            if interior:
                n = len(parts)
                if n == len(path):
                    node = path[-1].add(label)
                    path.append(node)
                else:
                    parent = path[n-1]
                    node = parent.add(label)
                    path[n] = node
            else:
                node = path[len(parts)-1].add_leaf(label)
            # self.nodes[label] = node

    @property
    def selection(self):
        '''
        If the current node corresponds to a full account name return that
        name, otherwise return None
        '''
        name = str(self.cursor_node.label)
        return self.fullname.get(name)

    def on_tree_node_selected(self, event):
        pass

    def action_show_selection(self):
        # log(f'on line {self.cursor_line} {self.cursor_node.label}')
        pass
