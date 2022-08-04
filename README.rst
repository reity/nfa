===
nfa
===

Pure-Python library for building and working with nondeterministic finite automata (NFAs).

|pypi| |readthedocs| |actions| |coveralls|

.. |pypi| image:: https://badge.fury.io/py/nfa.svg
   :target: https://badge.fury.io/py/nfa
   :alt: PyPI version and link.

.. |readthedocs| image:: https://readthedocs.org/projects/nfa/badge/?version=latest
   :target: https://nfa.readthedocs.io/en/latest/?badge=latest
   :alt: Read the Docs documentation status.

.. |actions| image:: https://github.com/reity/nfa/workflows/lint-test-cover-docs/badge.svg
   :target: https://github.com/reity/nfa/actions/workflows/lint-test-cover-docs.yml
   :alt: GitHub Actions status.

.. |coveralls| image:: https://coveralls.io/repos/github/reity/nfa/badge.svg?branch=main
   :target: https://coveralls.io/github/reity/nfa?branch=main
   :alt: Coveralls test coverage summary

Purpose
-------
This library makes it possible to concisely construct nondeterministic finite automata (NFAs) using common Python data structures and operators, as well as to perform common operations involving NFAs. NFAs are represented using a class derived from the Python dictionary type, wherein dictionary objects serve as individual states and dictionary entries serve as transitions (with dictionary keys representing transition labels).

Installation and Usage
----------------------
This library is available as a `package on PyPI <https://pypi.org/project/nfa>`__::

    python -m pip install nfa

The library can be imported in the usual way::

    import nfa
    from nfa import nfa

Examples
^^^^^^^^

.. |nfa| replace:: ``nfa``
.. _nfa: https://nfa.readthedocs.io/en/3.1.0/_source/nfa.html#nfa.nfa.nfa

This library makes it possible to concisely construct an NFA by using one or more instances of the |nfa|_ class. In the example below, an NFA is defined in which transition labels are strings::

    >>> from nfa import nfa
    >>> n = nfa({'a': nfa({'b': nfa({'c': nfa()})})})

The |nfa|_ object can be applied to a sequence of symbols (represented as an iterable of transition labels). This returns the length (as an integer) of the longest path that (1) traverses an ordered sequence of the NFA's transitions whose labels match the sequence of symbols supplied as the argument and (2) terminates at an accepting state::

    >>> n(['a', 'b', 'c'])
    3

By default, an empty NFA object ``nfa()`` is an accepting state and a non-empty object is *not* an accepting state. When an NFA is applied to an iterable of labels that does not traverse a path that leads to an accepting state, ``None`` is returned::

    >>> n(['a', 'b']) is None
    True

.. |neg| replace:: ``-``
.. _neg: https://nfa.readthedocs.io/en/3.1.0/_source/nfa.html#nfa.nfa.nfa.__neg__

To ensure that a state is not accepting (even if it is empty), the built-in prefix operator |neg|_ can be used::

    >>> n = nfa({'a': nfa({'b': nfa({'c': -nfa()})})})
    >>> n(['a', 'b', 'c']) is None
    True

.. |pos| replace:: ``+``
.. _pos: https://nfa.readthedocs.io/en/3.1.0/_source/nfa.html#nfa.nfa.nfa.__pos__

.. |inv| replace:: ``~``
.. _inv: https://nfa.readthedocs.io/en/3.1.0/_source/nfa.html#nfa.nfa.nfa.__invert__

The prefix operator |pos|_ returns an accepting state and the prefix operator |inv|_ reverses whether a state is accepting::

    >>> n = nfa({'a': ~nfa({'b': +nfa({'c': nfa()})})})
    >>> n(['a'])
    1
    >>> n(['a', 'b'])
    2

.. |bool| replace:: ``bool``
.. _bool: https://docs.python.org/3/library/functions.html#bool

Applying the built-in |bool|_ function to an |nfa|_ object returns a boolean value indicating whether *that specific object* (and *not* the overall NFA within which it may be an individual state) is an accepting state::

    >>> bool(n)
    False
    >>> bool(nfa())
    True
    >>> bool(-nfa())
    False

.. |epsilon| replace:: ``epsilon``
.. _epsilon: https://nfa.readthedocs.io/en/3.1.0/_source/nfa.html#nfa.nfa.epsilon

Epsilon transitions can be introduced using the |epsilon|_ object::

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

It is possible to retrieve the set of all transition labels that are found in the overall NFA (note that this does not include instances of |epsilon|_)::

    >>> n.symbols()
    {'c', 'a', 'b'}

.. |dict| replace:: ``dict``
.. _dict: https://docs.python.org/3/library/stdtypes.html#dict

