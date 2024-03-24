import melee
import Chains
from Tactics.tactic import Tactic
from melee.enums import Action


""" This is a tactic for self destructing when the bot is on an unsupported stage """
class SelfDestruct(Tactic):
    def shouldsd(gamestate, custombot_state, opponent_state):
        supportedstages = [melee.Stage.FINAL_DESTINATION, melee.Stage.BATTLEFIELD, \
            melee.Stage.YOSHIS_STORY, melee.Stage.DREAMLAND, melee.Stage.POKEMON_STADIUM, melee.Stage.FOUNTAIN_OF_DREAMS]

        # SD if we are on an unsupported stage
        if gamestate.stage not in supportedstages:
            return True

        return False

    def step(self, gamestate, custombot_state, opponent_state):
        self._propagate  = (gamestate, custombot_state, opponent_state)

        self.pickchain(Chains.SD)
        return
