#
# Author: Michael Stoll
# Last Updated: 4/3/2024 12:13 am
#

import melee
from melee.enums import Action, Button
from Chains.chain import Chain

class Juggle(Chain):
    "Keeps the opponent airborne by hitting them every time they try to land"
    def __init__(self):
        self.interruptible = True

    def step(self, gamestate, custombot_state, opponent_state):
        controller = self.controller
        self.interruptible = True

         #first, make sure we can even hit the target
        if opponent_state.action in [Action.DEAD_UP]:
            self.interruptible = False
            controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0.5)
            return
        
         #then see if they are in range and attack

         #not in range. so track the character and wait for them to be in range
        if opponent_state.action in [Action.THROWN_UP]:
            
            return

        self.interruptible = True
        controller.release_all()