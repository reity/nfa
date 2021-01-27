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

Package Installation and Usage
------------------------------
The package is available on PyPI::

    python -m pip install nfa

The library can be imported in the usual way::

    import nfa
    from nfa import nfa

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
