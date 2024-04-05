import melee
import Chains
from melee.enums import Action, Character, Stage
from Tactics.tactic import Tactic
from Chains.tilt import TILT_DIRECTION
from Chains.grabandthrow import THROW_DIRECTION
from Chains.airattack import AirAttack, AIR_ATTACK_DIRECTION
from Tactics.punish import Punish
from Tactics.infinite import Infinite


""" Probably remove infinite.py and create a version that will only allow the juggle a certain number of times"""
class Juggle(Tactic):
    def __init__(self, logger, controller, framedata, difficulty):
        Tactic.__init__(self, logger, controller, framedata, difficulty)

    def canjuggle(custombot_state, opponent_state, gamestate, framedata, difficulty):
        if opponent_state.invulnerability_left > 0:
            return False

        if custombot_state.off_stage:
            return False

        # If the opponent is in hitstun, in the air
        if (not opponent_state.on_ground) and (opponent_state.hitstun_frames_left > 0):
            if not framedata.is_attack(opponent_state.character, opponent_state.action):
                return True

        # Stop the juggle once at kill percent
        if opponent_state.percent > Infinite.killpercent(gamestate.stage, opponent_state.character):
            return False

        # If opponent is rolling and we can start a juggle combo from it
        if framedata.is_roll(opponent_state.character, opponent_state.action):
            if opponent_state.character in [Character.FOX, Character.FALCO, Character.JIGGLYPUFF, Character.PIKACHU]:
                return True

        return False

    def step(self, gamestate, custombot_state, opponent_state):
        self._propagate  = (gamestate, custombot_state, opponent_state)

        # If we can't interrupt the chain, just continue it
        if self.chain != None and not self.chain.interruptible:
            self.chain.step(gamestate, custombot_state, opponent_state)
            return

        # Get over to where they will end up at the end of hitstun
        end_x, end_y, frames_left = self.framedata.project_hit_location(opponent_state, gamestate.stage)

        if self.framedata.is_roll(opponent_state.character, opponent_state.action):
            end_x = self.framedata.roll_end_position(opponent_state, gamestate.stage) + self.framedata.slide_distance(opponent_state, opponent_state.speed_x_attack, frames_left)
            frames_left = self.framedata.last_roll_frame(opponent_state.character, opponent_state.action) - opponent_state.action_frame
            # TODO handle slideoff here

        facing_away = (custombot_state.position.x < end_x) != custombot_state.facing
        if custombot_state.action == Action.TURNING and custombot_state.action_frame == 1:
            facing_away = not facing_away

        on_ground = opponent_state.on_ground or opponent_state.position.y < 1 or opponent_state.action in [Action.TECH_MISS_UP, Action.TECH_MISS_DOWN]

        # Make sure we don't dashdance off the platform during a juggle
        side_platform_height, side_platform_left, side_platform_right = melee.side_platform_position(opponent_state.position.x > 0, gamestate.stage)
        top_platform_height, top_platform_left, top_platform_right = melee.top_platform_position(gamestate.stage)
        if opponent_state.position.y < 5:
            end_x = min(end_x, melee.EDGE_GROUND_POSITION[gamestate.stage]-5)
            end_x = max(end_x, -melee.EDGE_GROUND_POSITION[gamestate.stage]+5)
        elif (side_platform_height is not None) and abs(opponent_state.position.y - side_platform_height) < 5:
            end_x = min(end_x, side_platform_right-5)
            end_x = max(end_x, side_platform_left+5)
        elif (top_platform_height is not None) and abs(opponent_state.position.y - top_platform_height) < 5:
            end_x = min(end_x, top_platform_right-5)
            end_x = max(end_x, top_platform_left+5)

        # TODO Slideoff detection

        if self.logger:
            self.logger.log("Notes", " Predicted End Position: " + str(end_x) + " " + str(end_y) + " ", concat=True)
            self.logger.log("Notes", " on_ground: " + str(on_ground), concat=True)
            self.logger.log("Notes", " frames left: " + str(frames_left) + " ", concat=True)

        # Need to pivot the uptilt
        # Uptilt's hitbox is pretty forgiving if we do it a few frames early, so no big deal there
        if not on_ground:
            # If we can just throw out an uptilt and hit now, do it. No need to wait for them to fall further
            end_early_x, end_early_y, _ = self.framedata.project_hit_location(opponent_state, gamestate.stage, 7)
            if self.logger:
                self.logger.log("Notes", " uptilt early End Position: " + str(end_early_x) + " " + str(end_early_y) + " ", concat=True)
            in_range = (abs(end_early_x - custombot_state.position.x) < 8) and (abs(end_early_y - custombot_state.position.y) < 12)
            if custombot_state.action in [Action.TURNING, Action.STANDING] and in_range and (7 <= frames_left):
                if facing_away or abs(end_early_y - custombot_state.position.y) > 5:
                    self.chain = None
                    self.pickchain(Chains.Tilt, [TILT_DIRECTION.UP])
                    return
                # For the grab, they can't be too high vertically, or too low
                elif custombot_state.position.y + 2 < end_early_y:
                    self.chain = None
                    self.pickchain(Chains.GrabAndThrow, [THROW_DIRECTION.UP])
                    return

            # Check each height level, can we do an up-air right now?
            for height_level in AirAttack.height_levels():
                height = AirAttack.attack_height(height_level)
                commitment = AirAttack.frame_commitment(height_level)
                end_early_x, end_early_y, _ = self.framedata.project_hit_location(opponent_state, gamestate.stage, commitment)
                # -3 to commitment here because of first hit of upair. Shave 3 frames off
                if (commitment-3 < frames_left) and (abs(custombot_state.position.x - end_early_x) < 20):
                    # It's okay if custombot's end position is no more than 5 units above the target, and 10 below
                    if -10 < ((height+custombot_state.position.y) - end_early_y) < 5:
                        if self.logger:
                            self.logger.log("Notes", " Early End Position: " + str(end_early_x) + " " + str(end_early_y) + " ", concat=True)
                            self.logger.log("Notes", " height_level: " + str(height_level), concat=True)
                            self.logger.log("Notes", " commitment: " + str(commitment), concat=True)
                        self.chain = None
                        self.pickchain(Chains.AirAttack, [end_early_x, end_early_y, height_level, AIR_ATTACK_DIRECTION.UP])
                        return

            # They are going to land on a platform before hitstun ends
            if frames_left < opponent_state.hitstun_frames_left and end_y > 0:
                # Board the platform they're going to
                if end_y > 40:
                    self.chain = None
                    self.pickchain(Chains.BoardTopPlatform)
                    return
                else:
                    self.chain = None
                    self.pickchain(Chains.BoardSidePlatform, [end_x > 0, False])
                    return

            # Just dash dance to where they will end up
            if frames_left > 9:
                self.chain = None
                self.pickchain(Chains.DashDance, [end_x])
                return
        else:
            if self.framedata.is_roll(opponent_state.character, opponent_state.action):
                # We still have plenty of time, so just get closer to the DD spot
                #   Even if we're already close
                if frames_left > 10:
                    # Do we need to jump up to the side platform?
                    side_plat_height, side_plat_left, side_plat_right = melee.side_platform_position(opponent_state.position.x > 0, gamestate.stage)
                    # TODO 13 is the fastest getup attack of the legal character, do a lookup for the actual one
                    if opponent_state.action in [Action.TECH_MISS_UP, Action.TECH_MISS_DOWN]:
                        frames_left += 13
                    if side_plat_height is not None and (frames_left > 25) and abs(side_plat_height - opponent_state.position.y) < 5:
                        # But only if we're already mostly there
                        custombot_on_side_plat = custombot_state.on_ground and abs(custombot_state.position.y - side_plat_height) < 5
                        if side_plat_left < custombot_state.position.x < side_plat_right and not custombot_on_side_plat:
                            self.chain = None
                            self.pickchain(Chains.BoardSidePlatform, [opponent_state.position.x > 0, False])
                            return
                        else:
                            self.chain = None
                            self.pickchain(Chains.DashDance, [(side_plat_left + side_plat_right) / 2])
                            return

                    if self.logger:
                        self.logger.log("Notes", " DD at: " + str(end_x), concat=True)
                        self.logger.log("Notes", " plat at: " + str(side_plat_left) + " " + str(side_plat_right), concat=True)
                    self.chain = None
                    self.pickchain(Chains.DashDance, [end_x])
                    return
                # We need to get to a position where our back is to the end position. We'll do a pivot stand to get there
                if (abs(custombot_state.position.x - end_x) < 5) and (abs(custombot_state.position.y - end_y) < 20):
                    # Pivot
                    if custombot_state.action == Action.DASHING:
                        self.chain = None
                        self.pickchain(Chains.Run, [not custombot_state.facing])
                        return
                    if custombot_state.action in [Action.TURNING, Action.STANDING]:
                        if 7 <= frames_left <= 9:
                            if facing_away and gamestate.distance < 20:
                                self.pickchain(Chains.Tilt, [TILT_DIRECTION.UP])
                                return
                            # Can't grab a tech miss. Don't try
                            elif opponent_state.action not in [Action.TECH_MISS_UP, Action.TECH_MISS_DOWN] and gamestate.distance < 10:
                                self.pickchain(Chains.GrabAndThrow, [THROW_DIRECTION.UP])
                                return

                        """ This uses a shine move, so set to be only available for Fox/Falco """
                        # Don't waveshine an opponent if they're in tech miss or laying down on a platform
                        #   It will end the juggle and be impossible to follow up on. Instead, we can just wait
                        tech_miss_on_plat = opponent_state.position.y > 10 and opponent_state.action in [Action.TECH_MISS_UP, Action.TECH_MISS_DOWN, Action.LYING_GROUND_UP, Action.LYING_GROUND_DOWN]
                        if frames_left == 1 and gamestate.distance < 10 and not tech_miss_on_plat:
                            self.pickchain(Chains.Waveshine)
                            return
                        else:
                            self.pickchain(Chains.Nothing)
                            return

                # If we're a little further away than 5 units, but still in range
                elif (abs(custombot_state.position.x - end_x) < 10):
                    # Don't dashdance here. Just stand still
                    if custombot_state.action == Action.TURNING and custombot_state.action_frame > 1:
                        self.pickchain(Chains.Nothing)
                        return

                    self.chain = None
                    self.pickchain(Chains.DashDance, [end_x])
                    return

                # We're further than 5 units away, so DD into their end position
                self.chain = None
                self.pickchain(Chains.DashDance, [end_x])
                return

        self.chain = None
        self.pickchain(Chains.DashDance, [end_x])
