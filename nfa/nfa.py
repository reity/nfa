"""Data structure for non-deterministic finite automata.

Python data structure derived from dict that can represent
non-deterministic finite automata (NFAs) as an ensemble of
dictionaries (where dictionary instances serve as nodes,
dictionary keys serve as edge labels, and dictionary values
serve as edges).
"""

from __future__ import annotations
import doctest
from collections.abc import Iterable
from itertools import chain

class nfa(dict):
    """
    Class for a non-deterministic finite automaton
    (also an individual state node in the NFA state
    graph).
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
    >>> d_abc('b')
    False
    >>> f_star_e_d_abc = nfa({'e': d_abc})
    >>> f_star_e_d_abc('edb')
    True
    >>> f_star_e_d_abc['f'] = f_star_e_d_abc
    >>> all(f_star_e_d_abc(('f'*i) + 'edb') for i in range(5))
    True
    >>> f_star_e_d_abc['f'] = [f_star_e_d_abc]
    >>> all(f_star_e_d_abc(('f'*i) + 'edb') for i in range(5))
    True
    >>> f_star_e_d_abc['f'] = [f_star_e_d_abc, abc]
    >>> all(f_star_e_d_abc(('f'*5) + x) for i in range(1,5) for x in 'abc')
    True
    >>> b_star_c = nfa({'c':accept})
    >>> b_star_c['b'] = b_star_c
    >>> b_star_c('bbbbc')
    True
    >>> b_star_c(['b', 'b', 'b', 'b', 'c'])
    True
    >>> b_star_c((c for c in ['b', 'b', 'b', 'b', 'c']))
    True
    >>> accept(123)
    Traceback (most recent call last):
      ...
    ValueError: input must be an iterable
    """
    def __call__(self: nfa, string, _string=None) -> bool:
        if not isinstance(string, Iterable):
            raise ValueError('input must be an iterable')
        string = iter(string)

        # Reconstruction of string returned back to invocation.
        _string = {} if _string is None else _string

        # Attempt to obtain the next symbol or finish search.
        try:
            symbol = next(string) # Obtain the next symbol in the string.
            if symbol in self:
                nfas_ = self[symbol] # Consume one symbol.

                # There are multiple branches.
                if isinstance(nfas_, (tuple, list, set, frozenset)):
                    _string[()] = string # Set up reconstructible string.
                    for nfa_ in nfas_: # For each possible branch.
                        if nfa_(string, _string):
                            return True
                        # Restored string from call for next iteration.
                        string = _string[()]
                else:
                    if nfas_(string):
                        return True

            _string[()] = chain([symbol], string) # Restore symbol.
            return False # No accepting path found.

        except StopIteration:
            _string[()] = [] # Empty string for restoration.
            return len(self) == 0

if __name__ == "__main__":
    doctest.testmod() # pragma: no cover
