"""Data structure for nondeterministic finite automata.

Python data structure derived from dict that can represent
nondeterministic finite automata (NFAs) as an ensemble of
dictionaries (where dictionary instances serve as nodes,
dictionary keys serve as edge labels, and dictionary values
serve as edges).
"""

from __future__ import annotations
import doctest
from collections.abc import Iterable, Collection
from reiter import reiter

class epsilon:
    """
    Singleton class for epsilon-transition edge label.

    >>> nfa({_epsilon: nfa()})
    nfa({epsilon: nfa()})
    """
    def __hash__(self):
        """
        All instances are the same instance because this is a singleton class.
        """
        return 0

    def __eq__(self, other):
        """
        All instances are the same instance because this is a singleton class.
        """
        return isinstance(self, epsilon) and isinstance(other, epsilon)

    def __str__(self):
        """
        String representation (conforms with exported symbol for epsilon).
        """
        return 'epsilon'

    def __repr__(self):
        """
        String representation (conforms with exported symbol for epsilon).
        """
        return str(self)

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
    >>> a = nfa({'a': nfa({epsilon(): nfa()})})
    >>> a('a', full=False)
    1
    >>> a = nfa({'a': nfa({epsilon(): nfa({'b': nfa()})})})
    >>> a('a', full=False) is None
    True
    """
    def __new__(cls, argument=None):
        """
        Constructor for an instance that enforces constraints on argument types
        (i.e., NFA instances can only have other NFA instances or lists/tuples
        thereof as values).

        >>> nfa()
        nfa()
        >>> len(nfa({'a': nfa()}))
        1
        >>> len(nfa({'a': [nfa()]}))
        1
        >>> len(nfa({'a': (nfa(),)}))
        1
        >>> len(nfa([('x', nfa())]))
        1
        >>> len(nfa(list(zip(['a', 'b'], [nfa(), nfa()]))))
        2
        >>> len(nfa(zip(['a', 'b'], [nfa(), nfa()])))
        Traceback (most recent call last):
          ...
        TypeError: argument must be a collection
        >>> nfa({'a': []})
        Traceback (most recent call last):
          ...
        TypeError: values must be nfa instances or non-empty lists/tuples of nfa instances
        >>> nfa({'a': [123]})
        Traceback (most recent call last):
          ...
        TypeError: values must be nfa instances or non-empty lists/tuples of nfa instances
        >>> nfa([1, 2])
        Traceback (most recent call last):
          ...
        TypeError: values must be nfa instances or non-empty lists/tuples of nfa instances
        >>> nfa({'x': 123})
        Traceback (most recent call last):
          ...
        TypeError: values must be nfa instances or non-empty lists/tuples of nfa instances
        >>> nfa({'x': [123]})
        Traceback (most recent call last):
          ...
        TypeError: values must be nfa instances or non-empty lists/tuples of nfa instances
        """
        argument = {} if argument is None else argument

        # Ensure that type checking and other method invocations that may traverse
        # the NFA instance do not consume the argument (e.g., if it is an iterable).
        if not isinstance(argument, Collection):
            raise TypeError('argument must be a collection')

        # Ensure that it is possible to convert the argument to a dictionary using
        # the usual approach (making sure not to consume iterables permanently).
        type_error = TypeError(
            'values must be nfa instances or non-empty lists/tuples of nfa instances'
        )
        try:
            dict_ = dict(argument)
        except TypeError:
            raise type_error from None

        # Ensure value types are NFA instances or tuples/lists thereof.
        for value in dict_.values():
            if isinstance(value, nfa):
                pass
            elif isinstance(value, (tuple, list)) and len(value) > 0 and\
                 all(isinstance(item, nfa) for item in value):
                pass
            else:
                raise type_error

        return super().__new__(cls, dict_)

    def __bool__(self: nfa) -> bool:
        """
        Return a boolean indicating whether the state/node represented
        by this `nfa` instance is an accepting state.

        >>> (bool(nfa()), bool(nfa({'a': nfa()})))
        (True, False)
        >>> empty = nfa({epsilon(): nfa()})
        >>> (empty(''), empty('', full=False))
        (0, 0)
        >>> empty = empty.compile()
        >>> (empty(''), empty('', full=False))
        (0, 0)
        >>> (empty('a'), empty('a', full=False))
        (None, 0)
        >>> empty = empty.compile()
        >>> (empty('a'), empty('a', full=False))
        (None, 0)
        >>> a = nfa({'a': nfa()})
        >>> (a(''), a('', full=False))
        (None, None)
        >>> a = a.compile()
        >>> (a(''), a('', full=False))
        (None, None)
        >>> a = +a
        >>> a('', full=False)
        0
        >>> a = a.compile()
        >>> a('', full=False)
        0
        >>> cycle = nfa()
        >>> cycle['a'] = cycle
        >>> bool(cycle)
        False
        >>> (cycle('a'), cycle('a', full=False))
        (None, None)
        >>> cycle = cycle.compile()
        >>> (cycle('a'), cycle('a', full=False))
        (None, None)
        >>> reject = nfa({epsilon(): -nfa()})
        >>> (reject(''), reject('', full=False))
        (None, None)
        >>> reject = reject.compile()
        >>> (reject(''), reject('', full=False))
        (None, None)
        """
        # pylint: disable=E1101
        return len(self) == 0 if not hasattr(self, "_accept") else self._accept

    def __pos__(self: nfa) -> nfa:
        """
        Return a shallow copy of this NFA with the state/node represented
        by this `nfa` instance marked as an accepting state.

        >>> a = nfa({'a': +nfa({'b': nfa()})})
        >>> a('a')
        1
        """
        nfa_ = nfa(self.items())
        setattr(nfa_, "_accept", True)
        return nfa_

    def __neg__(self: nfa) -> nfa:
        """
        Return a shallow copy of this NFA with the state/node represented
        by this `nfa` instance marked as a non-accepting state.

        >>> none = nfa({'a': nfa({'b': -nfa()})})
        >>> none('a') is None
        True
        >>> none('ab', full=False) is None
        True
        """
        nfa_ = nfa(self.items())
        setattr(nfa_, "_accept", False)
        return nfa_

    def __invert__(self: nfa) -> nfa:
        """
        Return a shallow copy of this NFA with the state/node represented
        by this `nfa` instance marked with an accepting status that is the
        opposite of the original node.

        >>> none = nfa({'a': nfa({'b': ~nfa()})})
        >>> none('a') is None
        True
        >>> none('ab', full=False) is None
        True
        >>> none['a']['b'] = ~none['a']['b']
        >>> none('ab')
        2
        """
        nfa_ = nfa(self.items())
        setattr(nfa_, "_accept", not bool(self))
        return nfa_

    def __matmul__(self: nfa, argument):
        """
        Return a list of zero or more `nfa` instances reachable using transitions
        that match the supplied argument (either epsilon or a symbol).
        """
        if isinstance(argument, epsilon):
            # Collect all possible branches reachable via empty transitions.
            (nfas, cont, e) = ({id(self): self}, True, epsilon()) # pylint: disable=C0103
            while cont:
                cont = False
                for nfa_ in list(nfas.values()):
                    nfas_ = nfa_.get(e, [])
                    for nfa__ in [nfas_] if isinstance(nfas_, nfa) else nfas_:
                        if id(nfa__) not in nfas:
                            nfas[id(nfa__)] = nfa__
                            cont = True

            # The dictionary was used for deduplication.
            return nfas.values()

        # If the argument is a symbol, only one step along any
        # branch is possible.
        nfas_or_nfa = self.get(argument, [])
        return [nfas_or_nfa] if isinstance(nfas_or_nfa, nfa) else nfas_or_nfa

    def compile(self: nfa, _compiled=None, _states=None, _ids=None):
        """
        Compile NFA represented by this instance (i.e., acting as the initial
        state/node) into a transition table and save it as a private attribute.
        """
        compiled = {} if _compiled is None else _compiled
        ids = [] if _ids is None else _ids
        states = {id(self): self} if _states is None else _states

        # Cut off recursion if this state/node has already been visited.
        if id(self) in ids:
            return self

        # Update the transition table with entries corresponding to
        # this node.
        updated = False
        closure = self @ epsilon()
        for nfa__ in closure:
            if nfa__: # pylint: disable=W0212
                compiled[id(self)] = None

            # Update the state dictionary with this state/node (to ensure that
            # all states in the closure are included in the dictionary).
            states[id(nfa__)] = nfa__

            # Compile across all transitions from the state/node.
            for symbol in nfa__:
                if not isinstance(symbol, epsilon):
                    for nfa_ in nfa__ @ symbol:
                        # Add entry for the current state/node and symbol if it is not present.
                        if (symbol, id(self)) not in compiled:
                            compiled[(symbol, id(self))] = set()

                        # Update the transition table.
                        compiled[(symbol, id(self))] |= {id(nfa_)}

                        # Update the state dictionary.
                        states[id(nfa_)] = nfa_

                        # Indicate that compilation should continue.
                        updated = True

        # If any updates were made to the transition table, compile recursively.
        if updated:
            for nfa__ in closure:
                for symbol in nfa__:
                    if not isinstance(symbol, epsilon):
                        for nfa_ in nfa__ @ symbol:
                            nfa_.compile(
                                _compiled=compiled,
                                _states=states,
                                _ids=(ids + [id(self)])
                            )

        # If we are at the root invocation, save the state list and
        # transition table as attributes.
        if _compiled is None:
            setattr(self, "_compiled", compiled)
            setattr(self, "_states", list(states.values()))

        return self

    def states(self: nfa, argument=None):
        """
        Collect set of all states/nodes (i.e., the corresponding `nfa` instances)
        reachable from this NFA instance, or the set of states reachable via
        transitions that match the supplied argument.

        >>> abcd = nfa({'a': nfa({'b': nfa({'c': nfa()})})})
        >>> abcd['a']['b']['d'] = nfa()
        >>> [list(sorted(state.symbols())) for state in abcd.states()]
        [['a', 'b', 'c', 'd'], ['b', 'c', 'd'], ['c', 'd'], [], []]
        >>> [
        ...     [list(sorted(s.symbols())) for s in state.states(list(state.keys())[0])]
        ...     for state in abcd.states()
        ...     if len(state.keys()) > 0
        ... ]
        [[['b', 'c', 'd']], [['c', 'd']], [[]]]
        >>> none = nfa({_epsilon: nfa()})
        >>> none('')
        0
        >>> none = nfa({_epsilon: -nfa()})
        >>> none('') is None
        True
        >>> len([s for s in none.states()])
        2
        """
        # Return list of all reachable states.
        if argument is None:
            if not hasattr(self, '_states'):
                self.compile()

            return self._states # pylint: disable=E1101

        # If an argument is supplied, return the subset of states
        # reachable via matching with the supplied argument.
        return self @ argument

    def symbols(self: nfa):
        """
        Collect set of all symbols found in transitions of the NFA instance

        >>> nfa({'a': nfa({'b': nfa({'c': nfa()})})}).symbols() == {'a', 'b', 'c'}
        True
        """
        if not hasattr(self, '_compiled'):
            self.compile()

        return set(e[0] for e in self._compiled if isinstance(e, tuple)) # pylint: disable=E1101

    def to_dfa(self: nfa) -> nfa:
        """
        Compile NFA represented by this instance (i.e., acting as the initial
        state/node) into a DFA that accepts the same language.

        >>> final = nfa()
        >>> middle = +nfa({456:final})
        >>> first = nfa({123:middle})
        >>> first = first.to_dfa()
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
        >>> zero = zero.to_dfa()
        >>> (zero([0, 1, 2, 3]), zero([2, 3]), zero([2, 2, 3]))
        (4, 2, None)
        >>> (zero([0, 1, 2, 3, 4], full=False), zero([2, 3, 4], full=False), zero([2], full=False))
        (4, 2, None)
        >>> accept = nfa().compile()
        >>> accept('')
        0
        >>> accept('a') is None
        True
        >>> a_star = +nfa()
        >>> a_star['a'] = a_star
        >>> a_star = a_star.compile()
        >>> all(a_star('a'*i) == i for i in range(10))
        True
        >>> a_star('b') is None
        True
        """
        # The DFA transition table is built using the NFA transition table.
        if not hasattr(self, '_compiled'):
            self.compile()

        # Create empty DFA transition table.
        (t_nfa, t_dfa) = (self._compiled, {}) # pylint: disable=E1101

        # Build the deterministic transition table.
        states = [frozenset([id(self)])]
        updated = True
        while updated:
            updated = False
            states_ = set()
            for state in states:
                for symbol in self.symbols():
                    state_ = frozenset([
                        j
                        for i in state
                        if (symbol, i) in t_nfa
                        for j in t_nfa[(symbol, i)]
                    ])

                    if (symbol, state) not in t_dfa:
                        t_dfa[(symbol, state)] = set()

                    if not state_.issubset(t_dfa[(symbol, state)]):
                        t_dfa[(symbol, state)] |= state_
                        states_.add(state_)
                        updated = True

            states = states_

        # Remove transitions that lead to the empty set state.
        t_dfa = dict((e[0], frozenset(e[1])) for e in t_dfa.items() if len(e[1]) > 0)
        states = {frozenset({id(self)})} # Add initial state in case there are no transitions.
        states |= {state for (_, state) in t_dfa.items()} | {state for (_, state) in t_dfa}

        # Build states/nodes for DFA and mark them as accepting states/nodes
        # if they are such.
        dfas = {
            state: (+nfa() if any(i in t_nfa and t_nfa[i] is None for i in state) else nfa())
            for state in states
        }

        # Link the DFA states/nodes with one another.
        for (state, dfa) in dfas.items():
            for (symbol, state_) in t_dfa:
                if state == state_:
                    dfa[symbol] = dfas[frozenset(t_dfa[(symbol, state_)])]

        # The new DFA has a starting node that corresponds to starting node in this NFA instance.
        return dfas[frozenset([id(self)])]

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
                    if id_ in self._compiled and (not full or not string.has(_length)):
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
                        return max(lengths)

                    return None if full else max(lengths, default=None)

        # Since there is no compiled transition table, attempt to match
        # the supplied string via a recursive traversal through the nodes.
        closure = self @ epsilon() # Set of all reachable states/nodes.

        # Attempt to obtain the next symbol or end the search.
        # The length of each successful match will be collected so that the longest
        # match can be chosen (e.g., if matching the full string is not required).
        try:
            symbol = string[_length] # Obtain the next symbol in the string.

            # Examine all possible branches reachable via empty transitions.
            # For each branch, find all branches corresponding to the symbol.
            # Collect the lengths of the matches and return the largest.
            lengths = [_length] if self and not full else []
            for nfa_ in closure:
                # If we can reach an accepting state via epsilon transitions,
                # add a potential match length.
                if nfa_ and not full:
                    lengths.append(_length)

                # If the symbol can be consumed, do so and proceed recursively
                # along child branches.
                if symbol in nfa_:
                    nfas_ = nfa_ @ symbol # Consume one symbol.
                    for nfa__ in nfas_: # For each possible branch.
                        length = nfa__(string, full=full, _length=(_length + 1))
                        if length is not None:
                            lengths.append(length)

            # Return the longest match or, if there are none, either accept
            # (if an accepting state node has been reached and a full match is
            # not required) or reject (for this invocation).
            return max(lengths, default=(0 if bool(self) and not full else None))

        except (StopIteration, IndexError):
            # If there are no more symbols in the string and an accept
            # state/node is immediately reachable, accept.
            if any(nfa_ for nfa_ in closure):
                return _length

            # Reject the string (whether full matches are accepted is not relevant
            # because the string has been fully consumed at this point).
            return None

    def __str__(self: nfa, _visited=frozenset()) -> str:
        """
        Return string representation of instance.
        """
        # Avoid unbounded recursion.
        if id(self) in _visited:
            return 'nfa({...})'

        _visited = _visited | {id(self)}

        # Determine if a prefix operator is necessary.
        prefix = ''
        if self and len(self) > 0:
            prefix = '+'
        elif not self and len(self) == 0:
            prefix = '-'

        def str_(o):
            return o.__str__(_visited) if isinstance(o, nfa) else repr(o)

        def strs_(v):
            if isinstance(v, tuple):
                return (
                    '(' + (", ".join(str_(n) for n in v)) + ')'
                    if len(v) != 1 else
                    '(' + str_(v[0]) + ',)'
                )
            if isinstance(v, list):
                return '[' + (", ".join(str_(n) for n in v)) + ']'
            raise TypeError(
                'values must be nfa instances or non-empty lists/tuples of nfa instances'
            )

        return prefix + 'nfa(' + (
            ('{' + (", ".join([
                repr(k) + ': ' + (str_ if isinstance(v, nfa) else strs_)(v)
                for (k, v) in self.items()
            ])) + '}') if len(self) > 0 else ''
        ) + ')'

    def __repr__(self: nfa) -> str:
        """
        Return string representation of instance.

        >>> nfa({'a': nfa({'b':(nfa(),)})})
        nfa({'a': nfa({'b': (nfa(),)})})
        >>> nfa({'a': [nfa({'b': [nfa()]})]})
        nfa({'a': [nfa({'b': [nfa()]})]})
        >>> nfa()
        nfa()
        >>> +nfa({'a': nfa()})
        +nfa({'a': nfa()})
        >>> +nfa({'a': -nfa()})
        +nfa({'a': -nfa()})
        >>> cycle = nfa({'a': nfa()})
        >>> cycle['a']['b'] = cycle
        >>> cycle
        nfa({'a': nfa({'b': nfa({...})})})
        >>> cycle['a'] = 123
        >>> cycle
        Traceback (most recent call last):
          ...
        TypeError: values must be nfa instances or non-empty lists/tuples of nfa instances
        """
        return str(self)

    def copy(self: nfa, _memo=None) -> nfa:
        """
        Return a deep copy of this NFA in which all NFA instances
        are copies but all other references are not copies.

        >>> a_star = +nfa()
        >>> a_star['a'] = a_star
        >>> a_star['b'] = [nfa()]
        >>> a_star_ = a_star.copy()
        >>> all(a_star_('a'*i) == i for i in range(10))
        True
        >>> a_star_('b')
        1
        >>> a_star_('c') is None
        True
        """
        _memo = {} if _memo is None else _memo

        # If this node has already been copied, return the copy.
        if id(self) in _memo:
            return _memo[id(self)]

        # Create a copy of this node.
        nfa_ = nfa()
        if hasattr(self, '_accept'):
            setattr(nfa_, '_accept', self._accept) # pylint: disable=E1101
        _memo[id(self)] = nfa_
        for symbol in self:
            if isinstance(self[symbol], nfa):
                nfa_[symbol] = self[symbol].copy(_memo)
            else:
                nfa_[symbol] = tuple(nfa__.copy(_memo) for nfa__ in self[symbol])

        return nfa_

# Use symbol for sole instance of singleton class.
_epsilon = epsilon()

if __name__ == "__main__":
    doctest.testmod() # pragma: no cover
