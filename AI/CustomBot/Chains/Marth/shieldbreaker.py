import melee
from melee.enums import Action, Button
from Chains.chain import Chain
from enum import Enum

class ATTACK_DIRECTION(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

""" Might try to add a facing value and have direction default to facing if ATTACK_DIRECTION doesn't work right """
class ShieldBreaker(Chain):
    def __init__(self, charge = 0, direction=ATTACK_DIRECTION.RIGHT):
        self.direction = direction
        self.charge = charge
        self.frames_charged = 0

    def step(self, gamestate, custombot_state, opponent_state):
        controller = self.controller

        # We're done here if Marth is grabbing the ledge or if the move is fully charged
        if custombot_state.action in [Action.EDGE_CATCHING, Action.EDGE_HANGING, Action.MARTH_COUNTER_FALL]:
            self.interruptible = True
            controller.empty_input()
            return

        """ Not sure if you can jump cancel this move but just in case. """
        # Do we need to jump cancel?
        jumpcancelactions = [Action.SHIELD, Action.SHIELD_RELEASE, Action.DASHING, Action.RUNNING]
        if custombot_state.action in jumpcancelactions:
            if controller.prev.button[Button.BUTTON_Y]:
                controller.empty_input()
                return
            self.interruptible = False
            controller.press_button(Button.BUTTON_Y)
            return

        # If Marth is already in the Shield Breaker animation, check if we should release the charge
        if custombot_state.action in [Action.MARTH_COUNTER]:
            if self.frames_charged < self.charge:
                self.interruptible = False
                self.frames_charged += 1
                controller.press_button(Button.BUTTON_B)
            # Simple heuristic: release the charge if the opponent is close or if Marth is near the edge of the stage
            opponent_distance = abs(custombot_state.position.x - opponent_state.position.x)
            edge_distance = min(abs(custombot_state.position.x - melee.stages.EDGE_POSITION[gamestate.stage]),
                                abs(custombot_state.position.x + melee.stages.EDGE_POSITION[gamestate.stage]))
            if opponent_distance < 30 or edge_distance < 20:
                controller.release_button(Button.BUTTON_B)
            return


        self.interruptible = False
        controller.press_button(Button.BUTTON_A)
        if self.direction == ATTACK_DIRECTION.UP:
            controller.tilt_analog(Button.BUTTON_MAIN, .5, 1)
        elif self.direction == ATTACK_DIRECTION.DOWN:
            controller.tilt_analog(Button.BUTTON_MAIN, .5, 0)
        elif self.direction == ATTACK_DIRECTION.LEFT:
            controller.tilt_analog(Button.BUTTON_MAIN, 0, .5)
        elif self.direction == ATTACK_DIRECTION.RIGHT:
            controller.tilt_analog(Button.BUTTON_MAIN, 1, .5)
