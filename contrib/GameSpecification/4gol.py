from contrib.GameSpecification import BaseClass

from rules import StateRuleList, CountingRule, SquareNeighbourhoodShellIndexingRule, GameRuleDict

class GameOfZombiesAndMonsters(BaseClass.GameSpecification):
    def __init__(self):
        self.DEAD, self.ALIVE, self.ZOMBIE, self.MONSTER = range(4)
        dead_rules = StateRuleList(
            [
                CountingRule(self.ALIVE,
                             SquareNeighbourhoodShellIndexingRule([1]),
                             {3: self.ALIVE}),
                CountingRule(self.ZOMBIE,
                             SquareNeighbourhoodShellIndexingRule([1]),
                             {3: self.ZOMBIE}),
                CountingRule(self.MONSTER,
                             SquareNeighbourhoodShellIndexingRule([1]),
                             {3: self.MONSTER}),
                CountingRule(self.ALIVE,
                             SquareNeighbourhoodShellIndexingRule([1, 2]),
                             dict([(x, self.ZOMBIE) for x \
                                   in range(18, 25)])),
                ],
            self.DEAD)
        alive_rules = StateRuleList(
            [
                CountingRule(self.ZOMBIE,
                             SquareNeighbourhoodShellIndexingRule([1]),
                             dict([(x, self.ZOMBIE) for x \
                                   in range(2, 9)])),
                CountingRule(self.ALIVE,
                             SquareNeighbourhoodShellIndexingRule([1]),
                             {2: self.ALIVE,
                              3: self.ALIVE}),
                ],
            self.DEAD)
        zombie_rules = StateRuleList(
            [
                CountingRule(self.MONSTER,
                             SquareNeighbourhoodShellIndexingRule([1]),
                             dict([(x, self.MONSTER) for x \
                                   in range(1, 9)])),
                CountingRule(self.MONSTER,
                             SquareNeighbourhoodShellIndexingRule([1, 2]),
                             dict([(x, self.MONSTER) for x \
                                   in range(2, 25)])),
                CountingRule(self.ZOMBIE,
                             SquareNeighbourhoodShellIndexingRule([1]),
                             {2: self.ZOMBIE,
                              3: self.ZOMBIE}),
                CountingRule(self.ZOMBIE,
                             SquareNeighbourhoodShellIndexingRule([1, 2]),
                             dict([(x, self.ZOMBIE) for x \
                                   in range(13, 19)] + \
                                  [(x, self.MONSTER) for x \
                                    in range(19, 25)])),
                CountingRule(self.ALIVE,
                             SquareNeighbourhoodShellIndexingRule([1]),
                             {2: self.ZOMBIE,
                              3: self.ZOMBIE}),
                ],
            self.DEAD)
        monster_rules = StateRuleList(
            [
                CountingRule(self.MONSTER,
                             SquareNeighbourhoodShellIndexingRule([1]),
                             dict([(x, self.MONSTER) for x \
                                   in range(3, 5)])),
                CountingRule(self.ALIVE,
                             SquareNeighbourhoodShellIndexingRule([1]),
                             dict([(x, self.ALIVE) for x \
                                   in range(3, 5)] + \
                                  [(x, self.DEAD) for x \
                                    in range(5, 9)])),
                CountingRule(self.ZOMBIE,
                             SquareNeighbourhoodShellIndexingRule([1]),
                             dict([(x, self.ZOMBIE) for x \
                                   in range(4, 5)] + \
                                  [(x, self.MONSTER) for x \
                                    in range(5, 6)])),
                ],
            self.ALIVE)

        self.rule_dict = GameRuleDict({self.DEAD: dead_rules,
                                       self.ALIVE: alive_rules,
                                       self.ZOMBIE: zombie_rules,
                                       self.MONSTER: monster_rules})
        self.colormap = {self.DEAD: BaseClass.colors['black'],
                         self.ALIVE: BaseClass.colors['white'],
                         self.ZOMBIE: BaseClass.colors['green'],
                         self.MONSTER: BaseClass.colors['red']}
        self.button_action_map = {BaseClass.buttons['left']: self.ALIVE,
                                  BaseClass.buttons['right']: self.DEAD,
                                  BaseClass.buttons['right']: self.ZOMBIE}

