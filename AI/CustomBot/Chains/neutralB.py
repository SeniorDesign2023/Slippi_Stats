#
# Author: Michael Stoll
# Last Updated: 4/3/2024 11:55 am
#
import melee
from melee.enums import Action, Button
from Chains.chain import Chain

class NeutralB(Chain):
    "Charges and activates neutral B"
    def __init__(self):
        self.interruptible = True

    def step(self, gamestate, custombot_state, opponent_state):
        controller = self.controller
        self.interruptible = True

        #first, make sure we're not in a strange state
        if custombot_state.action in [Action.TURNING, Action.LANDING]:
            self.interruptible = False
            controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0.5)
            return


        #now make sure it's not a side B. 
        if custombot_state.action == Action.DASHING:
            self.interruptible = True
            controller.tilt_analog(Button.BUTTON_MAIN, int(not custombot_state.facing), 0.5)
            return
        
        #finally, we're standing still or only moving vertically. charge until full then fire
        #might still be bugged. debug here first
        if custombot_state.action in [Action.STANDING, Action.FALLING]:
            if custombot_state.action_frame == 1:
                self.interruptible = False
                controller.tilt_analog(Button.BUTTON_MAIN, int(custombot_state.position.x < opponent_state.position.x), 0.5)
                if custombot_state.action == Action.NEUTRAL_B_FULL_CHARGE:
                    controller.release_button(Button.BUTTON_B)
                else:
                    controller.press_button(Button.BUTTON_B)
                return
            


        self.interruptible = True
        controller.release_all()