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
    """
    def __call__(self: nfa, string) -> bool:
        if len(string) == 0:
            return len(self) == 0
        elif string[0] in self:
            nfas_ = self[string[0]]
            if isinstance(nfas_, (tuple, list, set, frozenset)):
                return any(nfa_(string[1:]) for nfa_ in nfas_)
            else:
                return nfas_(string[1:])
        else:
            return False

if __name__ == "__main__":
    doctest.testmod() # pragma: no cover
