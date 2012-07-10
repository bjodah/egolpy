#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

from project_helpers import memoize

from motif import SquareGridMotif

class GameRuleDict(dict):
    def bind_to_motif(self, motif):
        self._motif = motif
        for state, state_rule_list in self.items():
            state_rule_list.bind_to_motif(motif)

def test_GameRuleDict():
    grd = GameRuleDict({'a': 1, 'b': 2})
    #assert hasattr(grd, 'bind_to_motif')
    assert grd['a'] == 1
    assert grd['b'] == 2
    assert grd.get('c', None) == None


class StateRuleList(list):
    """
    Set of rules for a state
    """

    def __init__(self, counting_rule_list, default_outcome):
        """
        A state has a ordered rule set
        """
        super(self.__class__, self).__init__(counting_rule_list)
        self.default_outcome = default_outcome
        self.reverse_map = None

    def bind_to_motif(self, motif):
        self._motif = motif
        for counting_rule in self:
            counting_rule.bind_to_motif(motif)


def test_StateRuleList():
    srl = StateRuleList([1, 2, 3], 7)
    assert srl.default_outcome == 7
    assert srl[:] == [1, 2, 3]


class NeigbourCounting(object):
    pass


class CountingRule(object):
    """
    Rule class for egol
    """

    def __init__(self, counted_state, neighbour_indexing_rule,
                 count_outcomes):
        """
        """
        self.counted_state = counted_state
        self._neighbour_indexing_rule = neighbour_indexing_rule
        self._count_outcomes = count_outcomes

    def bind_to_motif(self, motif):
        self._motif = motif
        self._neighbour_indexing_rule.bind_to_motif(motif)


    def match(self, index):
        nr = self._motif.count_state_at_indices(self.counted_state,
                    self._neighbour_indexing_rule.get_neigh_idxs(index))
        # nr = sum([self._motif[i] == self.counted_state for i in \
        #          self._neighbour_indexing_rule.get_neigh_idxs(index)])
        return self._count_outcomes.get(nr, None)

    @memoize
    def get_neigh_idxs(self, index):
        return self._neighbour_indexing_rule.get_neigh_idxs(index)

    def __str__(self):
        fmtstr = "CountingRule({},{},{})"
        return fmtstr.format(self.counted_state, self._neighbour_indexing_rule, self._count_outcomes)

class NeighbourIndexingRule(object):
    def __init__(self, *args):
        pass

    def __str__(self):
        pass


class SquareNeighbourhoodShellIndexingRule(NeighbourIndexingRule):
    """
    TODO:
    Implement caching?
    """

    def __init__(self, shell_idxs):
        self._shell_idxs = shell_idxs
        self._motif = None

    def bind_to_motif(self, motif):
        assert isinstance(motif, SquareGridMotif)
        self._motif = motif

    def get_neigh_idxs(self, index):
        result = []
        for shell_idx in self._shell_idxs:
            result.extend(self._motif.get_nth_square_neighbour_indices(shell_idx, index))
        return result

    def __str__(self):
        return "<SqNeighShIdxRl({})>".format(self._shell_idxs)

def test_SquareNeighbourhoodShellIndexingRule():
    snsir = SquareNeighbourhoodShellIndexingRule([1])
    motif = SquareGridMotif(sparse_data= {5: 1, 6: 1, 9: 1, 10: 1}.items(),
                            dim = (4, 4))
    snsir.bind_to_motif(motif)
    neigh7 = snsir.get_neigh_idxs(7)
    count = 0
    for ni in neigh7:
        print(motif[ni])
        count += 1 if motif[ni] == 1 else 0
    print(count)
    print(motif)
    print(neigh7)
    for ni in neigh7:
        motif[ni] = 2
    print(motif)


