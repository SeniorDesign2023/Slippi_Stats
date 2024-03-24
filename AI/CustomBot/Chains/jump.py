import melee
from melee.enums import Action, Button
from Chains.chain import Chain

class Jump(Chain):
    def __init__(self, x=0.5):
        self.x = x

    def step(self, gamestate, custombot_state, opponent_state):
        controller = self.controller
        self.interruptible = True

        controller.tilt_analog(Button.BUTTON_MAIN, self.x, 0.5)
        if controller.prev.button[Button.BUTTON_Y]:
            controller.release_button(Button.BUTTON_Y)
        else:
            controller.press_button(Button.BUTTON_Y)
