import melee
from melee.enums import Action, Button, Character
from Chains.chain import Chain

# Grab the edge
class Grabedge(Chain):
    def __init__(self, wavedash=True):
        self.wavedash = wavedash

    def step(self, gamestate, custombot_state, opponent_state):
        controller = self.controller

        # Moved this here from constructor.
        #   It should be fine, but let's keep an eye out for if this breaks
        edge_x = melee.stages.EDGE_GROUND_POSITION[gamestate.stage]
        if opponent_state.position.x < 0:
            edge_x = -edge_x
        edgedistance = abs(edge_x - custombot_state.position.x)
        if edgedistance > 15:
            self.wavedash = False
        if edgedistance < 2:
            self.wavedash = False

        # Where is the edge that we're going to?
        edge_x = melee.stages.EDGE_GROUND_POSITION[gamestate.stage]
        if opponent_state.position.x < 0:
            edge_x = -edge_x

        # If we're on the edge, then we're done here, end the chain
        if custombot_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING, Action.SWORD_DANCE_3_LOW]:
            self.interruptible = True
            controller.empty_input()
            return

        # If we're in spotdodge, do nothing
        if custombot_state.action == Action.SPOTDODGE:
            self.interruptible = True
            controller.empty_input()
            return

        # If we're stuck wavedashing, just hang out and do nothing
        if custombot_state.action == Action.LANDING_SPECIAL:
            self.interruptible = False
            controller.empty_input()
            return

        #If we're walking, stop for a frame
        #Also, if we're shielding, don't try to dash. We will accidentally roll
        if custombot_state.action == Action.WALK_SLOW or \
            custombot_state.action == Action.WALK_MIDDLE or \
            custombot_state.action == Action.WALK_FAST or \
            custombot_state.action == Action.SHIELD_START or \
            custombot_state.action == Action.SHIELD_REFLECT or \
            custombot_state.action == Action.SHIELD:
                self.interruptible = True
                controller.empty_input()
                return

        facinginwards = custombot_state.facing == (custombot_state.position.x < 0)
        if custombot_state.action == Action.TURNING and custombot_state.action_frame == 1:
            facinginwards = not facinginwards

        edgedistance = abs(edge_x - custombot_state.position.x)
        turnspeed = abs(custombot_state.speed_ground_x_self)
        # If we turn right now, what will our speed be?
        if custombot_state.action == Action.DASHING:
            turnspeed = (abs(custombot_state.speed_ground_x_self) - 0.32) / 4
        slidedistance = self.framedata.slide_distance(custombot_state, turnspeed, 7)
        closetoedge = edgedistance < slidedistance

        # Do a wavedash off
        if self.wavedash and not custombot_state.off_stage:
            self.interruptible = False
            if custombot_state.action == Action.KNEE_BEND and custombot_state.action_frame >= 3:
                controller.press_button(Button.BUTTON_L)
                controller.release_button(Button.BUTTON_Y)
                controller.tilt_analog(melee.Button.BUTTON_MAIN, int(not custombot_state.facing), 0.2)
                return
            if facinginwards:
                if controller.prev.button[Button.BUTTON_Y]:
                    controller.release_button(Button.BUTTON_Y)
                    return
                else:
                    controller.press_button(Button.BUTTON_Y)
                    return
            else:
                # Dash inwards to turn
                controller.tilt_analog(melee.Button.BUTTON_MAIN, int(not custombot_state.facing), 0.5)
                return

        # This is actually shine turnaround
        if custombot_state.action == Action.MARTH_COUNTER:
            self.interruptible = False
            controller.empty_input()
            return

        """ Fox shine """
        # If we're in the shine, but too high, just wait
        if custombot_state.action in [Action.SWORD_DANCE_4_MID_AIR, Action.SWORD_DANCE_4_LOW_AIR] \
                and -10 < custombot_state.position.y and edgedistance < 10:
            self.interruptible = False
            controller.empty_input()
            return

        # Fastfall, but only once
        if custombot_state.action == Action.FALLING:
            self.interruptible = False

            sing = (opponent_state.character == Character.JIGGLYPUFF) and opponent_state.action in [Action.SHINE_RELEASE_AIR, Action.DOWN_B_AIR]

            """ Fox shine """
            # Should we shine?
            canhit = gamestate.distance < 11.8 and (opponent_state.invulnerability_left == 0) and not sing and opponent_state.action != Action.EDGE_HANGING
            if (custombot_state.position.y < -15) or canhit:
                controller.press_button(Button.BUTTON_B)
                controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
                return

            # Fastfall speed is 3.4, but we need a little wiggle room
            if custombot_state.speed_y_self > -3.35:
                controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
            else:
                # DI in to the opponent
                x = 0
                if custombot_state.position.x < opponent_state.position.x:
                    x = 1
                controller.tilt_analog(melee.Button.BUTTON_MAIN, x, 0.5)
            return

        """ Fox shine """
        # Shine turnaround
        if custombot_state.action == Action.DOWN_B_STUN and not facinginwards:
            self.interruptible = False
            controller.tilt_analog(melee.Button.BUTTON_MAIN, int(not custombot_state.facing), .5)
            return

        """ Fox shine """
        # Jump out of shine
        if custombot_state.action == Action.DOWN_B_AIR and facinginwards:
            self.interruptible = False
            controller.release_button(Button.BUTTON_B)
            controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0.5)
            if controller.prev.button[Button.BUTTON_Y]:
                controller.release_button(Button.BUTTON_Y)
                return
            else:
                controller.press_button(Button.BUTTON_Y)
                return

        # Firefox to grab edge
        if custombot_state.action == Action.JUMPING_ARIAL_FORWARD:
            # Must be between 0 and -10
            inxrange = -10 < (abs(edge_x) - abs(custombot_state.position.x)) < 0
            if -15 < custombot_state.position.y < -5 and inxrange:
                self.interruptible = False
                controller.press_button(Button.BUTTON_B)
                controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 1)
                return
            else:
                self.interruptible = False
                controller.empty_input()
                return

        # Pivot slide
        if custombot_state.action == Action.TURNING and facinginwards and closetoedge:
            self.interruptible = False
            controller.empty_input()
            return

        # Do the turn
        if custombot_state.action == Action.DASHING and closetoedge:
            self.interruptible = False
            controller.tilt_analog(melee.Button.BUTTON_MAIN, int(not custombot_state.facing), .5)
            return

        #If we're starting the turn around animation, keep pressing that way or
        #   else we'll get stuck in the slow turnaround
        if custombot_state.action == Action.TURNING and custombot_state.action_frame == 1:
            self.interruptible = True
            return

        #Dash back, since we're about to start running
        if custombot_state.action == Action.DASHING and custombot_state.action_frame >= 11:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, int(not custombot_state.facing), .5)
            self.interruptible = True
            return

        #We can't dash IMMEDIATELY after landing. So just chill for a bit
        if custombot_state.action == Action.LANDING and custombot_state.action_frame < 2:
            self.interruptible = True
            controller.empty_input()
            return

        #Are we outside the given radius of dash dancing?
        if custombot_state.position.x < edge_x:
            self.interruptible = True
            if not self.wavedash:
                self.interruptible = False
            controller.tilt_analog(melee.Button.BUTTON_MAIN, 1, .5)
            return

        if custombot_state.position.x > edge_x:
            self.interruptible = True
            if not self.wavedash:
                self.interruptible = False
            controller.tilt_analog(melee.Button.BUTTON_MAIN, 0, .5)
            return

        #Keep running the direction we're going
        self.interruptible = True
        controller.tilt_analog(melee.Button.BUTTON_MAIN, int(not custombot_state.facing), .5)
        return
