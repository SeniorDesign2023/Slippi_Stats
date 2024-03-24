import melee
from melee.enums import Action, Button
from Chains.chain import Chain

""" Will need to write a counter tactic for Marth and other characters with counters. """
class Counter(Chain):
    def step(self, gamestate, custombot_state, opponent_state):
        controller = self.controller

        # We're done here if Marth is in the counter stance or if he's performing the counter attack
        if custombot_state.action in [Action.MARTH_COUNTER, Action.MARTH_COUNTER_FALL]:
            self.interruptible = True
            controller.empty_input()
            return

        # Press down and B to initiate the counter
        controller.press_button(Button.BUTTON_B)
        controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0)
        self.interruptible = False
