import melee
from melee.enums import Action, Button
from Chains.chain import Chain

class Roll(Chain):
    def step(self, gamestate, custombot_state, opponent_state):
        controller = self.controller

        # Don't try to spot dodge in the air
        if not custombot_state.on_ground:
            self.interruptible = True
            controller.empty_input()
            return

        # If we're shielding, do the roll
        if custombot_state.action in [Action.SHIELD_REFLECT, Action.SHIELD, Action.SHIELD_START]:
            if controller.prev.main_stick != (.5, .5):
                controller.tilt_analog(Button.BUTTON_MAIN, .5, .5)
                return
            self.interruptible = False
            controller.tilt_analog(Button.BUTTON_MAIN, int(custombot_state.position.x < opponent_state.position.x), 0.5)
            return

        # Let go once we're in the roll
        if custombot_state.action in [Action.ROLL_BACKWARD, Action.ROLL_FORWARD]:
            self.interruptible = True
            controller.empty_input()
            return

        # If we already pressed L last frame, let go
        if controller.prev.button[Button.BUTTON_L]:
            self.interruptible = True
            controller.empty_input()
            return

        self.interruptible = False
        controller.press_button(Button.BUTTON_L)
        controller.tilt_analog(Button.BUTTON_MAIN, .5, .5)
