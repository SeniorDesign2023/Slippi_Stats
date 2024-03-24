import melee
import Chains
import math
from melee.enums import Action, Button, Character
from Tactics.tactic import Tactic
from Chains.smashattack import SMASH_DIRECTION
from Chains.shffl import SHFFL_DIRECTION
from Chains.shieldaction import SHIELD_ACTION


""" This file also is mostly just for setting up shine."""
class Punish(Tactic):
    # How many frames do we have to work with for the punish
    def framesleft(opponent_state, framedata, custombot_state):
        # For some dumb reason, the game shows the standing animation as having a large hitstun
        #   manually account for this
        if opponent_state.action == Action.STANDING:
            return 1

        # Opponent's shield is broken, opponent is resting Puff.
        restingpuff = opponent_state.character == Character.JIGGLYPUFF and opponent_state.action == Action.MARTH_COUNTER
        if restingpuff or opponent_state.action in [Action.SHIELD_BREAK_STAND_U, Action.SHIELD_BREAK_TEETER]:
            return 249 - opponent_state.action_frame

        # Don't try to punish Samus knee_bend, because they will go into UP_B and it has invulnerability
        if opponent_state.action == Action.KNEE_BEND and opponent_state.character == Character.SAMUS:
            return 0

        # It's unsafe to shine an opponent lying on a platform. Just wait for them to act instead
        if opponent_state.position.y > 5 and opponent_state.action in [Action.LYING_GROUND_UP, Action.LYING_GROUND_DOWN]:
            return 0

        # Samus UP_B invulnerability
        if opponent_state.action in [Action.SWORD_DANCE_3_MID, Action.SWORD_DANCE_3_LOW] and \
                opponent_state.character == Character.SAMUS and opponent_state.action_frame <= 5:
            return 0

        # Bowser up-b invulnerability
        if opponent_state.action in [Action.SWORD_DANCE_2_HIGH_AIR, Action.DOWN_B_GROUND_START] and \
                opponent_state.character == Character.BOWSER and opponent_state.action_frame <= 4:
            return 0

        # Samus morph ball
        if opponent_state.character == Character.SAMUS and opponent_state.action in [Action.SWORD_DANCE_4_MID, Action.SWORD_DANCE_4_HIGH, Action.NEUTRAL_B_CHARGING]:
            return 1

        # Pikachu skull bash, thunder
        if opponent_state.action in [Action.NEUTRAL_B_FULL_CHARGE, Action.NEUTRAL_B_ATTACKING, Action.SWORD_DANCE_2_MID_AIR, Action.SWORD_DANCE_2_HIGH_AIR] and \
                opponent_state.character == Character.PIKACHU:
            return 1

        # Jigglypuff jumps
        if opponent_state.character == Character.JIGGLYPUFF and opponent_state.action in \
                [Action.LASER_GUN_PULL, Action.NEUTRAL_B_CHARGING, Action.NEUTRAL_B_ATTACKING, Action.NEUTRAL_B_FULL_CHARGE, Action.WAIT_ITEM]:
            return 1

        if opponent_state.character == Character.SHEIK:
            if opponent_state.action in [Action.SWORD_DANCE_4_HIGH, Action.SWORD_DANCE_1_AIR]:
                return 17 - opponent_state.action_frame
            if opponent_state.action in [Action.SWORD_DANCE_4_LOW, Action.SWORD_DANCE_2_HIGH_AIR] and opponent_state.action_frame <= 21:
                return 0

        # Shine wait
        if opponent_state.character in [Character.FOX, Character.FALCO]:
            if opponent_state.action in [Action.SWORD_DANCE_2_MID_AIR, Action.SWORD_DANCE_3_HIGH_AIR, Action.SWORD_DANCE_3_LOW_AIR]:
                return 3

        if opponent_state.action == Action.LOOPING_ATTACK_MIDDLE:
            return 1

        if opponent_state.character == Character.SHEIK and opponent_state.action == Action.SWORD_DANCE_2_HIGH:
            return 1

        # Opponent is in a lag state
        if opponent_state.action in [Action.UAIR_LANDING, Action.FAIR_LANDING, \
                Action.DAIR_LANDING, Action.BAIR_LANDING, Action.NAIR_LANDING]:
            # TODO: DO an actual lookup to see how many frames this is
            return 8 - (opponent_state.action_frame // 3)

        # Is opponent attacking?
        if framedata.is_attack(opponent_state.character, opponent_state.action):
            # What state of the attack is the opponent in?
            # Windup / Attacking / Cooldown
            attackstate = framedata.attack_state(opponent_state.character, opponent_state.action, opponent_state.action_frame)
            if attackstate == melee.enums.AttackState.WINDUP:
                # Don't try to punish opponent in windup when they're invulnerable
                if opponent_state.invulnerability_left > 0:
                    return 0
                # Don't try to punish standup attack windup
                if opponent_state.action in [Action.GROUND_ATTACK_UP, Action.GETUP_ATTACK]:
                    return 0
                frame = framedata.first_hitbox_frame(opponent_state.character, opponent_state.action)
                # Account for boost grab. Dash attack can cancel into a grab
                if opponent_state.action == Action.DASH_ATTACK:
                    return min(6, frame - opponent_state.action_frame - 1)
                return max(0, frame - opponent_state.action_frame - 1)
            if attackstate == melee.enums.AttackState.ATTACKING and custombot_state.action == Action.SHIELD_RELEASE:
                if opponent_state.action in [Action.NAIR, Action.FAIR, Action.UAIR, Action.BAIR, Action.DAIR]:
                    return 7
                elif opponent_state.character == Character.PEACH and opponent_state.action in [Action.NEUTRAL_B_FULL_CHARGE, Action.WAIT_ITEM, Action.NEUTRAL_B_ATTACKING, Action.NEUTRAL_B_CHARGING, Action.NEUTRAL_B_FULL_CHARGE_AIR]:
                    return 6
                else:
                    return framedata.frame_count(opponent_state.character, opponent_state.action) - opponent_state.action_frame
            if attackstate == melee.enums.AttackState.ATTACKING and custombot_state.action != Action.SHIELD_RELEASE:
                return 0
            if attackstate == melee.enums.AttackState.COOLDOWN:
                frame = framedata.iasa(opponent_state.character, opponent_state.action)
                return max(0, frame - opponent_state.action_frame)
        if framedata.is_roll(opponent_state.character, opponent_state.action):
            frame = framedata.last_roll_frame(opponent_state.character, opponent_state.action)
            return max(0, frame - opponent_state.action_frame)

        # Opponent is in hitstun
        if opponent_state.hitstun_frames_left > 0:
            # Special case here for lying on the ground.
            #   For some reason, the hitstun count is totally wrong for these actions
            if opponent_state.action in [Action.LYING_GROUND_UP, Action.LYING_GROUND_DOWN]:
                return 1

            # If opponent is in the air, we need to cap the return at when they will hit the ground
            if opponent_state.position.y > .02 or not opponent_state.on_ground:
                # When will they land?
                speed = opponent_state.speed_y_attack + opponent_state.speed_y_self
                height = opponent_state.position.y
                gravity = framedata.characterdata[opponent_state.character]["Gravity"]
                termvelocity = framedata.characterdata[opponent_state.character]["TerminalVelocity"]
                count = 0
                while height > 0:
                    height += speed
                    speed -= gravity
                    speed = max(speed, -termvelocity)
                    count += 1
                    # Shortcut if we get too far
                    if count > 120:
                        break
                return min(count, opponent_state.hitstun_frames_left)

            return opponent_state.hitstun_frames_left

        # Exception for Jigglypuff rollout
        #   The action frames are weird for this action, and Jiggs is actionable during it in 1 frame
        if opponent_state.character == Character.JIGGLYPUFF and \
                opponent_state.action in [Action.SWORD_DANCE_1, Action.NEUTRAL_B_FULL_CHARGE_AIR, Action.SWORD_DANCE_4_LOW, \
                Action.SWORD_DANCE_4_MID, Action.SWORD_DANCE_3_LOW]:
            return 1

        # Opponent is in a B move
        if framedata.is_bmove(opponent_state.character, opponent_state.action):
            return framedata.frame_count(opponent_state.character, opponent_state.action) - opponent_state.action_frame

        return 1

    # Static function that returns whether we have enough time to run in and punish,
    # given the current gamestate. Either a shine or upsmash
    def canpunish(custombot_state, opponent_state, gamestate, framedata):

        restingpuff = opponent_state.character == Character.JIGGLYPUFF and opponent_state.action == Action.MARTH_COUNTER
        if restingpuff or opponent_state.action in [Action.SHIELD_BREAK_TEETER, Action.SHIELD_BREAK_STAND_U]:
            return True

        # Wait until the later shieldbreak animations to punish, sometimes custombot usmashes too early
        if opponent_state.action in [Action.SHIELD_BREAK_FLY, Action.SHIELD_BREAK_DOWN_U]:
            return False

        # Can't punish opponent in shield
        shieldactions = [Action.SHIELD_START, Action.SHIELD, Action.SHIELD_RELEASE, \
            Action.SHIELD_STUN, Action.SHIELD_REFLECT]
        if opponent_state.action in shieldactions:
            return False

        if custombot_state.off_stage or opponent_state.off_stage:
            return False

        firefox = opponent_state.action == Action.SWORD_DANCE_3_LOW and opponent_state.character in [Character.FOX, Character.FALCO]
        if firefox and opponent_state.position.y > 15:
            return False

        left = Punish.framesleft(opponent_state, framedata, custombot_state)
        # Will our opponent be invulnerable for the entire punishable window?
        if left <= opponent_state.invulnerability_left:
            return False

        if left < 1:
            return False

        if framedata.is_roll(opponent_state.character, opponent_state.action):
            return True

        # Don't punish if the vertical difference is too great.
        if abs(custombot_state.position.y - opponent_state.position.y) > 10:
            return False

        # Can we shine right now without any movement?
        shineablestates = [Action.TURNING, Action.STANDING, Action.WALK_SLOW, Action.WALK_MIDDLE, \
            Action.WALK_FAST, Action.EDGE_TEETERING_START, Action.EDGE_TEETERING, Action.CROUCHING, \
            Action.RUNNING]

        foxshinerange = 9.9
        if gamestate.distance < foxshinerange and custombot_state.action in shineablestates:
            return True

        foxrunspeed = 2.2
        #TODO: Subtract from this time spent turning or transitioning
        # Assume that we can run at max speed toward our opponent
        # We can only run for framesleft-1 frames, since we have to spend at least one attacking
        potentialrundistance = (left-1) * foxrunspeed

        if gamestate.distance - potentialrundistance < foxshinerange:
            return True
        return False

    def step(self, gamestate, custombot_state, opponent_state):
        self._propagate  = (gamestate, custombot_state, opponent_state)

        # Can we charge an upsmash right now?
        framesleft = Punish.framesleft(opponent_state, self.framedata, custombot_state)
        endposition = opponent_state.position.x + self.framedata.slide_distance(opponent_state, opponent_state.speed_x_attack, framesleft)
        slidedistance = self.framedata.slide_distance(custombot_state, custombot_state.speed_ground_x_self, framesleft)
        custombot_endposition = slidedistance + custombot_state.position.x

        if self.logger:
            self.logger.log("Notes", "framesleft: " + str(framesleft) + " ", concat=True)

        #If we can't interrupt the chain, just continue it
        if self.chain != None and not self.chain.interruptible:
            self.chain.step(gamestate, custombot_state, opponent_state)
            return

        # TODO: May be missing some relevant inactionable states
        inactionablestates = [Action.THROW_DOWN, Action.THROW_UP, Action.THROW_FORWARD, Action.THROW_BACK, Action.UAIR_LANDING, Action.FAIR_LANDING, \
                Action.DAIR_LANDING, Action.BAIR_LANDING, Action.NAIR_LANDING, Action.UPTILT, Action.DOWNTILT, Action.UPSMASH, \
                Action.DOWNSMASH, Action.FSMASH_MID, Action.FTILT_MID, Action.FTILT_LOW, Action.FTILT_HIGH]
        if custombot_state.action in inactionablestates:
            self.pickchain(Chains.Nothing)
            return

        # Attempt powershield action, note, we don't have a way of knowing for sure if we hit a physical PS
        opponentxvelocity = (opponent_state.speed_air_x_self + opponent_state.speed_ground_x_self + opponent_state.speed_x_attack)
        opponentyvelocity = (opponent_state.speed_y_attack + opponent_state.speed_y_self)
        opponentonright = opponent_state.position.x > custombot_state.position.x

        if custombot_state.action == Action.SHIELD_RELEASE and gamestate.custom["powershielded_last"]:
            # Sometimes shine OOS will miss because the oppponent is still rising with an aerial. Peach's float can be hard to shine OOS.
            if opponent_state.position.y >= 11.5:
                # If the opponent is above a certain height and still rising, or outside of a small x range, don't shine, just WD.
                if opponentyvelocity >= 0 or abs(opponent_state.position.x - custombot_state.position.x) > 6:
                    self.pickchain(Chains.Wavedash)
                    return
                # Shine otherwise (i.e. if they're above a certain height but falling towards us or in a certain x range)
                else:
                    self.pickchain(Chains.ShieldAction, [SHIELD_ACTION.PSSHINE])
                    return
            # If the opponent is closer to the ground
            else:
                # PS shine if the opponent is drifting towards us
                if gamestate.distance <= 14 and not (opponentxvelocity > 0) == opponentonright:
                    self.pickchain(Chains.ShieldAction, [SHIELD_ACTION.PSSHINE])
                    return
                # PS shine if the opponent is drifting away from us
                elif gamestate.distance <= 13 and (opponentxvelocity > 0) == opponentonright:
                    self.pickchain(Chains.ShieldAction, [SHIELD_ACTION.PSSHINE])
                    return
                else:
                    self.pickchain(Chains.Wavedash)
                    return

        shieldactions = [Action.SHIELD_START, Action.SHIELD, Action.SHIELD_RELEASE, \
            Action.SHIELD_STUN, Action.SHIELD_REFLECT]

        # JC Shine OOS if possible/necessary
        if 4 <= framesleft <= 7:
            # Numbers are adjusted from PS shine to be more conservative due to longer startup.
            if opponent_state.position.y >= 11:
                if opponentyvelocity >= 0 or abs(opponent_state.position.x - custombot_state.position.x) > 5:
                    if custombot_state.action in shieldactions:
                        self.pickchain(Chains.Wavedash)
                        return
                else:
                    self.pickchain(Chains.Waveshine)
                    return
            else:
                if custombot_state.action in shieldactions and gamestate.distance <= 12.2 and not (opponentxvelocity > 0) == opponentonright and framesleft >= 4:
                    self.pickchain(Chains.Waveshine)
                    return
                if custombot_state.action in shieldactions and gamestate.distance <= 11.5 and (opponentxvelocity > 0) == opponentonright and framesleft >= 4:
                    self.pickchain(Chains.Waveshine)
                    return

        if framesleft <= 10:
            # If opponent is on a side platform and we're not
            on_main_platform = custombot_state.position.y < 1 and custombot_state.on_ground
            if opponent_state.position.y > 1 and opponent_state.on_ground and on_main_platform and gamestate.stage != melee.enums.Stage.FOUNTAIN_OF_DREAMS:
                self.pickchain(Chains.BoardSidePlatform, [opponent_state.position.x > 0])
                return

        # How many frames do we need for an upsmash?
        # It's 7 frames normally, plus some transition frames
        # 1 if in shield, shine, or dash/running
        framesneeded = 7
        shineactions = [Action.DOWN_B_STUN, Action.DOWN_B_GROUND_START, Action.DOWN_B_GROUND]
        runningactions = [Action.DASHING, Action.RUNNING]
        if custombot_state.action in shieldactions:
            framesneeded += 1
        if custombot_state.action in shineactions:
            framesneeded += 1
        if custombot_state.action in runningactions:
            framesneeded += 1

        endposition = opponent_state.position.x
        isroll = self.framedata.is_roll(opponent_state.character, opponent_state.action)
        slideoff = False

        # If we have the time....
        if framesneeded <= framesleft:
            # Calculate where the opponent will end up
            if opponent_state.hitstun_frames_left > 0:
                endposition = opponent_state.position.x + self.framedata.slide_distance(opponent_state, opponent_state.speed_x_attack, framesleft)

            if isroll:
                endposition = self.framedata.roll_end_position(opponent_state, gamestate.stage)

                initialrollmovement = 0
                facingchanged = False
                try:
                    initialrollmovement = self.framedata.framedata[opponent_state.character][opponent_state.action][opponent_state.action_frame]["locomotion_x"]
                    facingchanged = self.framedata.framedata[opponent_state.character][opponent_state.action][opponent_state.action_frame]["facing_changed"]
                except KeyError:
                    pass
                backroll = opponent_state.action in [Action.ROLL_BACKWARD, Action.GROUND_ROLL_BACKWARD_UP, \
                    Action.GROUND_ROLL_BACKWARD_DOWN, Action.BACKWARD_TECH]
                if not (opponent_state.facing ^ facingchanged ^ backroll):
                    initialrollmovement = -initialrollmovement

                speed = opponent_state.speed_x_attack + opponent_state.speed_ground_x_self - initialrollmovement
                endposition += self.framedata.slide_distance(opponent_state, speed, framesleft)

                # But don't go off the end of the stage
                if opponent_state.action in [Action.TECH_MISS_DOWN, Action.TECH_MISS_UP, Action.NEUTRAL_TECH]:
                    if abs(endposition) > melee.stages.EDGE_GROUND_POSITION[gamestate.stage]:
                        slideoff = True
                endposition = max(endposition, -melee.stages.EDGE_GROUND_POSITION[gamestate.stage])
                endposition = min(endposition, melee.stages.EDGE_GROUND_POSITION[gamestate.stage])


            # And we're in range...
            # Take our sliding into account
            slidedistance = self.framedata.slide_distance(custombot_state, custombot_state.speed_ground_x_self, framesleft)
            custombot_endposition = slidedistance + custombot_state.position.x

            # Do we have to consider character pushing?
            # Are we between the character's current and predicted position?
            if opponent_state.position.x < custombot_endposition < endposition or \
                    opponent_state.position.x > custombot_endposition > endposition:
                # Add a little bit of push distance along that path
                # 0.3 pushing for max of 16 frames
                #TODO Needs work here
                onleft = custombot_state.position.x < opponent_state.position.x
                if onleft:
                    custombot_endposition -= 4.8
                else:
                    custombot_endposition += 4.8

            if self.logger:
                self.logger.log("Notes", "endposition: " + str(endposition) + " ", concat=True)
                self.logger.log("Notes", "custombot_endposition: " + str(custombot_endposition) + " ", concat=True)

            facing = custombot_state.facing == (custombot_endposition < endposition)
            # Remember that if we're turning, the attack will come out the opposite way
            # On f1 of smashturn, custombot hasn't changed directions yet. On/after frame 2, it has. Tilt turn may be a problem.
            if custombot_state.action == Action.TURNING and custombot_state.action_frame == 1:
                facing = not facing

            # Get height of opponent at the targeted frame
            height = opponent_state.position.y
            firefox = opponent_state.action == Action.SWORD_DANCE_3_LOW and opponent_state.character in [Character.FOX, Character.FALCO]
            speed = opponent_state.speed_y_attack
            gravity = self.framedata.characterdata[opponent_state.character]["Gravity"]
            termvelocity = self.framedata.characterdata[opponent_state.character]["TerminalVelocity"]
            if not opponent_state.on_ground and not firefox:
                # Loop through each frame and count the distances
                for i in range(framesleft):
                    speed -= gravity
                    # We can't go faster than termvelocity downwards
                    speed = max(speed, -termvelocity)
                    height += speed

            distance = abs(endposition - custombot_endposition)
            x = 1
            # If we are really close to the edge, wavedash straight down
            if melee.stages.EDGE_GROUND_POSITION[gamestate.stage] - abs(custombot_state.position.x) < 3:
                x = 0
            # This makes custombot wavedash down if he shines the opponent outwards near the ledge.
            if abs(opponent_state.position.x) + 41 > melee.stages.EDGE_GROUND_POSITION[gamestate.stage] and abs(opponent_state.position.x) > abs(custombot_state.position.x):
                x = 0

            if not slideoff and distance < 14.5 and -5 < height < 8:
                # If custombot is in the corner and below usmash kill %, he will opt to waveshine them back towards center rather than usmash
                if abs(custombot_state.position.x) + 42 > melee.stages.EDGE_GROUND_POSITION[gamestate.stage] and opponent_state.percent < 89 and abs(opponent_state.position.x) < abs(custombot_state.position.x) and gamestate.distance < 9.9:
                    self.pickchain(Chains.Waveshine, [x])
                    return
                if facing:
                    self.chain = None
                    # Do the upsmash
                    # NOTE: If we get here, we want to delete the chain and start over
                    #   Since the amount we need to charge may have changed
                    self.pickchain(Chains.SmashAttack, [framesleft-framesneeded-1, SMASH_DIRECTION.UP])
                    return
                else:
                    # Do the bair if there's not enough time to wavedash, but we're facing away and out of shine range
                    #   This shouldn't happen often, but can if we're pushed away after powershield
                    offedge = melee.stages.EDGE_GROUND_POSITION[gamestate.stage] < abs(endposition)
                    if framesleft < 11 and not offedge:
                        if gamestate.distance <= 9.5 and opponent_state.percent < 89:
                            self.pickchain(Chains.Waveshine, [x])
                        else:
                            self.pickchain(Chains.Shffl, [SHFFL_DIRECTION.BACK])
                        return
                    # If we are running away from our opponent, just shine now
                    onright = opponent_state.position.x < custombot_state.position.x
                    if (custombot_state.speed_ground_x_self > 0) == onright and gamestate.distance <= 9.5:
                        self.pickchain(Chains.Waveshine, [x])
                        return
            # If we're not in attack range, and can't run, then maybe we can wavedash in
            #   Now we need more time for the wavedash. 10 frames of lag, and 3 jumping
            framesneeded = 13
            if framesneeded <= framesleft:
                if custombot_state.action in shieldactions or custombot_state.action in shineactions:
                    self.pickchain(Chains.Wavedash)
                    return

        # We can't smash our opponent, so let's just shine instead. Do we have time for that?
        #TODO: Wrap the shine range into a helper
        framesneeded = 1
        if custombot_state.action == Action.DASHING:
            framesneeded = 2
        if custombot_state.action in [Action.SHIELD_RELEASE, Action.SHIELD]:
            framesneeded = 4
        if custombot_state.action in [Action.DOWN_B_STUN, Action.DOWN_B_GROUND_START, Action.DOWN_B_GROUND]:
            framesneeded = 4

        foxshinerange = 9.9
        if custombot_state.action == Action.RUNNING:
            shinerange = 12.8
        if custombot_state.action == Action.DASHING:
            foxshinerange = 9.5

        # If we're teetering, and opponent is off stage, hit'm
        opponent_pushing = (gamestate.distance < 8) and abs(custombot_state.position.x) > abs(opponent_state.position.x)
        if custombot_state.action == Action.EDGE_TEETERING_START and not opponent_pushing:
            # Little baby wavedash
            self.pickchain(Chains.Waveshine, [0.2])
            return

        edgetooclose = (custombot_state.action == Action.EDGE_TEETERING_START or melee.stages.EDGE_GROUND_POSITION[gamestate.stage] - abs(custombot_state.position.x) < 5) or (custombot_state.action in [Action.RUNNING, Action.RUN_BRAKE, Action.CROUCH_START] and melee.stages.EDGE_GROUND_POSITION[gamestate.stage] - abs(custombot_state.position.x) < 10.5)
        if gamestate.distance < foxshinerange and not edgetooclose:
            if framesneeded <= framesleft:
                # Also, don't shine someone in the middle of a roll
                if (not isroll) or (opponent_state.action_frame < 3):
                    self.chain = None
                    # If we are facing towards the edge, don't wavedash off of it
                    #   Reduce the wavedash length
                    x = 1
                    # If we are really close to the edge, wavedash straight down
                    if melee.stages.EDGE_GROUND_POSITION[gamestate.stage] - abs(custombot_state.position.x) < 3:
                        x = 0
                    # Additionally, if the opponent is going to get sent offstage by the shine, wavedash down
                    # This makes custombot wavedash down if he shines the opponent outwards near the ledge. The gamestate.distance condition is there to ignore RUNNING situations where custombot/opponent are within 0.8 units where an extra frame causes them to switch sides.
                    if abs(opponent_state.position.x) + 41 > melee.stages.EDGE_GROUND_POSITION[gamestate.stage] and abs(opponent_state.position.x) > abs(custombot_state.position.x) and gamestate.distance > 0.8 and custombot_state.action in [Action.RUNNING, Action.RUN_BRAKE, Action.CROUCH_START]:
                        x = 0
                    # RUNNING and DASHING are very different. Even if custombot/opponent are within 0.1 units of each other during DASHING, they will not cross each other up if custombot does a pivot shine.
                    if abs(opponent_state.position.x) + 41 > melee.stages.EDGE_GROUND_POSITION[gamestate.stage] and abs(opponent_state.position.x) > abs(custombot_state.position.x) and custombot_state.action in [Action.DASHING, Action.TURNING, Action.STANDING]:
                        x = 0
                    # If we are running away from our opponent, just shine now
                    onright = opponent_state.position.x < custombot_state.position.x
                    if (custombot_state.speed_ground_x_self > 0) == onright and abs(gamestate.distance) <= 9.5:
                        self.pickchain(Chains.Waveshine, [x])
                        return
                    if framesleft <= 6:
                        self.pickchain(Chains.Waveshine, [x])
                        return
            # We're in range, but don't have enough time. Let's try turning around to do a pivot.
            else:
                self.chain = None
                # Pick a point right behind us
                pivotpoint = custombot_state.position.x
                dashbuffer = 5
                if custombot_state.facing:
                    dashbuffer = -dashbuffer
                pivotpoint += dashbuffer
                self.pickchain(Chains.DashDance, [pivotpoint])
                return

        # Kill the existing chain and start a new one
        self.chain = None
        self.pickchain(Chains.DashDance, [endposition])
