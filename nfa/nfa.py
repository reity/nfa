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

class epsilon:
    """
    Singleton class for epsilon-transition edge label.
    """
    def __hash__(self):
        return 0

    def __eq__(self, other):
        return isinstance(self, epsilon) and isinstance(other, epsilon)

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
    >>> e = epsilon()
    >>> b_star_c[e] = abc
    >>> (b_star_c('a'), b_star_c('b'), b_star_c('c'), b_star_c('d'))
    (True, True, True, False)
    >>> abc[e] = abc
    >>> (abc('a'), abc('b'), abc('c'), abc('d'))
    (True, True, True, False)
    >>> b_star_c[e] = [abc, b_star_c]
    >>> (b_star_c('a'), b_star_c('b'), b_star_c('c'), b_star_c('d'))
    (True, True, True, False)
    >>> accept(123)
    Traceback (most recent call last):
      ...
    ValueError: input must be an iterable
    """
    def __matmul__(self: nfa, argument):
        """
        Return a list of zero or more `nfa` instances
        based on the supplied argument.
        """
        if argument in self:
            nfas = self[argument]
            if isinstance(nfas, (tuple, list, set, frozenset)):
                nfas = list(nfas)
            else:
                nfas = list([nfas])
            return nfas

        return list()

    def __call__(self: nfa, string, _string=None) -> bool:
        """
        Determine whether a "string" (i.e., iterable) of symbols
        is accepted by the `nfa` instance.
        """
        if not isinstance(string, Iterable):
            raise ValueError('input must be an iterable')
        string = iter(string)

        # Reconstruction of string returned back to invocation.
        _string = {} if _string is None else _string

        # Attempt to obtain the next symbol or end the search.
        try:
            # Obtain the next symbol in the string.
            symbol = next(string)

            # Collect all possible branches reachable via empty transitions.
            (nfas, cont, e) = ({id(self): self}, True, epsilon()) # pylint: disable=C0103
            while cont:
                cont = False
                for nfa_ in list(nfas.values()):
                    for nfa__ in nfa_ @ e:
                        if id(nfa__) not in nfas:
                            nfas[id(nfa__)] = nfa__
                            cont = True

            # For each branch, find all branches corresponding to the symbol.
            for nfa_ in nfas.values():
                if symbol in nfa_:
                    nfas_ = nfa_ @ symbol # Consume one symbol.
                    _string[()] = string # Set up reconstructible string.
                    for nfa__ in nfas_: # For each possible branch.
                        if nfa__(string, _string):
                            return True
                        # Restored string from call for next iteration.
                        string = _string[()]

            _string[()] = chain([symbol], string) # Restore symbol.
            return False # No accepting path found.

        except StopIteration:
            _string[()] = [] # Empty string for restoration.
            return len(self) == 0

# Use symbol for sole instance of singleton class.
_epsilon = epsilon()

if __name__ == "__main__":
    doctest.testmod() # pragma: no cover
