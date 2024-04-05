import melee
from melee.enums import Action, Button
from Chains.chain import Chain
from enum import Enum


""" Any ranged grabs like Samus's grab will need statements to check if the opponent is in range. """
class THROW_DIRECTION(Enum):
    UP = 0
    DOWN = 1
    FORWARD = 2
    BACK = 3

# Grab and throw opponent
class GrabAndThrow(Chain):
    def __init__(self, direction=THROW_DIRECTION.DOWN):
        self.direction = direction

    def step(self, gamestate, custombot_state, opponent_state):
        controller = self.controller

        self.interruptible = False

        # If we already pressed Z last frame, let go
        if controller.prev.button[Button.BUTTON_Z]:
            controller.empty_input()
            return

        if custombot_state.action == Action.GRAB and custombot_state.action_frame > 12:
            controller.empty_input()
            self.interruptible = True
            return

        if custombot_state.action == Action.LANDING_SPECIAL:
            controller.empty_input()
            self.interruptible = True
            return

        # If we need to jump cancel, do it
        jcstates = [Action.DOWN_B_GROUND_START, Action.DOWN_B_GROUND]
        if (custombot_state.action in jcstates) and custombot_state.action_frame >= 3:
            controller.press_button(Button.BUTTON_Y)
            controller.release_button(Button.BUTTON_Z)
            return

        # Grab on knee bend
        if custombot_state.action == Action.KNEE_BEND:
            # Let go of Z if we already had it pressed
            if controller.prev.button[Button.BUTTON_Z]:
                controller.release_button(Button.BUTTON_Z)
                return
            controller.press_button(Button.BUTTON_Z)
            return

        # Do the throw
        if custombot_state.action in [Action.GRAB_WAIT, Action.GRAB_PULLING]:
            if self.direction == THROW_DIRECTION.DOWN:
                controller.tilt_analog(Button.BUTTON_MAIN, .5, 0)
            if self.direction == THROW_DIRECTION.UP:
                controller.tilt_analog(Button.BUTTON_MAIN, .5, 1)
            if self.direction == THROW_DIRECTION.FORWARD:
                controller.tilt_analog(Button.BUTTON_MAIN, int(custombot_state.facing), .5)
            if self.direction == THROW_DIRECTION.BACK:
                controller.tilt_analog(Button.BUTTON_MAIN, int(not custombot_state.facing), .5)
            self.interruptible = True
            return

        # Do the grab
        # Let go of Z if we already had it pressed
        if controller.prev.button[Button.BUTTON_Z]:
            controller.release_button(Button.BUTTON_Z)
            return
        controller.press_button(Button.BUTTON_Z)
