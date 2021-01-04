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
    >>> three = nfa({3:accept})
    >>> two = nfa({2:three})
    >>> one = nfa({1:two})
    >>> zero = nfa({0:one, 2:three})
    >>> (zero([0, 1, 2, 3]), zero([2, 3]), zero([2, 2, 3]))
    (4, 2, None)
    >>> zero = nfa({0:one, epsilon():[two, three]}).compile()
    >>> zero([0, 1, 2, 3]), zero([2, 3]), zero([3]), zero([2, 2, 3])
    (4, 2, 1, None)
    >>> abc = nfa({'a':accept, 'b':accept, 'c':accept})
    >>> abc('a')
    1
    >>> (abc('ab'), abc(iter('ab')))
    (None, None)
    >>> d_abc = nfa({'d': abc})
    >>> d_abc('db')
    2
    >>> d_abc('d') is None
    True
    >>> d_abc('c') is None
    True
    >>> d_abc('b') is None
    True
    >>> f_star_e_d_abc = nfa({'e': d_abc})
    >>> f_star_e_d_abc('edb')
    3
    >>> f_star_e_d_abc['f'] = f_star_e_d_abc
    >>> all(f_star_e_d_abc(('f'*i) + 'edb') == i + 3 for i in range(5))
    True
    >>> f_star_e_d_abc['f'] = [f_star_e_d_abc]
    >>> all(f_star_e_d_abc(('f'*i) + 'edb') == i + 3 for i in range(5))
    True
    >>> f_star_e_d_abc['f'] = [f_star_e_d_abc, abc]
    >>> all(f_star_e_d_abc(('f'*i) + x) == i + 1 for i in range(1,5) for x in 'abc')
    True
    >>> set(f_star_e_d_abc(iter(('f'*5) + x))  for _ in range(1,5) for x in 'abc')
    {6}
    >>> b_star_c = nfa({'c':accept})
    >>> b_star_c['b'] = b_star_c
    >>> (b_star_c('bbbbc'), b_star_c(iter('bbbbc')))
    (5, 5)
    >>> b_star_c(['b', 'b', 'b', 'b', 'c'])
    5
    >>> b_star_c((c for c in ['b', 'b', 'b', 'b', 'c']))
    5
    >>> e = epsilon()
    >>> b_star_c[e] = abc
    >>> (b_star_c('a'), b_star_c('b'), b_star_c('c'), b_star_c('d'))
    (1, 1, 1, None)
    >>> abc[e] = abc
    >>> (abc('a'), abc('b'), abc('c'), abc('d'))
    (1, 1, 1, None)
    >>> b_star_c[e] = [abc, b_star_c]
    >>> (b_star_c('a'), b_star_c('b'), b_star_c('c'), b_star_c('d'))
    (1, 1, 1, None)
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

    def _epsilon_closure(self: nfa):
        """
        Collect all possible branches reachable via empty transitions.
        """
        (nfas, cont, e) = ({id(self): self}, True, epsilon()) # pylint: disable=C0103
        while cont:
            cont = False
            for nfa_ in list(nfas.values()):
                for nfa__ in nfa_ @ e:
                    if id(nfa__) not in nfas:
                        nfas[id(nfa__)] = nfa__
                        cont = True
        return nfas

    def compile(self: nfa, _compiled=None):
        """
        Compile NFA represented by this instance (i.e., acting as the initial
        state/node) into a transition table and save it as a private attribute.
        """
        compiled = {} if _compiled is None else _compiled

        # Update the transition table with entries corresponding to
        # this node.
        updated = False
        closure = self._epsilon_closure()
        for nfa__ in closure.values():
            for symbol in nfa__:
                if not isinstance(symbol, epsilon):
                    for nfa_ in nfa__ @ symbol:
                        # Add entry for the current state and symbol if it is not present.
                        if (symbol, id(self)) not in compiled:
                            compiled[(symbol, id(self))] = set()

                        # The accepting terminal state is marked by `None`.
                        compiled[(symbol, id(self))] |= {None if len(nfa_) == 0 else id(nfa_)}
                        updated = True

        # If any updates were made to the transition table, compile recursively.
        if updated:
            for nfa__ in closure.values():
                for symbol in nfa__:
                    if not isinstance(symbol, epsilon):
                        for nfa_ in nfa__ @ symbol:
                            nfa_.compile(_compiled=compiled)

        # If we are at the root invocation, save the transition table as an attribute.
        if _compiled is None:
            setattr(self, "_compiled", compiled)

        return self

    def __call__(self: nfa, string, _string=None, _length=0) -> bool:
        """
        Determine whether a "string" (i.e., iterable) of symbols
        is accepted by the `nfa` instance.
        """
        if not isinstance(string, Iterable):
            raise ValueError('input must be an iterable')
        string = iter(string)

        # If the NFA represented by this instance has been compiled, attempt
        # to match the supplied string via the compiled transition table.

        if hasattr(self, "_compiled") and self._compiled is not None: # pylint: disable=E1101
            ids_ = set([id(self)])
            while True:
                try:
                    # Obtain the next symbol in the string.
                    symbol = next(string)
                    _length += 1

                    # Collect the list of subsequent states/nodes.
                    ids__ = set()
                    for id_ in ids_:
                        if (symbol, id_) in self._compiled: # pylint: disable=E1101
                            ids__ |= set(self._compiled[(symbol, id_)]) # pylint: disable=E1101

                    # If no matching subsequent state/node exists, do not accept.
                    if len(ids__) == 0:
                        return None

                    # Update list of working states/nodes.
                    ids_ = ids__
                except StopIteration:
                    return _length if None in ids_ else None # Accepting terminal state/node.

        # Since there is no compiled transition table, attempt to match
        # the supplied string via a recursive traversal through the nodes.

        # Reconstruction of string returned back to invocation.
        _string = {} if _string is None else _string

        # Attempt to obtain the next symbol or end the search.
        try:
            # Obtain the next symbol in the string.
            symbol = next(string)

            # Collect all possible branches reachable via empty transitions.
            # For each branch, find all branches corresponding to the symbol.
            for nfa_ in self._epsilon_closure().values():
                if symbol in nfa_:
                    nfas_ = nfa_ @ symbol # Consume one symbol.
                    _string[()] = string # Set up reconstructible string.
                    for nfa__ in nfas_: # For each possible branch.
                        length = nfa__(string, _string, _length + 1) # pylint: disable=W0212
                        if length is not None:
                            return length

                        # Restored string from call for next iteration.
                        string = _string[()]

            _string[()] = chain([symbol], string) # Restore symbol.
            return None # No accepting path found.

        except StopIteration:
            _string[()] = [] # Empty string for restoration.
            return _length if len(self) == 0 else None

# Use symbol for sole instance of singleton class.
_epsilon = epsilon()

if __name__ == "__main__":
    doctest.testmod() # pragma: no cover
