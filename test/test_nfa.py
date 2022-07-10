"""
Test suite in which functional unit tests for matching, compilation, and
conversion methods are applied to a sample of a bounded subset of all
possible data structure instances.
"""
from __future__ import annotations
from typing import Sequence, Iterable
from importlib import import_module
from itertools import product, islice, chain, combinations
from random import sample
from unittest import TestCase

from nfa.nfa import nfa, epsilon

def api_methods():
    """
    API symbols that should be available to users upon module import.
    """
    return {'nfa', 'epsilon'}

class Test_namespace(TestCase):
    """
    Tests of module namespace.
    """
    def test_module(self):
        """
        Confirm that the exported namespace provide access to the expected
        classes and functions.
        """
        module = import_module('nfa.nfa')
        self.assertTrue(api_methods().issubset(module.__dict__.keys()))

def powerset(iterable: Iterable) -> Iterable:
    """
    Return iterable of all subsets of items in the input.
    """
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

def strs(alphabet: Sequence[str], k: int) -> Iterable[str]:
    """
    Yield all strings of length at most ``k`` containing
    only the characters in the supplied alphabet of symbols.
    """
    for i in range(k):
        for s in product(*[alphabet]*i):
            yield s

def nfas(alphabet: Sequence[str]) -> Iterable[nfa]:
    """
    Yield a sample of all NFAs for the supplied alphabet of symbols.
    """
    ns = [nfa()]
    while True:
        # Take some of the NFAs that are already built.
        ns = sample(ns, min(len(ns), 3))

        # A new state/node can associate each of the alphabet symbols to any
        # subset of the above NFAs. Thus, collect all subsets of above NFAs.
        nss = [ns_ for ns_ in powerset(ns) if len(ns_) > 0]

        # Iterate over every non-empty subset of symbols.
        for ss in [ss for ss in powerset(alphabet + [epsilon]) if len(ss) > 0]:

            # Iterate over every way of assigning a subset to a symbol
            # in order to create forward edges from the new node.
            for ns_per_s in product(*[nss]*len(ss)):

                # Create new node and its forward edges.
                n = nfa(list(zip(ss, ns_per_s))).copy()

                # Add a self-loop and/or back edges to the node from existing nodes.
                for (s, n_) in product(ss, sample(n.states(), len(n.states()) // 2)):
                    n_[s] = n

                # The new state/node can either be an accepting state/node or not.
                for n in [n.copy(), (+n).copy()]:
                    ns.append(n)
                    yield n

nfas_for_tests = list(islice(nfas(['a', 'b']), 0, 1000))
strs_for_tests = list(strs(['a', 'b'], 7))

class Test_epsilon(TestCase):
    """
    Unit tests of the epsilon transition label class.
    """
    def test_epsilon(self):
        """
        Basic unit tests of the sole epsilon transition label object.
        """
        self.assertTrue(epsilon == epsilon) # pylint: disable=comparison-with-itself
        self.assertTrue(str(epsilon) == 'epsilon')
        self.assertTrue(len({epsilon, epsilon}) == 1)

class Test_nfa(TestCase):
    """
    Functional unit tests of data structure methods.
    """
    def test_nfa(self):
        """
        Basic unit tests of default full string matching functionality.
        """
        for (i, nfa_) in enumerate(nfas_for_tests):
            for s in sample(strs_for_tests, max(1, len(strs_for_tests) // (i + 1))):
                match = nfa_(s)
                self.assertTrue((isinstance(match, int) and match == len(s)) or match is None)

    def test_nfa_full_false(self):
        """
        Basic unit tests of partial string matching functionality.
        """
        for (i, nfa_) in enumerate(nfas_for_tests):
            for s in sample(strs_for_tests, max(1, len(strs_for_tests) // (i + 1))):
                s_ = s + ('c', 'd')
                match = nfa_(s_, full=False)
                self.assertTrue((isinstance(match, int) and match <= len(s_) - 2) or match is None)

    def test_nfa_compile(self):
        """
        Unit tests of instance compilation method and table-based matching functionality.
        """
        for (i, nfa_) in enumerate(nfas_for_tests):
            for full in (True, False):
                ss = list(sample(strs_for_tests, max(1, len(strs_for_tests) // (i + 1))))
                sms_nfa_ = set((s, m) for s in ss for m in [nfa_(s, full)])
                nfa_ = nfa_.compile()
                sms_nfa_compiled = set((s, m) for s in ss for m in [nfa_(s, full)])
                self.assertEqual(sms_nfa_, sms_nfa_compiled)

    def test_nfa_to_dfa_is_dfa(self):
        """
        Unit tests of instance DFA conversion method.
        """
        for (i, nfa_) in enumerate(nfas_for_tests):
            for full in (True, False):
                ss = list(sample(strs_for_tests, max(1, len(strs_for_tests) // (i + 1))))
                sms_nfa_ = set((s, m) for s in ss for m in [nfa_(s, full)])
                dfa_ = nfa_.to_dfa()
                sms_dfa_ = set((s, m) for s in ss for m in [dfa_(s, full)])
                self.assertTrue(dfa_.is_dfa())
                self.assertEqual(sms_nfa_, sms_dfa_)
