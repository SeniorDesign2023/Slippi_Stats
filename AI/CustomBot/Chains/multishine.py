import melee
from melee.enums import Action, Button
from Chains.chain import Chain
from enum import Enum

class MULTISHINE_DIRECTION(Enum):
    NEUTRAL = 1
    FORWARD = 2
    BACK = 3

class Multishine(Chain):
    def __init__(self, direction = MULTISHINE_DIRECTION.FORWARD):
        self.direction = direction

    def step(self, gamestate, custombot_state, opponent_state):
        controller = self.controller

        # Don't multishine forward on the Yoshi's lip
        if gamestate.stage == melee.Stage.YOSHIS_STORY and abs(custombot_state.position.x) > 37:
            self.direction = MULTISHINE_DIRECTION.NEUTRAL

        # Don't multishine off the stage
        if abs(abs(custombot_state.position.x) - melee.stages.EDGE_GROUND_POSITION[gamestate.stage]) < 10:
            self.direction = MULTISHINE_DIRECTION.NEUTRAL

        # Pivot if we're dashing. Or else we might dash right off stage, which is annoying
        if custombot_state.action in [Action.DASHING]:
            self.interruptible = True
            controller.tilt_analog(Button.BUTTON_MAIN, int(not custombot_state.facing), 0.5)
            return

        actionable_landing = custombot_state.action == Action.LANDING and custombot_state.action_frame >= 4

        #If standing or turning, shine
        if custombot_state.action in [Action.STANDING, Action.TURNING] or actionable_landing:
            controller.press_button(Button.BUTTON_B)
            controller.tilt_analog(Button.BUTTON_MAIN, .5, 0)
            self.interruptible = False
            return

        #Shine on frame 3 of knee bend, else nothing
        if custombot_state.action == Action.KNEE_BEND:
            if custombot_state.action_frame == 3:
                controller.press_button(Button.BUTTON_B)
                controller.tilt_analog(Button.BUTTON_MAIN, .5, 0)
                self.interruptible = False
                return
            if custombot_state.action_frame == 2:
                self.interruptible = False
                if self.direction == MULTISHINE_DIRECTION.FORWARD:
                    controller.tilt_analog(Button.BUTTON_MAIN, int(custombot_state.facing), .5) #advancing JC shine
                elif self.direction == MULTISHINE_DIRECTION.BACK:
                    controller.tilt_analog(Button.BUTTON_MAIN, int(not custombot_state.facing), .5) #retreating JC shine
                else:
                    controller.empty_input()
                return
            if custombot_state.action_frame == 1:
                self.interruptible = True
                controller.empty_input()
                return

        isInShineStart = (custombot_state.action == Action.DOWN_B_STUN or \
            custombot_state.action == Action.DOWN_B_GROUND_START or \
            custombot_state.action == Action.DOWN_B_GROUND)

        #Jump out of shine
        if isInShineStart and custombot_state.action_frame >= 3 and custombot_state.on_ground:
            controller.press_button(Button.BUTTON_Y)
            self.interruptible = False
            return

        if custombot_state.action == Action.DOWN_B_GROUND:
            controller.press_button(Button.BUTTON_Y)
            self.interruptible = False
            return

        # Catchall
        self.interruptible = True
        controller.empty_input()