Because the |nfa|_ class is derived from |dict|_, it supports all operators and methods that are supported by |dict|_. In particular, the state reachable from a given state via a transition that has a specific label can be retrieved by using index notation::

    >>> n.keys()
    dict_keys(['a'])
    >>> m = n['a']
    >>> m(['b', 'c'])
    2

.. |mod| replace:: ``%``
.. _mod: https://nfa.readthedocs.io/en/3.1.0/_source/nfa.html#nfa.nfa.nfa.__mod__

To retrieve the collection of *all* states that can be reached via paths that involve zero or more epsilon transitions (and no labeled transitions), the built-in infix operator |mod|_ can be used (note that this also includes *all* intermediate states along the paths to the first labeled transitions)::

    >>> b = nfa({epsilon: nfa({'b': nfa()})})
    >>> c = nfa({'c': nfa()})
    >>> n = nfa({epsilon: [b, c]})
    >>> for s in (n % epsilon):
    ...     print(s)
    ...
    nfa({epsilon: [nfa({epsilon: nfa({'b': nfa()})}), nfa({'c': nfa()})]})
    nfa({epsilon: nfa({'b': nfa()})})
    nfa({'c': nfa()})
    nfa({'b': nfa()})

Other methods make it possible to `retrieve all the states found in an NFA <https://nfa.readthedocs.io/en/3.1.0/_source/nfa.html#nfa.nfa.nfa.states>`__, to `compile an NFA <https://nfa.readthedocs.io/en/3.1.0/_source/nfa.html#nfa.nfa.nfa.compile>`__ (enabling more efficient processing of iterables), and to `transform an NFA into a deterministic finite automaton (DFA) <https://nfa.readthedocs.io/en/3.1.0/_source/nfa.html#nfa.nfa.nfa.to_dfa>`__. Descriptions and examples of these methods can be found in the `documentation for the main library module <https://nfa.readthedocs.io/en/3.1.0/_source/nfa.html>`__.

Development
-----------
All installation and development dependencies are fully specified in ``pyproject.toml``. The ``project.optional-dependencies`` object is used to `specify optional requirements <https://peps.python.org/pep-0621>`__ for various development tasks. This makes it possible to specify additional options (such as ``docs``, ``lint``, and so on) when performing installation using `pip <https://pypi.org/project/pip>`__::

    python -m pip install .[docs,lint]

Documentation
^^^^^^^^^^^^^
The documentation can be generated automatically from the source files using `Sphinx <https://www.sphinx-doc.org>`__::

    python -m pip install .[docs]
    cd docs
    sphinx-apidoc -f -E --templatedir=_templates -o _source .. && make html

Testing and Conventions
^^^^^^^^^^^^^^^^^^^^^^^
All unit tests are executed and their coverage is measured when using `pytest <https://docs.pytest.org>`__ (see the ``pyproject.toml`` file for configuration details)::

    python -m pip install .[test]
    python -m pytest

The subset of the unit tests included in the module itself can be executed using `doctest <https://docs.python.org/3/library/doctest.html>`__::

    python src/nfa/nfa.py -v

Style conventions are enforced using `Pylint <https://pylint.pycqa.org>`__::

    python -m pip install .[lint]
    python -m pylint src/nfa test/test_nfa.py

Contributions
^^^^^^^^^^^^^
In order to contribute to the source code, open an issue or submit a pull request on the `GitHub page <https://github.com/reity/nfa>`__ for this library.

Versioning
^^^^^^^^^^
The version number format for this library and the changes to the library associated with version number increments conform with `Semantic Versioning 2.0.0 <https://semver.org/#semantic-versioning-200>`__.

Publishing
^^^^^^^^^^
This library can be published as a `package on PyPI <https://pypi.org/project/nfa>`__ by a package maintainer. First, install the dependencies required for packaging and publishing::

    python -m pip install .[publish]

Ensure that the correct version number appears in ``pyproject.toml``, and that any links in this README document to the Read the Docs documentation of this package (or its dependencies) have appropriate version numbers. Also ensure that the Read the Docs project for this library has an `automation rule <https://docs.readthedocs.io/en/stable/automation-rules.html>`__ that activates and sets as the default all tagged versions. Create and push a tag for this version (replacing ``?.?.?`` with the version number)::

    git tag ?.?.?
    git push origin ?.?.?

Remove any old build/distribution files. Then, package the source into a distribution archive::

    rm -rf build dist src/*.egg-info
    python -m build --sdist --wheel .

Finally, upload the package distribution archive to `PyPI <https://pypi.org>`__::

    python -m twine upload dist/*
