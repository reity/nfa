"""Data structure for non-deterministic finite automata.

Python data structure derived from dict that can represent
non-deterministic finite automata (NFAs) as an ensemble of
dictionaries (where dictionary instances serve as nodes,
dictionary keys serve as edge labels, and dictionary values
serve as edges).
"""

from __future__ import annotations
import doctest

class nfa(dict):
    """
    Class for a non-deterministic finite automaton.

    >>> accept = nfa()
    >>> abc = nfa({'a':accept, 'b':accept, 'c':accept})
    >>> abc('a')
    True
    >>> d_abc = nfa({'d': abc})
    >>> d_abc('db')
    True
    >>> d_abc('d')
    False
    >>> d_abc('c')
    False
    """
    def __call__(self, string):
        if len(string) == 0:
            return len(self) == 0
        elif string[0] in self:
            return self[string[0]](string[1:])
        else:
            return False

if __name__ == "__main__":
    doctest.testmod()
