from abc import ABCMeta
import Tactics

class Strategy:
    __metaclass__ = ABCMeta
    tactic = None

    def picktactic(self, tactic):
        if type(self.tactic) != tactic:
            self.tactic = tactic(self.logger,
                                self.controller,
                                self.framedata,
                                self.difficulty
            )
        self.tactic.step(self._propagate[0], self._propagate[1], self._propagate[2])

    def step(self, gamestate, custombot_state, opponent_state): ...
