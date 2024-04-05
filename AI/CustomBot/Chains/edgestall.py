import melee
from melee.enums import Action, Button
from Chains.chain import Chain

# Edgestall
class Edgestall(Chain):
    def step(self, gamestate, custombot_state, opponent_state):
        controller = self.controller

        # If we just grabbed the edge, wait
        if custombot_state.action == Action.EDGE_CATCHING:
            self.interruptible = True
            controller.empty_input()
            return

        # If we are able to let go of the edge, do it
        if custombot_state.action == Action.EDGE_HANGING:
            # If we already pressed back last frame, let go
            if controller.prev.c_stick != (0.5, 0.5):
                controller.empty_input()
                return
            x = 1
            if custombot_state.position.x < 0:
                x = 0
            self.interruptible = False
            controller.tilt_analog(Button.BUTTON_C, x, 0.5)
            return

        """ This should work for most characters, but is designed for Fox."""
        # Once we're falling, UP-B
        if custombot_state.action == Action.FALLING:
            self.interruptible = False
            controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 1)
            controller.press_button(Button.BUTTON_B)
            return

        self.interruptible = True
        controller.empty_input()
