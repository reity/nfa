"""Data structure for nondeterministic finite automata.

Python data structure derived from dict that can represent
nondeterministic finite automata (NFAs) as an ensemble of
dictionaries (where dictionary instances serve as nodes,
dictionary keys serve as edge labels, and dictionary values
serve as edges).
"""

from __future__ import annotations
from typing import Sequence, Optional, Any
import doctest
from collections.abc import Iterable, Collection
from reiter import reiter

class nfa(dict):
    """
    An instance of this class can represent an individual state within a
    nondeterministic finite automaton (NFA). When a state represented by
    an instance of this class is understood to be a starting state, it
    also represents an NFA as a whole that consists of all states that
    are reachable from the starting state.

    While instances of this class serve as individual NFA states, entries
    within the instances represent transitions between states (with keys
    serving as transition labels). In the example below, an NFA with four
    states and three transitions is defined. The transition labels are
    ``'a'``, ``'b'``, and ``'c'``.

    >>> n = nfa({'a': nfa({'b': nfa({'c': nfa()})})})

    "Strings" of symbols are represented using iterable sequences of Python
    values or objects that can serve as dictionary keys. Applying an instance
    of this class to an iterable sequences of symbols returns the length (as
    an integer) of the longest path that (1) traverses an ordered sequence of
    transitions whose labels match the sequence of symbols supplied as the
    argument and (1) terminates at an accepting state.

    >>> n(['a', 'b', 'c'])
    3

    The ``epsilon`` object can be used to represent unlabeled transitions.

    >>> a = nfa({'a': nfa({epsilon: nfa()})})
    >>> a('a', full=False)
    1
    >>> a = nfa({'a': nfa({epsilon: nfa({'b': nfa()})})})
    >>> a('a', full=False) is None
    True

    Increasingly complex NFAs can be represented by building up instances of
    this class; cycles can be introduced by adding references to instances that
    have already been defined.

    >>> accept = nfa()
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
    >>> b_star_c[epsilon] = abc
    >>> (b_star_c('a'), b_star_c('b'), b_star_c('c'), b_star_c('d'))
    (1, 1, 1, None)
    >>> abc[epsilon] = abc
    >>> (abc('a'), abc('b'), abc('c'), abc('d'))
    (1, 1, 1, None)
    >>> b_star_c[epsilon] = [abc, b_star_c]
    >>> (b_star_c('a'), b_star_c('b'), b_star_c('c'), b_star_c('d'))
    (1, 1, 1, None)
    """
    def __new__(cls, argument=None):
        """
        Constructor for an instance that enforces constraints on argument types
        (*i.e.*, NFA instances can only have other NFA instances or lists/tuples
        thereof as values).

        >>> nfa()
        nfa()
        >>> n = nfa({'a': nfa()})
        >>> n = nfa({'a': [nfa()]})
        >>> n = nfa({'a': (nfa(),)})
        >>> n = nfa([('x', nfa())])
        >>> n = nfa(list(zip(['a', 'b'], [nfa(), nfa()])))

        Any attempt to construct an ``nfa`` instance that does not contain other
        ``nfa`` instances (or lists/tuples of ``nfa`` instances) raises an
        exception.

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
        Return a boolean indicating whether the state represented by this ``nfa``
        instance is an accepting state.

        Be default, a non-empty instance *is not* an accepting state and an
        empty instance *is* an accepting state.

        >>> bool(nfa())
        True
        >>> bool(nfa({'a': nfa()}))
        False

        Modifying an empty instance by adding a transition entry to it causes
        it to become a non-accepting state. In the example below, ``cycle``
        does not accept any string because it contains no accepting states.

        >>> cycle = nfa()
        >>> cycle['a'] = cycle
        >>> bool(cycle)
        False
        >>> cycle('a') is None
        True
        """
        # pylint: disable=E1101
        return len(self) == 0 if not hasattr(self, "_accept") else self._accept

    def __pos__(self: nfa) -> nfa:
        """
        Return a shallow copy of this instance with the state represented
        by this `nfa` instance marked as an accepting state.

        >>> n = nfa({'a': nfa({'b': nfa()})})
        >>> n('a') is None
        True
        >>> n = nfa({'a': +nfa({'b': nfa()})})
        >>> n('a')
        1
        """
        nfa_ = nfa(self.items())
        setattr(nfa_, "_accept", True)
        return nfa_

    def __neg__(self: nfa) -> nfa:
        """
        Return a shallow copy of this instance with the state represented
        by this `nfa` instance marked as a non-accepting state.

        >>> none = nfa({'a': nfa({'b': -nfa()})})
        >>> none('a') is None
        True
        >>> none(['a', 'b'], full=False) is None
        True
        """
        nfa_ = nfa(self.items())
        setattr(nfa_, "_accept", False)
        return nfa_

    def __invert__(self: nfa) -> nfa:
        """
        Return a shallow copy of this instance that has an accepting status
        that is the opposite of the accepting status of this instance.

        >>> none = nfa({'a': nfa({'b': ~nfa()})})
        >>> none('a') is None
        True
        >>> none(['a', 'b'], full=False) is None
        True
        >>> none['a']['b'] = ~none['a']['b']
        >>> none(['a', 'b'])
        2
        """
        nfa_ = nfa(self.items())
        setattr(nfa_, "_accept", not bool(self))
        return nfa_

    def __mod__(self: nfa, argument: Any) -> Sequence[nfa]:
        """
        Return a list of zero or more `nfa` instances reachable using any path
        that has exactly one transition labeled with the supplied argument (and
        any number of epsilon transitions). If the supplied argument is itself
        `epsilon`, then all states reachable via zero or more `epsilon`
        transitions are returned.

        >>> a = nfa({'a': nfa()})
        >>> b = nfa({epsilon: [a]})
        >>> c = nfa({epsilon: [a]})
        >>> b[epsilon].append(c)
        >>> c[epsilon].append(b)
        >>> n = nfa({epsilon: [b, c]})
        >>> len(n % epsilon)
        4
        >>> a = nfa({'a': nfa()})
        >>> b = nfa({epsilon: [a]})
        >>> c = nfa({epsilon: [a]})
        >>> b[epsilon].append(c)
        >>> c[epsilon].append(b)
        >>> n = nfa({epsilon: [b, c]})
        >>> len(n % 'a')
        1
        """
        if argument == epsilon:
            # Collect all possible branches reachable via epsilon transitions.
            (nfas, cont) = ({id(self): self}, True) # pylint: disable=C0103
            while cont:
                cont = False
                for nfa_ in list(nfas.values()):
                    nfas_ = nfa_.get(epsilon, [])
                    for nfa__ in [nfas_] if isinstance(nfas_, nfa) else nfas_:
                        if id(nfa__) not in nfas:
                            nfas[id(nfa__)] = nfa__
                            cont = True

            # The dictionary was used for deduplication.
            return nfas.values()

        # Return all instances reachable via any path that contains zero or
        # more epsilon transitions and exactly one transition labeled with
        # the supplied argument.
        return {
            id(nfa___): nfa___
            for nfa_ in self % epsilon
            for nfa__ in nfa_ @ argument
            for nfa___ in nfa__ % epsilon
        }.values()

    def __matmul__(self: nfa, argument: Any) -> Sequence[nfa]:
        """
        Return a list of zero or more `nfa` instances reachable using a single
        transition that has a label (either epsilon or a symbol) matching the
        supplied argument.

        >>> n = nfa({'a': nfa({'b': nfa({'c': nfa()})})})
        >>> n @ 'a'
        [nfa({'b': nfa({'c': nfa()})})]
        >>> n @ 'b'
        []
        >>> n = nfa({epsilon: [nfa({'a': nfa()}), nfa({'b': nfa()})]})
        >>> n @ epsilon
        [nfa({'a': nfa()}), nfa({'b': nfa()})]
        """
        nfas_or_nfa = self.get(argument, [])
        return [nfas_or_nfa] if isinstance(nfas_or_nfa, nfa) else nfas_or_nfa

    def compile(self: nfa, _compiled=None, _states=None, _ids=None):
        """
        Compile the NFA represented by this instance (*i.e.*, the NFA in which
        this instance is the starting state) into a transition table and save
        the table as a private attribute.

        >>> final = nfa()
        >>> middle = +nfa({456: final})
        >>> first = nfa({123: middle})
        >>> (first([123]), first([123, 456]), first([456]))
        (1, 2, None)
        >>> first = first.compile()
        >>> (first([123]), first([123, 456]), first([456]))
        (1, 2, None)

        Compilation can improve performance when applying instances to iterable
        sequences of symbols.

        >>> zeros = nfa({epsilon: nfa()})
        >>> zeros[0] = [zeros]
        >>> zeros = zeros.compile()
        >>> all(zeros([0] * i) == i for i in range(10))
        True

        Compilation does not affect what sequences are accepted, and invoking
        this method multiple times for the same instance has no new effects.

        >>> empty = nfa({epsilon: nfa()})
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
        >>> reject = nfa({epsilon: -nfa()})
        >>> (reject(''), reject('', full=False))
        (None, None)
        >>> reject = reject.compile()
        >>> (reject(''), reject('', full=False))
        (None, None)
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
        closure = self % epsilon
        for nfa__ in closure:
            if nfa__: # pylint: disable=W0212
                compiled[id(self)] = None

            # Update the state dictionary with this state/node (to ensure that
            # all states in the closure are included in the dictionary).
            states[id(nfa__)] = nfa__

            # Compile across all transitions from the state/node.
            for symbol in nfa__:
                if not symbol == epsilon:
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
                    if not symbol == epsilon:
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

    def states(self: nfa, argument: Any=None) -> Sequence[nfa]:
        """
        Collect set of all states (*i.e.*, the corresponding `nfa` instances)
        reachable from this instance, or the set of states reachable via
        any one transition that has a label matching the supplied argument.

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

        All states (including accepting empty states and states that have
        only epsilon transitions) are included.

        >>> none = nfa({epsilon: nfa()})
        >>> len([s for s in none.states()])
        2
        """
        # Return list of all reachable states.
        if argument is None:
            if not hasattr(self, '_states'):
                self.compile()

            return self._states # pylint: disable=E1101

        # If an argument is supplied, return the subset of states reachable
        # via matching one transition with the supplied argument.
        return self @ argument

    def symbols(self: nfa) -> set:
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
        Compile the NFA represented by this instance (*i.e.*, the NFA in which
        this instance is the starting state) into a DFA that accepts the same
        set of symbol sequences.

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
        >>> n = nfa()
        >>> n[epsilon] = n
        >>> n([]) is None
        True
        >>> d = n.to_dfa()
        >>> d([]) is None
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
            state: (+nfa() if any(i in t_nfa and t_nfa[i] is None for i in state) else -nfa())
            for state in states
        }

        # Link the DFA states/nodes with one another.
        for (state, dfa) in dfas.items():
            for (symbol, state_) in t_dfa:
                if state == state_:
                    dfa[symbol] = dfas[frozenset(t_dfa[(symbol, state_)])]

        # The new DFA has a starting node that corresponds to starting
        # node in this NFA instance.
        return dfas[frozenset([id(self)])]

    def __call__(self: nfa, string: Iterable, full: bool=True, _length=0) -> Optional[int]:
        """
        Determine whether a "string" (*i.e.*, iterable sequence of symbols)
        is accepted by this `nfa` instance.

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
        >>> zero = nfa({0:one, epsilon:[two, three]}).compile()
        >>> (zero([0, 1, 2, 3]), zero([2, 3]), zero([3]), zero([2, 2, 3]))
        (4, 2, 1, None)
        >>> (zero([0, 1, 2, 3, 4], full=False), zero([2, 3, 4], full=False), zero([2], full=False))
        (4, 2, None)
        >>> zeros = nfa({epsilon:[accept]})
        >>> zeros[0] = [zeros]
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

        A sequence of symbols of length zero is accepted if only epsilon
        transitions are traversed to reach an accepting state. If no
        accepting state can be reached, it is rejected.

        >>> none = nfa({epsilon: nfa()})
        >>> none('')
        0
        >>> none = nfa({epsilon: -nfa()})
        >>> none('') is None
        True

        Any attempt to apply an instance to a non-sequence or other invalid
        argument raises an exception.

        >>> accept = nfa()
        >>> accept(123)
        Traceback (most recent call last):
          ...
        ValueError: input must be an iterable
        >>> accept([epsilon])
        Traceback (most recent call last):
          ...
        ValueError: input cannot contain epsilon
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
        closure = self % epsilon # Set of all reachable states/nodes.

        # Attempt to obtain the next symbol or end the search.
        # The length of each successful match will be collected so that the longest
        # match can be chosen (e.g., if matching the full string is not required).
        try:
            symbol = string[_length] # Obtain the next symbol in the string.

            if symbol == epsilon:
                raise ValueError('input cannot contain epsilon')

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
        Return string representation of instance. Instances that represent small
        NFAs that do not contain cycles yield strings that can be evaluated.

        >>> nfa()
        nfa()
        >>> nfa({'a': nfa({'b':(nfa(),)})})
        nfa({'a': nfa({'b': (nfa(),)})})
        >>> nfa({'a': [nfa({'b': [nfa()]})]})
        nfa({'a': [nfa({'b': [nfa()]})]})

        Instances that have been designated as accepting (or as non-accepting)
        in a manner that deviates from the default are marked as such with the
        appropriate prefix operator.

        >>> +nfa({'a': nfa()})
        +nfa({'a': nfa()})
        >>> +nfa({'a': -nfa()})
        +nfa({'a': -nfa()})

        Instances that have cycles are not converted into a string beyond any
        depth at which a state repeats.

        >>> cycle = nfa({'a': nfa()})
        >>> cycle['a']['b'] = cycle
        >>> cycle
        nfa({'a': nfa({'b': nfa({...})})})

        Any attempt to convert an instance that contains invalid values into a
        string raises an exception.

        >>> cycle['a'] = 123
        >>> cycle
        Traceback (most recent call last):
          ...
        TypeError: values must be nfa instances or non-empty lists/tuples of nfa instances
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
        Return string representation of instance. Instances that represent small
        NFAs that do not contain cycles yield strings that can be evaluated.
        """
        return str(self)

    def copy(self: nfa, _memo=None) -> nfa:
        """
        Return a deep copy of this instance in which all reachable instances of
        ``nfa`` are new copies but references to all other objects are not copies.

        >>> m = nfa({'a': nfa({'b': nfa({'c': nfa()})})})
        >>> n = m.copy()
        >>> n('abc')
        3
        >>> set(map(id, m.states())) & set(map(id, n.states()))
        set()

        This method behaves as expected when cycles exist.

        >>> a_star = +nfa()
        >>> a_star['a'] = a_star
        >>> a_star['b'] = [nfa()]
        >>> a_star_ = a_star.copy()
        >>> all(a_star_('a' * i) == i for i in range(10))
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

