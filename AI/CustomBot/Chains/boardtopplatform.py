import melee
import random
from Chains.chain import Chain
from melee.enums import Action, Button

#for now, just a clone of boardsideplatform so that custombot compiles and runs
class BoardTopPlatform(Chain):
    def __init__(self, right_platform, attack=True):
        self.right_platform = right_platform
        self.interruptible = True
        self.attack = attack

    def step(self, gamestate, custombot_state, opponent_state):
        if self.logger:
            self.logger.log("Notes", " right side platform: " + str(self.right_platform) + " ", concat=True)

        platform_center = 0
        platform_height, platform_left, platform_right = melee.side_platform_position(self.right_platform, gamestate.stage)
        if platform_height is not None:
            platform_center = (platform_left + platform_right) / 2

        top_platform_height, _, _ = melee.top_platform_position(gamestate.stage)

        # Where to dash dance to
        pivot_point = platform_center
        # If opponent is on the platform, get right under them
        if platform_left < opponent_state.position.x < platform_right:
            pivot_point = opponent_state.position.x

        # Unless we don't need to attack them, then it's safe to just board asap
        if not self.attack and (platform_left+2 < custombot_state.position.x < platform_right-2):
            pivot_point = custombot_state.position.x

        # If we're just using the side platform as a springboard, then go closer in than the middle
        if top_platform_height is not None and (opponent_state.position.y >= top_platform_height):
            if custombot_state.position.x > 0:
                pivot_point = platform_left + 8
            else:
                pivot_point = platform_right - 8

        # Don't run off the stage (mostly on Yoshis)
        pivot_point = max(-melee.stages.EDGE_GROUND_POSITION[gamestate.stage]+5, pivot_point)
        pivot_point = min(melee.stages.EDGE_GROUND_POSITION[gamestate.stage]-5, pivot_point)

        if custombot_state.on_ground:
            self.interruptible = True
            # If we're already on the platform, just do nothing. We shouldn't be here
            if custombot_state.position.y > 5:
                self.controller.release_all()
                return

        # Are we in position to jump?
        if (abs(custombot_state.position.x - pivot_point) < 5) and (platform_left+2 < custombot_state.position.x < platform_right-2):
            # Do pivot jumps to prevent too much unpredictable horizontal movement
            if custombot_state.action == Action.TURNING:
                self.interruptible = False
                self.controller.press_button(melee.Button.BUTTON_Y)
                return

        # If we're crouching, keep holding Y
        if custombot_state.action == Action.KNEE_BEND:
            # Jump toward the pivot point, if we're far away
            if abs(custombot_state.position.x - pivot_point) > 10:
                self.controller.tilt_analog(melee.Button.BUTTON_MAIN, int(custombot_state.position.x < pivot_point), 0)
            else:
                self.controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0.5)

            self.controller.press_button(melee.Button.BUTTON_Y)
            self.interruptible = False
            return

        # Jump out of shine
        if custombot_state.action in [Action.DOWN_B_AIR]:
            self.controller.press_button(melee.Button.BUTTON_Y)
            return

        # Can we shine our opponent right now, while we're in the air?
        foxshinerange = 11.8
        shineable = custombot_state.action in [Action.JUMPING_FORWARD, Action.JUMPING_BACKWARD]
        if self.attack and shineable and gamestate.distance < foxshinerange:
            self.controller.press_button(melee.Button.BUTTON_B)
            self.controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
            return

        # Waveland down
        aerials = [Action.NAIR, Action.FAIR, Action.UAIR, Action.BAIR, Action.DAIR]
        if custombot_state.ecb.bottom.y + custombot_state.position.y > platform_height and custombot_state.action not in aerials:
            self.interruptible = True
            self.controller.press_button(melee.Button.BUTTON_L)
            # When we're choosing to not attack, just get close to the opponent if we're already
            x = int(custombot_state.position.x < opponent_state.position.x) * 0.8
            if not self.attack and abs(custombot_state.position.x - opponent_state.position.x) < 10:
                x = 0.5
            self.controller.tilt_analog(melee.Button.BUTTON_MAIN, x, 0)
            return

        # Don't jump into Peach's dsmash or SH early dair spam
        dsmashactive = opponent_state.action == Action.DOWNSMASH and opponent_state.action_frame <= 22
        if shineable and (opponent_state.action == Action.DAIR or dsmashactive):
            self.interruptible = True
            self.controller.press_button(melee.Button.BUTTON_L)
            self.controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
            return

        # If we see the opponent jump, they cannot protect themselves from uair.
        # Does not look for KNEE_BEND because custombot needs to discern between SH and FH
        y_afternineframes = opponent_state.position.y
        gravity = self.framedata.characterdata[opponent_state.character]["Gravity"]
        y_speed = opponent_state.speed_y_self
        for i in range(1,10):
            y_afternineframes += y_speed
            y_speed -= gravity


        aerialsminusdair = [Action.NAIR, Action.FAIR, Action.UAIR, Action.BAIR]
        if shineable and (opponent_state.action in [Action.JUMPING_FORWARD, Action.JUMPING_BACKWARD] or opponent_state.action in aerialsminusdair) and y_afternineframes < 50:
            self.controller.press_button(melee.Button.BUTTON_A)
            self.controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 1)
            return

        # Last resort, just dash at the center of the platform
        if custombot_state.on_ground:
            self.interruptible = True
            #If we're starting the turn around animation, keep pressing that way or
            #   else we'll get stuck in the slow turnaround
            if custombot_state.action == Action.TURNING and custombot_state.action_frame == 1:
                return

            #Dash back, since we're about to start running
            if custombot_state.action == Action.DASHING and custombot_state.action_frame >= 11:
                self.controller.tilt_analog(melee.Button.BUTTON_MAIN, int(not custombot_state.facing), .5)
                return
            else:
                self.controller.tilt_analog(melee.Button.BUTTON_MAIN, int(custombot_state.position.x < pivot_point), .5)
                return
        # Mash analog L presses to L-cancel if custombot is throwing out an aerial
        elif not custombot_state.on_ground and custombot_state.action in aerials:
            self.interruptible = False
            if gamestate.frame % 2 == 0:
                self.controller.press_shoulder(Button.BUTTON_L, 1)
            else:
                self.controller.press_shoulder(Button.BUTTON_L, 0)
            return
        else:
            self.controller.empty_input()
