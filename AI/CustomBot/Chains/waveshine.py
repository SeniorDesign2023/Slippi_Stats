import melee
import random
from melee.enums import Action, Button
from Chains.chain import Chain

# Shine, then wavedash
class Waveshine(Chain):
    # Distance argument is a multiplier to how far we'll wavedash
    # 0 is straight in place
    # 1 is max distance
    def __init__(self, distance=1):
        self.hasshined = False
        self.distance = distance
        self.frames_spent = 0

    def step(self, gamestate, custombot_state, opponent_state):
        controller = self.controller
        self.frames_spent += 1

        # This is here to break the custombot ditto deadlock
        if self.frames_spent > 180 and random.randint(0, 100) < 20:
            self.interruptible = True
            controller.empty_input()
            return

        shineablestates = [Action.TURNING, Action.STANDING, Action.WALK_SLOW, Action.WALK_MIDDLE, \
            Action.WALK_FAST, Action.EDGE_TEETERING_START, Action.EDGE_TEETERING, Action.CROUCHING, \
            Action.RUNNING, Action.RUN_BRAKE, Action.CROUCH_START, Action.CROUCH_END, Action.SHIELD_RELEASE]

        jcshine = (custombot_state.action == Action.KNEE_BEND) and (custombot_state.action_frame == 3)
        lastdashframe = (custombot_state.action == Action.DASHING) and (custombot_state.action_frame == 12)
        landing_over = (custombot_state.action == Action.LANDING) and (custombot_state.action_frame >= 4)

        # If we're in the air high, don't try to waveshine
        if custombot_state.action == Action.DOWN_B_AIR:
            if custombot_state.position.y > 5:
                self.interruptible = True
                controller.empty_input()
                return
            else:
                self.interruptible = False
                controller.empty_input()
                return

        # If somehow we are off stage, give up immediately
        if custombot_state.off_stage:
            self.interruptible = True
            controller.empty_input()
            return

        # Jump out of shield if we didn't powershield this hit
        if custombot_state.action == Action.SHIELD_RELEASE and not gamestate.custom["powershielded_last"]:
            self.interruptible = False
            controller.press_button(Button.BUTTON_Y)
            return

        # Do the shine if we can
        if not self.hasshined and ((custombot_state.action in shineablestates) or lastdashframe or jcshine or landing_over):
            self.interruptible = False
            controller.press_button(Button.BUTTON_B)
            controller.tilt_analog(Button.BUTTON_MAIN, .5, 0)
            self.hasshined = True
            return

        # Alternative shine. Happens when we clank. Do the shine again!
        if jcshine and gamestate.distance < 11.8 and opponent_state.hitlag_left == 0 and opponent_state.hitstun_frames_left == 0:
            self.interruptible = False
            controller.press_button(Button.BUTTON_B)
            controller.tilt_analog(Button.BUTTON_MAIN, .5, 0)
            self.hasshined = True
            return

        # If we're in the early knee bend frames, just hang on and wait
        if (custombot_state.action == Action.KNEE_BEND) and (custombot_state.action_frame < 3):
            controller.empty_input()
            return

        # Pivot. You can't shine from a dash animation. So make it a pivot
        if custombot_state.action == Action.DASHING:
            # Turn around
            self.interruptible = True
            controller.release_button(Button.BUTTON_B)
            controller.tilt_analog(Button.BUTTON_MAIN, int(not custombot_state.facing), .5)
            #controller.press_button(Button.BUTTON_Y) #attempt JC shine instead of pivot shine
            return

        # In the off-chance waveshine.py gets called during GRAB_WAIT, down-throw
        if custombot_state.action == Action.GRAB_WAIT:
            controller.tilt_analog(Button.BUTTON_MAIN, .5, 0)
            if self.controller.prev.main_stick[1] == 0:
                controller.empty_input()
            return

        isInShineStart = custombot_state.action in [Action.DOWN_B_GROUND_START, Action.DOWN_B_GROUND]
        needsJC = custombot_state.action in [Action.SHIELD, Action.TURNING_RUN] #Added TURNING_RUN in case waveshine gets called during that animation

        # Jump out of shield, turning run, or tilt turn
        if needsJC or (custombot_state.action == Action.TURNING and custombot_state.action_frame in range(2,12)): #
            if controller.prev.button[Button.BUTTON_Y]:
                controller.empty_input()
                return
            self.interruptible = False
            controller.press_button(Button.BUTTON_Y)
            return

        # Jump out of shine
        if isInShineStart:
            self.interruptible = False
            if custombot_state.action_frame >= 3:
                controller.press_button(Button.BUTTON_Y)
                return
            else:
                controller.empty_input()
                return

        # We shouldn't need these. It's just there in case we miss the knee bend somehow
        jumping = [Action.JUMPING_ARIAL_FORWARD, Action.JUMPING_ARIAL_BACKWARD]

        # Airdodge back down into the stage
        if jcshine or custombot_state.action in jumping:
            self.interruptible = False
            controller.press_button(Button.BUTTON_L)
            # Always wavedash the direction opponent is moving
            opponentspeed = opponent_state.speed_x_attack + opponent_state.speed_ground_x_self
            direction = opponentspeed > 0
            onleft = custombot_state.position.x < opponent_state.position.x
            if abs(opponentspeed) < 0.01:
                direction = onleft

            # Unless we're RIGHT on top of the edge. In which case the only safe wavedash is back on the stage
            edge_x = melee.stages.EDGE_GROUND_POSITION[gamestate.stage]
            if opponent_state.position.x < 0:
                edge_x = -edge_x
            edgedistance = abs(edge_x - custombot_state.position.x)
            if edgedistance < 0.5:
                direction = custombot_state.position.x < 0

            # Don't waveshine off the stage facing away
            facinginwards = custombot_state.facing == (custombot_state.position.x < 0)
            moving_out = direction == (0 < custombot_state.position.x)
            if edgedistance < 18.5 and moving_out and not facinginwards:
                self.distance = 0

            # Normalize distance from (0->1) to (-0.5 -> 0.5)
            delta = (self.distance / 2) # 0->0.5
            if not direction:
                delta = -delta
            controller.tilt_analog(Button.BUTTON_MAIN, 0.5 + delta, .35)
            return

        # If we're sliding and have shined, then we're all done here
        if custombot_state.action == Action.LANDING_SPECIAL: #removed and self.hasshined
            self.interruptible = True
            controller.empty_input()
            return

        if custombot_state.action in [Action.SWORD_DANCE_4_MID_AIR, Action.SWORD_DANCE_4_LOW_AIR]:
            self.interruptible = False
        else:
            self.interruptible = True

        controller.empty_input()
