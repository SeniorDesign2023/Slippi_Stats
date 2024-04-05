import melee
import Tactics
import random
from melee.enums import Action, Button
from Strategies.strategy import Strategy
from Tactics.punish import Punish
from Tactics.pressure import Pressure
from Tactics.defend import Defend
from Tactics.recover import Recover
from Tactics.mitigate import Mitigate
from Tactics.edgeguard import Edgeguard
from Tactics.infinite import Infinite
from Tactics.juggle import Juggle
from Tactics.celebrate import Celebrate
from Tactics.wait import Wait
from Tactics.retreat import Retreat
from Tactics.selfdestruct import SelfDestruct
from Tactics.approach import Approach
from Tactics.challenge import Challenge

class Bait(Strategy):
    def __init__(self, logger, controller, framedata, difficulty):
        self.approach = False
        self.approach_frame = -123
        self.logger = logger
        self.controller = controller
        self.framedata = framedata
        self.set_difficulty = difficulty
        self.difficulty = 4

    def __str__(self):
        string = "Bait"

        if not self.tactic:
            return string
        string += str(type(self.tactic))

        if not self.tactic.chain:
            return string
        string += str(type(self.tactic.chain))
        return string

    def step(self, gamestate, custombot_state, opponent_state):
        self._propagate  = (gamestate, custombot_state, opponent_state)

        # -1 means auto-adjust difficulty based on stocks remaining
        if self.set_difficulty == -1:
            self.difficulty = custombot_state.stock
        else:
            self.difficulty = self.set_difficulty

        if SelfDestruct.shouldsd(gamestate, custombot_state, opponent_state):
            self.picktactic(Tactics.SelfDestruct)
            return

        # Reset the approach state after 1 second
        #   Or if opponent becomes invulnerable
        if self.approach and ((abs(self.approach_frame - gamestate.frame) > 60) or (opponent_state.invulnerability_left > 0)):
            self.approach_frame = -123
            self.approach = False

        # Randomly approach sometimes rather than keeping distance
        # Should happen on average once per 2 seconds
        # The effect will last for about 1 second
        # On the first two difficulties, just always approach
        if (random.randint(0, 120) == 0 or (self.difficulty >= 4 and opponent_state.action != Action.CROUCHING)) and (opponent_state.invulnerability_left == 0):
            self.approach = True
            self.approach_frame = gamestate.frame

        if self.logger:
            self.logger.log("Notes", " approach: " + str(self.approach) + " ", concat=True)

        if Mitigate.needsmitigation(custombot_state):
            self.picktactic(Tactics.Mitigate)
            return

        if self.tactic and not self.tactic.isinteruptible():
            self.tactic.step(gamestate, custombot_state, opponent_state)
            return

        # If we're stuck in a lag state, just do nothing. Trying an action might just
        #   buffer an input we don't want
        if Wait.shouldwait(gamestate, custombot_state, opponent_state, self.framedata):
            self.picktactic(Tactics.Wait)
            return

        if Recover.needsrecovery(custombot_state, opponent_state, gamestate):
            self.picktactic(Tactics.Recover)
            return

        if Celebrate.deservescelebration(custombot_state, opponent_state):
            self.picktactic(Tactics.Celebrate)
            return

        # Difficulty 5 is a debug / training mode
        #   Don't do any attacks, and don't do any shielding
        #   Take attacks, DI, and recover
        if self.difficulty == 5:
            self.picktactic(Tactics.KeepDistance)
            return

        if Defend.needsprojectiledefense(custombot_state, opponent_state, gamestate, self.logger):
            self.picktactic(Tactics.Defend)
            return

        """ Difficulty will determine likelihood of doing infinite and should probably have a cap on it """
        # If we can infinite our opponent, do that!
        if Infinite.caninfinite(custombot_state, opponent_state, gamestate, self.framedata, self.difficulty):
            self.picktactic(Tactics.Infinite)
            return
        
        """ Difficulty will determine likelihood of juggling and should probably have a cap on it """
        # If we can juggle opponent in the air, do that
        if Juggle.canjuggle(custombot_state, opponent_state, gamestate, self.framedata, self.difficulty):
            self.picktactic(Tactics.Juggle)
            return

        # If we can punish our opponent for a laggy move, let's do that
        if Punish.canpunish(custombot_state, opponent_state, gamestate, self.framedata):
            self.picktactic(Tactics.Punish)
            return

        # Do we need to defend an attack?
        if Defend.needsdefense(custombot_state, opponent_state, gamestate, self.framedata):
            self.picktactic(Tactics.Defend)
            return

        # Can we edge guard them?
        if Edgeguard.canedgeguard(custombot_state, opponent_state, gamestate):
            self.picktactic(Tactics.Edgeguard)
            return

        # Can we shield pressure them?
        if Pressure.canpressure(opponent_state, gamestate):
            self.picktactic(Tactics.Pressure)
            return

        if Retreat.shouldretreat(custombot_state, opponent_state, gamestate, not self.approach):
            self.picktactic(Tactics.Retreat)
            return

        if Challenge.canchallenge(custombot_state, opponent_state, gamestate, self.framedata, self.difficulty):
            self.picktactic(Tactics.Challenge)
            return

        if Approach.shouldapproach(custombot_state, opponent_state, gamestate, self.framedata, self.logger) or \
                (self.approach and not Approach.approach_too_dangerous(custombot_state, opponent_state, gamestate, self.framedata)):
            self.picktactic(Tactics.Approach)
            return

        self.picktactic(Tactics.KeepDistance)
