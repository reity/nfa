===
nfa
===

Library for defining and working with native Python implementations of nondeterministic finite automata (NFAs).

|pypi| |travis| |coveralls|

.. |pypi| image:: https://badge.fury.io/py/nfa.svg
   :target: https://badge.fury.io/py/nfa
   :alt: PyPI version and link.

.. |travis| image:: https://travis-ci.com/reity/nfa.svg?branch=main
   :target: https://travis-ci.com/reity/nfa

.. |coveralls| image:: https://coveralls.io/repos/github/reity/nfa/badge.svg?branch=main
   :target: https://coveralls.io/github/reity/nfa?branch=main

Purpose
-------
This library makes it possible to concisely construct nondeterministic finite automata (NFAs) using common Python data structures and operators, as well as to perform common operations involving NFAs. NFAs are represented using a class derived from the Python dictionary type, wherein dictionary objects serve as individual states and dictionary entries serve as transitions (with dictionary keys representing transition labels).

Package Installation and Usage
------------------------------
The package is available on PyPI::

    python -m pip install nfa

The library can be imported in the usual way::

    import nfa
    from nfa import nfa

Examples
^^^^^^^^
This library makes it possible to concisely construct an NFA. In the example below, an NFA is defined in which transition labels are strings. It is then applied to an iterable of strings. This returns the length (as an integer) of the longest path that (1) traverses an ordered sequence of transitions whose labels match the sequence of symbols supplied as the argument and (1) terminates at an accepting state::

    >>> from nfa import nfa
    >>> n = nfa({'a': nfa({'b': nfa({'c': nfa()})})})
    >>> n(['a', 'b', 'c'])
    3

By default, an empty NFA object ``nfa()`` is an accepting state and a non-empty object is *not* an accepting state. When an NFA is applied to an iterable of labels that does not traverse a path that leads to an accepting state, ``None`` is returned::

    >>> n(['a', 'b']) is None
    True

To ensure that a state is not accepting, the built-in prefix operator ``-`` can be used::

    >>> n = nfa({'a': nfa({'b': nfa({'c': -nfa()})})})
    >>> n(['a', 'b', 'c']) is None
    True

The prefix operator ``+`` yields an accepting state and the prefix operator ``~`` reverses whether a state is accepting::

    >>> n = nfa({'a': ~nfa({'b': +nfa({'c': nfa()})})})
    >>> n(['a'])
    1
    >>> n(['a', 'b'])
    2

Applying the built-in ``bool`` function to an ``nfa`` object returns a boolean value indicating whether that *that specific object* (and *not* the overall NFA within which it may be an individual state) is an accepting state::

    >>> bool(n)
    False
    >>> bool(nfa())
    True
    >>> bool(-nfa())
    False

Epsilon transitions can be introduced using the ``epsilon`` object::

    >>> from nfa import epsilon
    >>> n = nfa({'a': nfa({epsilon: nfa({'b': nfa({'c': nfa()})})})})
    >>> n(['a', 'b', 'c'])
    3

If an NFA instance is applied to an iterable that yields enough symbols to reach an accepting state but has additional symbols remaining, ``None`` is returned::

    >>> n(['a', 'b', 'c', 'd', 'e']) is None
    True
    
If the length of the longest path leading to an accepting state is desired (even if additional symbols remain in the iterable), the ``full`` parameter can be set to ``False``::

    >>> n(['a', 'b', 'c', 'd', 'e'], full=False)
    3

It is possible to retrieve the set of all transition labels that are found in the overall NFA (note that this does not include instances of ``epsilon``)::

    >>> n.symbols()
    {'c', 'a', 'b'}

Because the ``nfa`` class is derived from ``dict``, it supports all operators and methods that are supported by ``dict``. In particular, the state reachable from a given state via a transition that has a specific label can be retrieved by using index notation::

    >>> n.keys()
    dict_keys(['a'])
    >>> m = n['a']
    >>> m(['b', 'c'])
    2

To retrieve the collection of *all* states that can be reached via paths that involve zero or more epsilon transitions (and no labeled transitions), the built-in infix operator ``%`` can be used (note that this also includes *all* intermediate states along the paths to the first labeled transitions)::

    >>> b = nfa({epsilon: nfa({'b': nfa()})})
    >>> c = nfa({'c': nfa()})
    >>> n = nfa({epsilon: [b, c]})
    >>> for s in (n % epsilon): print(s)
    ...
    nfa({epsilon: [nfa({epsilon: nfa({'b': nfa()})}), nfa({'c': nfa()})]})
    nfa({epsilon: nfa({'b': nfa()})})
    nfa({'c': nfa()})
    nfa({'b': nfa()})

Other methods make it possible to retrieve all the states found in an NFA, to compile an NFA (enabling more efficient processing of iterables), and to compile an NFA into a deterministic finite automaton (DFA). Descriptions and examples of these methods can be found in the documentation for the main library module.

Documentation
-------------
.. include:: toc.rst

The documentation can be generated automatically from the source files using `Sphinx <https://www.sphinx-doc.org/>`_::

    python -m pip install sphinx sphinx-rtd-theme
    cd docs
    sphinx-apidoc -f -E --templatedir=_templates -o _source .. ../setup.py && make html

Testing and Conventions
-----------------------
All unit tests are executed and their coverage is measured when using `nose <https://nose.readthedocs.io/>`_ (see ``setup.cfg`` for configution details)::

    nosetests

The subset of the unit tests included in the module itself can be executed using `doctest <https://docs.python.org/3/library/doctest.html>`_::

    python nfa/nfa.py -v

Style conventions are enforced using `Pylint <https://www.pylint.org/>`_::

    pylint nfa test/test_nfa

Contributions
-------------
In order to contribute to the source code, open an issue or submit a pull request on the GitHub page for this library.

Versioning
----------
The version number format for this library and the changes to the library associated with version number increments conform with `Semantic Versioning 2.0.0 <https://semver.org/#semantic-versioning-200>`_.
