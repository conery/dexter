###
# 
# Subset sum algorithm -- used to find a set of card purchase transactions with 
# amounts that sum to the amount in a card payment transaction. The algorithm
# is a branch-and-bound search of a binary tree where each node is a BBNode object.  
#

class BBNode:
    
    items = []
    target = 0
    template = '⟦level {:d} members {:b} sum {} potential {}⟧'
    N = 0
    
    count = 0
    
    def __init__(self, level = -1, members = 0, csum = 0, psum = None, skipped = 0):
        BBNode.count += 1
        self._level = level
        self._members = members
        self._csum = csum
        self._psum = psum or sum(BBNode.items)
        self._skipped = skipped
        
    def __repr__(self):
        return BBNode.template.format(self._level, self._members, self._csum, self._psum) # + str(self.members())
    
    def __lt__(self, other):
        "define node priority as distance from target -- raises an exception it target not set"
        return (self._skipped/(10000*self._level+1) < other._skipped/(10000*other._level+1))

    def level(self):
        return self._level

    def potential_solution(self):
        return (self._csum <= BBNode.target) and (self._psum >= BBNode.target)

    def members(self):
        return { i for i in range(len(BBNode.items)) if self._members & 1 << i }
    
    def is_solution(self):
        return self._csum == BBNode.target
    
    def expand(self):
        self._level += 1
        if self._level == len(BBNode.items):
            return None
        delta = BBNode.items[self._level]
        succ = BBNode(self._level, (self._members | (1 << self._level)), self._csum + delta, self._psum, self._skipped )
        self._psum -= delta
        self._skipped += 1
        return succ
    
    @staticmethod
    def set_items(lst):
        BBNode.items = lst
        BBNode.N = len(lst)

    @staticmethod
    def set_target(n):
        BBNode.target = n
        
import heapq


def find_subset(ints, target):
    '''
    Find a subset of a list of integers that sum to target.
    Return a BBNode object that has the indexes of the numbers
    in the subset, or None if no subset found.
    '''
    BBNode.set_items(ints)
    BBNode.set_target(target)
    BBNode.count = 0
        
    pq = [ BBNode() ]
    
    safety_valve = 100*len(ints)
    
    while pq:
        node = heapq.heappop(pq)
        succ = node.expand()
        if not succ:
            continue
        for x in [node,succ]:
            if x.is_solution():
                return x
            if x.potential_solution():
                heapq.heappush(pq, x)
        safety_valve -= 1
        if not safety_valve:
            break
            
    return None