class epsilon:
    """
    Singleton class for the epsilon transition label. Only a sole instance
    of  this class is ever be created. Therefore, the symbol ``epsilon``
    exported by this library is assigned the sole *instance* of this class.
    Thus, the exported exported object ``epsilon`` can be used in any context
    that expects a transition label.

    >>> nfa({epsilon: nfa()})
    nfa({epsilon: nfa()})
    """
    def __hash__(self: epsilon) -> int:
        """
        All instances are the same instance because this is a singleton class.

        >>> {epsilon, epsilon}
        {epsilon}
        """
        return 0

    def __eq__(self: epsilon, other: epsilon) -> bool:
        """
        All instances are the same instance because this is a singleton class.

        >>> epsilon == epsilon
        True
        """
        return isinstance(self, type(other))

    def __str__(self: epsilon) -> str:
        """
        String representation (conforms with exported symbol for epsilon).

        >>> str(epsilon)
        'epsilon'
        """
        return 'epsilon'

    def __repr__(self: epsilon) -> str:
        """
        String representation (conforms with exported symbol for epsilon).

        >>> epsilon
        epsilon
        """
        return str(self)

# The exported symbol refers to the sole instance of the
# epsilon transition label class.
epsilon = epsilon()

if __name__ == "__main__":
    doctest.testmod() # pragma: no cover
