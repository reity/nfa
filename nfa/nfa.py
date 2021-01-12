"""Data structure for nondeterministic finite automata.

Python data structure derived from dict that can represent
nondeterministic finite automata (NFAs) as an ensemble of
dictionaries (where dictionary instances serve as nodes,
dictionary keys serve as edge labels, and dictionary values
serve as edges).
"""

from __future__ import annotations
import doctest
from collections.abc import Iterable
from reiter import reiter

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
    Class for a nondeterministic finite automaton (also an individual
    state/node in the NFA state graph).

    >>> final = nfa()
    >>> middle = +nfa({456:final})
    >>> first = nfa({123:middle})
    >>> (first([123]), first([123, 456]), first([456]))
    (1, 2, None)
    >>> first = first.compile()
    >>> (first([123]), first([123, 456]), first([456]))
    (1, 2, None)
    >>> accept = nfa()
    >>> three = nfa({3:accept})
    >>> two = nfa({2:three})
    >>> one = nfa({1:two})
    >>> zero = nfa({0:one, 2:three})
    >>> (zero([0, 1, 2, 3]), zero([2, 3]), zero([2, 2, 3]))
    (4, 2, None)
    >>> (zero([0, 1, 2, 3, 4], full=False), zero([2, 3, 4], full=False), zero([2], full=False))
    (4, 2, None)
    >>> zero = nfa({0:one, epsilon():[two, three]}).compile()
    >>> (zero([0, 1, 2, 3]), zero([2, 3]), zero([3]), zero([2, 2, 3]))
    (4, 2, 1, None)
    >>> (zero([0, 1, 2, 3, 4], full=False), zero([2, 3, 4], full=False), zero([2], full=False))
    (4, 2, None)
    >>> zeros = nfa({epsilon():[accept]})
    >>> zeros[0] = [zeros]
    >>> all(zeros([0]*i) == i for i in range(10))
    True
    >>> zeros = nfa({epsilon():[accept]})
    >>> zeros[0] = [zeros]
    >>> zeros = zeros.compile()
    >>> all(zeros([0]*i) == i for i in range(10))
    True
    >>> zeros = nfa({0:[accept]})
    >>> zeros[0].append(zeros)
    >>> all(zeros([0]*i) == i for i in range(1, 10))
    True
    >>> all(zeros([0]*i, full=False) == i for i in range(1, 10))
    True
    >>> zeros = zeros.compile()
    >>> all(zeros([0]*i) == i for i in range(1, 10))
    True
    >>> all(zeros([0]*i, full=False) == i for i in range(1, 10))
    True
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
    @staticmethod
    def _has(string: reiter, index: int) -> bool:
        """
        Return a boolean indicating whether a reiterable symbol
        string instance has a symbol at the specified index.
        """
        try:
            string[index] # pylint: disable=W0104
            return True
        except (StopIteration, IndexError):
            return False

    def _accepts(self: nfa) -> bool:
        """
        Return a boolean indicating whether the state/node represented
        by this `nfa` instance is an accepting state.
        """
        # pylint: disable=E1101
        return len(self) == 0 or\
            (hasattr(self, "_accept") and self._accept)

    def __pos__(self: nfa) -> nfa:
        """
        Return a shallow copy of this NFA with the state/node represented
        by this `nfa` instance marked as an accepting state.
        """
        nfa_ = nfa(self.items())
        setattr(nfa_, "_accept", True)
        return nfa_

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

    def compile(self: nfa, _compiled=None, _ids=None):
        """
        Compile NFA represented by this instance (i.e., acting as the initial
        state/node) into a transition table and save it as a private attribute.
        """
        compiled = {} if _compiled is None else _compiled
        ids = [] if _ids is None else _ids

        # Cut off recursion if this state/node has already been visited.
        if id(self) in ids:
            return self

        # Update the transition table with entries corresponding to
        # this node.
        updated = False
        closure = self._epsilon_closure()
        for nfa__ in closure.values():
            if nfa__._accepts(): # pylint: disable=W0212
                compiled[id(self)] = None

            for symbol in nfa__:
                if not isinstance(symbol, epsilon):
                    for nfa_ in nfa__ @ symbol:
                        # Add entry for the current state/node and symbol if it is not present.
                        if (symbol, id(self)) not in compiled:
                            compiled[(symbol, id(self))] = set()

                        # Update the transition table.
                        compiled[(symbol, id(self))] |= {id(nfa_)}
                        updated = True

        # If any updates were made to the transition table, compile recursively.
        if updated:
            for nfa__ in closure.values():
                for symbol in nfa__:
                    if not isinstance(symbol, epsilon):
                        for nfa_ in nfa__ @ symbol:
                            nfa_.compile(_compiled=compiled, _ids=(ids + [id(self)]))

        # If we are at the root invocation, save the transition table as an attribute.
        if _compiled is None:
            setattr(self, "_compiled", compiled)

        return self

    def __call__(self: nfa, string, full: bool=True, _length=0) -> bool:
        """
        Determine whether a "string" (i.e., iterable) of symbols
        is accepted by the `nfa` instance.
        """
        if not isinstance(string, (Iterable, reiter)):
            raise ValueError('input must be an iterable')
        string = reiter(string)

        # If the NFA represented by this instance has been compiled, attempt
        # to match the supplied string via the compiled transition table.

        if hasattr(self, "_compiled") and self._compiled is not None: # pylint: disable=E1101
            lengths = set() # Lengths of paths that led to an accepting state/node.
            ids_ = set([id(self)]) # Working set of states/nodes during multi-branch traversal.

            while True:
                # Collect the list of subsequent states/nodes.
                ids__ = set()
                for id_ in ids_:
                    # pylint: disable=E1101
                    if id_ in self._compiled and (not full or not nfa._has(string, _length)):
                        lengths.add(_length)

                # Attempt to traverse possible paths using the next symbol in the string.
                try:
                    symbol = string[_length]
                    _length += 1

                    # Check table for given symbol and current states/nodes.
                    for id_ in ids_:
                        if (symbol, id_) in self._compiled: # pylint: disable=E1101
                            ids__ |= set(self._compiled[(symbol, id_)]) # pylint: disable=E1101

                    # No matching subsequent state/node exists.
                    if len(ids__) == 0:
                        return None if full else max(lengths, default=None)

                    # Update working set of states/nodes.
                    ids_ = ids__
                except (StopIteration, IndexError):
                    # Accept longest match if terminal states/nodes found.
                    if any(id_ in self._compiled for id_ in ids_): # pylint: disable=E1101
                        return _length
                    return max(lengths, default=None) if not full else None

        # Since there is no compiled transition table, attempt to match
        # the supplied string via a recursive traversal through the nodes.
        closure = self._epsilon_closure().values() # Set of all reachable states/nodes.

        # Attempt to obtain the next symbol or end the search.
        # The length of each successful match will be collected so that the longest
        # match can be chosen (e.g., if matching the full string is not required).
        try:
            symbol = string[_length] # Obtain the next symbol in the string.

            # Examine all possible branches reachable via empty transitions.
            # For each branch, find all branches corresponding to the symbol.
            # Collect the lengths of the matches and return the largest.
            lengths = [_length] if self._accepts() and not full else []
            for nfa_ in closure:
                if symbol in nfa_:
                    nfas_ = nfa_ @ symbol # Consume one symbol.
                    for nfa__ in nfas_: # For each possible branch.
                        length = nfa__(string, full=full, _length=(_length + 1))
                        if length is not None:
                            lengths.append(length)

            return max(lengths, default=None)

        except (StopIteration, IndexError):
            # If there are no more symbols in the string and an accept
            # state/node is immediately reachable, accept.
            return _length if any(nfa_._accepts() for nfa_ in closure) else None

# Use symbol for sole instance of singleton class.
_epsilon = epsilon()

if __name__ == "__main__":
    doctest.testmod() # pragma: no cover
