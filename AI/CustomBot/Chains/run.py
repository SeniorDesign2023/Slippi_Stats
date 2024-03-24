import melee
from melee.enums import Action, Button
from Chains.chain import Chain

class Run(Chain):
    def __init__(self, rundirection):
        self.rundirection = rundirection

    def step(self, gamestate, custombot_state, opponent_state):

        #If we're starting the turn around animation, keep pressing that way or
        #   else we'll get stuck in the slow turnaround
        if custombot_state.action == Action.TURNING and custombot_state.action_frame == 1:
            return

        controller = self.controller

        if custombot_state.action in [Action.SHIELD_REFLECT, Action.SHIELD_STUN]:
            self.interruptible = True
            controller.release_all()
            return

        """ Different characters will probably need different ranges but this is for Fox. """
        #We need to input a jump to wavedash out of these states if dash/run gets called while in one of these states, or else we get stuck
        jcstates = [Action.DOWN_B_GROUND_START, Action.DOWN_B_GROUND, Action.TURNING_RUN]
        if (custombot_state.action in jcstates) or (custombot_state.action == Action.TURNING and custombot_state.action_frame in range(2,12)):
            self.controller.press_button(Button.BUTTON_Y)
            return

        #If the past action didn't work because custombot tried to press Y on a bad frame and continues holding Y, he needs to let go of Y and try again
        if controller.prev.button[Button.BUTTON_Y] and custombot_state.action in jcstates:
            self.controller.release_button(Button.BUTTON_Y)
            self.controller.press_button(Button.BUTTON_X)
            return

        #If the past action didn't work because custombot tried to press Y on a bad frame and continues holding Y, he should let go of X
        if controller.prev.button[Button.BUTTON_X] and custombot_state.action in jcstates:
            self.controller.release_button(Button.BUTTON_X)
            return

        # Airdodge for the wavedash
        jumping = [Action.JUMPING_ARIAL_FORWARD, Action.JUMPING_ARIAL_BACKWARD]
        jumpcancel = (custombot_state.action == Action.KNEE_BEND) and (custombot_state.action_frame == 3)
        if jumpcancel or custombot_state.action in jumping:
            self.controller.press_button(Button.BUTTON_L)
            onleft = custombot_state.position.x < opponent_state.position.x
            # Normalize distance from (0->1) to (0.5 -> 1)
            x = 1
            if onleft != False:
                x = -x
            self.controller.tilt_analog(Button.BUTTON_MAIN, x, 0.35)
            return

        # Otherwise, run in the specified direction
        x = 0
        if self.rundirection:
            x = 1
        controller.tilt_analog(Button.BUTTON_MAIN, x, .5)
        self.interruptible = True
