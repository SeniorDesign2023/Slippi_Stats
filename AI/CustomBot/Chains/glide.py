import melee
from melee.enums import Action, Button
from Chains.chain import Chain

""" I believe this is a Fox tech called Shine Gliding."""
class Glide(Chain):
    def __init__(self, pivot_point):
        self.pivot_point = pivot_point

    def step(self, gamestate, custombot_state, opponent_state):
        controller = self.controller
        self.interruptible = True

        if gamestate.frame % 2 == 0:
            x = 0.4
            if custombot_state.position.x < self.pivot_point:
                x = 0.6
            controller.tilt_analog(Button.BUTTON_MAIN, x, 0.5)
        else:
            controller.release_all()
