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
    Check that the exported namespace provide access to the expected
    classes and functions.
    """
    def test_module(self):
        module = import_module('nfa.nfa')
        self.assertTrue(api_methods().issubset(module.__dict__.keys()))

def powerset(iterable):
    """
    Return iterable of all subsets of items in the input.
    """
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

def strs(alphabet, k):
    """
    Yield all strings of length at most `k` containing
    only the characters in the supplied alphabet of symbols.
    """
    for i in range(k):
        for s in product(*[alphabet]*i):
            yield s

def nfas(alphabet):
    """
    Yield a sample of all NFAs for the supplied alphabet of symbols.
    """
    e = epsilon
    ns = [nfa()]
    while True:
        # Take some of the NFAs that are already built.
        ns = sample(ns, min(len(ns), 3))

        # A new state/node can associate each of the alphabet symbols to any
        # subset of the above NFAs. Thus, collect all subsets of above NFAs.
        nss = list([ns_ for ns_ in powerset(ns) if len(ns_) > 0])

        # Iterate over every non-empty subset of symbols.
        for ss in [ss for ss in powerset(alphabet) if len(ss) > 0]:
            # Iterate over every way of assigning a subset to a symbol:
            for ns_per_s in product(*[nss]*len(ss)):
                n = nfa(zip(ss, ns_per_s))
                # The new state/node can either be an accepting state/node or not.
                for n in [n, +n]:
                    ns.append(n)
                    yield n

class Test_nfa(TestCase):
    def test_nfa(self):
        for nfa_ in islice(nfas(['a', 'b']), 0, 500):
            for s in strs(['a', 'b'], 5):
                match = nfa_(s)
                self.assertTrue((isinstance(match, int) and match == len(s)) or match is None)

    def test_nfa_full_false(self):
        for nfa_ in islice(nfas(['a', 'b']), 0, 500):
            for s in strs(['a', 'b'], 5):
                s += ('c', 'd')
                match = nfa_(s, full=False)
                self.assertTrue((isinstance(match, int) and match <= len(s) - 2) or match is None)

    def test_nfa_compile(self):
        for nfa_ in islice(nfas(['a', 'b']), 0, 500):
            for full in (True, False):
                ss = list(strs(['a', 'b'], 5))
                sms_nfa_ = set((s, m) for s in ss for m in [nfa_(s, full)])
                nfa_ = nfa_.compile()
                sms_nfa_compiled = set((s, m) for s in ss for m in [nfa_(s, full)])
                self.assertEqual(sms_nfa_, sms_nfa_compiled)

    def test_nfa_to_dfa(self):
        for nfa_ in islice(nfas(['a', 'b']), 0, 500):
            for full in (True, False):
                ss = list(strs(['a', 'b'], 5))
                sms_nfa_ = set((s, m) for s in ss for m in [nfa_(s, full)])
                dfa_ = nfa_.to_dfa()
                sms_dfa_ = set((s, m) for s in ss for m in [dfa_(s, full)])
                self.assertEqual(sms_nfa_, sms_dfa_)
