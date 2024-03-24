import melee
from melee.enums import Action, Button
from Chains.chain import Chain
from enum import Enum

class SHORTEN(Enum):
    SHORT = 0
    MID_SHORT = 1
    MID = 2
    LONG = 3

class Illusion(Chain):
    def __init__(self, length=SHORTEN.LONG):
        self.length = length

    def step(self, gamestate, custombot_state, opponent_state):
        controller = self.controller

        # Yea, the names are wrong here, deal with it. Maybe I'll fix it sometime

        # Let go of the controller once starting the illusion
        if custombot_state.action == Action.SWORD_DANCE_2_HIGH:
            self.interruptible = False
            controller.empty_input()
            return

        # End the chain
        if custombot_state.on_ground or custombot_state.action == Action.DEAD_FALL:
            self.interruptible = True
            controller.empty_input()
            return

        # Start the illusion
        illusionactions = [Action.SWORD_DANCE_2_HIGH, Action.SWORD_DANCE_2_MID, Action.SWORD_DANCE_3_HIGH]
        if custombot_state.action not in illusionactions:
            # If we already pressed B last frame, let go
            if controller.prev.button[Button.BUTTON_B]:
                self.interruptible = True
                controller.empty_input()
                return
            x = 0
            if custombot_state.position.x < 0:
                x = 1
            self.interruptible = False
            controller.tilt_analog(Button.BUTTON_MAIN, x, 0.5)
            controller.press_button(Button.BUTTON_B)
            return

        if custombot_state.action == Action.SWORD_DANCE_2_MID:
            if custombot_state.action_frame == 1 and self.length == SHORTEN.SHORT:
                controller.press_button(Button.BUTTON_B)
                return
            if custombot_state.action_frame == 3 and self.length == SHORTEN.MID_SHORT:
                controller.press_button(Button.BUTTON_B)
                return
            if custombot_state.action_frame == 4 and self.length == SHORTEN.MID:
                controller.press_button(Button.BUTTON_B)
                return

        controller.empty_input()
