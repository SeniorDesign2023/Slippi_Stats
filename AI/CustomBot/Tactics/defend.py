import melee
import Chains
import math
from melee.enums import Action, Button, Character
from Tactics.tactic import Tactic

class Defend(Tactic):
    def needsprojectiledefense(custombot_state, opponent_state, gamestate, logger=None):
        if custombot_state.invulnerability_left > 2:
            return False

        # Ignore Fox lasers. They 'just' do damage. Nothing we actually care about
        #   It's worse to put ourselves in stun just to prevent a few percent
        if opponent_state.character == Character.FOX:
            return False

        # Loop through each projectile
        for projectile in gamestate.projectiles:
            if projectile.type == melee.ProjectileType.SAMUS_GRAPPLE_BEAM and opponent_state.on_ground:
                continue
            if projectile.type in [melee.ProjectileType.SHEIK_SMOKE, melee.ProjectileType.SHEIK_CHAIN ]:
                continue
            # Missles and needles that aren't moving are actually already exploded. Ignore them
            if projectile.type in [melee.ProjectileType.SAMUS_MISSLE, melee.ProjectileType.NEEDLE_THROWN] and (-0.01 < projectile.speed.x < 0.01):
                continue

            if projectile.type == melee.ProjectileType.SAMUS_BOMB and (-0.01 < projectile.speed.y < 0.01):
                continue

            size = 10
            if projectile.type in [melee.ProjectileType.PIKACHU_THUNDERJOLT_1, melee.ProjectileType.PICHU_THUNDERJOLT_1]:
                size = 18
            if projectile.type == melee.ProjectileType.NEEDLE_THROWN:
                size = 12
            if projectile.type in [melee.ProjectileType.PIKACHU_THUNDER, melee.ProjectileType.PICHU_THUNDER]:
                size = 30
            if projectile.type == melee.ProjectileType.TURNIP:
                size = 12
            # Your hitbox is super distorted when edge hanging. Give ourselves more leeway here
            if custombot_state.action == Action.EDGE_HANGING:
                size *= 2

            # If the projectile is above us, then increase its effective size.
            #   Since our hurtbox extends upwards more that way
            if abs(custombot_state.position.x - projectile.position.x) < 15 and abs(projectile.speed.x) < 1:
                size += 15

            # Is this about to hit us in the next frame?
            proj_x, proj_y = projectile.position.x, projectile.position.y
            for i in range(0, 1):
                proj_x += projectile.speed.x
                proj_y += projectile.speed.y
                custombot_y = custombot_state.position.y
                custombot_x = custombot_state.position.x + custombot_state.speed_ground_x_self
                # This is a bit hacky, but it's easiest to move our "center" up a little for the math
                if custombot_state.on_ground:
                    custombot_y += 8
                distance = math.sqrt((proj_x - custombot_x)**2 + (proj_y - custombot_y)**2)
                if logger:
                    logger.log("Notes", " distance to projectile: " + str(distance) + " ", concat=True)
                if distance < size:
                    return True
        return False

    def needsdefense(custombot_state, opponent_state, gamestate, framedata):
        # Is opponent attacking?
        if custombot_state.invulnerability_left > 2:
            return False

        # Ignore the chain
        if opponent_state.character == Character.SHEIK and opponent_state.action == Action.SWORD_DANCE_2_HIGH:
            return False

        # Try to the ledge from Sheik Shino stall first
        if opponent_state.character == Character.SHEIK and opponent_state.action == Action.SWORD_DANCE_1_AIR and opponent_state.action_frame < 10:
            return False

        # Puff sing stall is safe to grab from
        if opponent_state.character == Character.JIGGLYPUFF and opponent_state.action in [Action.DOWN_B_AIR, Action.SHINE_RELEASE_AIR] and opponent_state.action_frame < 10:
            return False

        # FireFox is different
        firefox = opponent_state.action in [Action.SWORD_DANCE_4_HIGH, Action.SWORD_DANCE_4_MID] and opponent_state.character in [Character.FOX, Character.FALCO]
        if firefox:
            # Assume they're heading at us, shield in time
            speed = 2.2
            if opponent_state.character == Character.FOX:
                speed = 3.8
            if (gamestate.distance - 12) / speed < 3:
                return True

        # What state of the attack is the opponent in?
        # Windup / Attacking / Cooldown / Not Attacking
        attackstate = framedata.attack_state(opponent_state.character, opponent_state.action, opponent_state.action_frame)
        if attackstate == melee.AttackState.COOLDOWN:
            return False
        if attackstate == melee.AttackState.NOT_ATTACKING:
            return False

        # We can't be grabbed while on the edge
        if framedata.is_grab(opponent_state.character, opponent_state.action) and \
                custombot_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING]:
            return False

        # Will we be hit by this attack if we stand still?
        hitframe = framedata.in_range(opponent_state, custombot_state, gamestate.stage)
        # Only defend on the edge if the hit is about to get us
        if custombot_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING] and hitframe > 2:
            return False
        if hitframe:
            return True

        return False

    def step(self, gamestate, custombot_state, opponent_state):
        self._propagate  = (gamestate, custombot_state, opponent_state)
        #If we can't interrupt the chain, just continue it
        if self.chain != None and not self.chain.interruptible:
            self.chain.step(gamestate, custombot_state, opponent_state)
            return

        projectiles = gamestate.projectiles
        framedata = self.framedata

        
        """ This will need to be adjustable based on difficulty """
        # Do we need to defend against a projectile?
        #   If there is a projectile, just assume that's why we're here.
        #   TODO: maybe we should re-calculate if this is what we're defending
        if Defend.needsprojectiledefense(custombot_state, opponent_state, gamestate):
            for projectile in projectiles:
                # Don't consider a grapple beam a projectile. It doesn't have a hitbox
                if projectile.type == melee.ProjectileType.SAMUS_GRAPPLE_BEAM:
                    continue
                if custombot_state.action == Action.EDGE_HANGING:
                    if opponent_state.character == Character.PEACH and \
                            opponent_state.action in [Action.MARTH_COUNTER, Action.PARASOL_FALLING]:
                        #TODO: Make this a chain
                        self.chain = None
                        self.controller.press_button(Button.BUTTON_L)
                        return
                    else:
                        self.chain = None
                        self.pickchain(Chains.DI, [0.5, 0.65])
                        return
                self.pickchain(Chains.Powershield, [False, True])
                return

        hitframe = framedata.in_range(opponent_state, custombot_state, gamestate.stage)
        framesuntilhit = hitframe - opponent_state.action_frame

        # FireFox is different
        firefox = opponent_state.action in [Action.SWORD_DANCE_4_HIGH, Action.SWORD_DANCE_4_MID] and opponent_state.character in [Character.FOX, Character.FALCO]

        if firefox:
            # Assume they're heading at us, shield in time
            speed = 2.2
            if opponent_state.character == Character.FOX:
                speed = 3.8
            if (gamestate.distance - 12) / speed < 3:
                framesuntilhit = 0

        # Is the attack a grab? If so, spot dodge right away
        is_grab = self.framedata.is_grab(opponent_state.character, opponent_state.action)
        #   Ignore yoshi's really long windup
        if opponent_state.character == Character.YOSHI and opponent_state.action in [Action.NEUTRAL_B_CHARGING_AIR, Action.SWORD_DANCE_2_MID] and opponent_state.action_frame < 14:
            is_grab = False
        # Bowser's claw is so slow we have to wait a bit.
        if opponent_state.character == Character.BOWSER and opponent_state.action_frame < 14 and opponent_state.action in [Action.NEUTRAL_B_ATTACKING_AIR, Action.SWORD_DANCE_3_MID]:
            is_grab = False
        #   Falcon/Ganon up-B
        dangerous_up_b = opponent_state.character in [Character.GANONDORF, Character.CPTFALCON] and opponent_state.action == Action.SWORD_DANCE_3_LOW
        if not dangerous_up_b and is_grab and (opponent_state.character != Character.SAMUS or framesuntilhit <= 2):
            self.pickchain(Chains.SpotDodge)
            return

        if self.logger:
            self.logger.log("Notes", "framesuntilhit: " + str(framesuntilhit) + " ", concat=True)

        onfront = (opponent_state.position.x < custombot_state.position.x) == opponent_state.facing
        # Are we in the powershield window?
        if framesuntilhit <= 2 and not is_grab:
            if framesuntilhit == 2 and opponent_state.action in [Action.GROUND_ATTACK_UP, Action.GETUP_ATTACK]:
                self.chain = None
                self.pickchain(Chains.Run, [custombot_state.position.x < opponent_state.position.x])
                return

            if custombot_state.action == Action.EDGE_HANGING:
                self.chain = None
                self.pickchain(Chains.DI, [0.5, 0.65])
                return
            hold = framedata.hitbox_count(opponent_state.character, opponent_state.action) > 1
            self.pickchain(Chains.Powershield, [hold, False])
        else:
            # 12 starting buffer for Fox's character model size
            bufferzone = 12
            if onfront:
                bufferzone += framedata.range_forward(opponent_state.character, opponent_state.action, opponent_state.action_frame)
            else:
                bufferzone += framedata.range_backward(opponent_state.character, opponent_state.action, opponent_state.action_frame)

            pivotpoint = opponent_state.position.x

            # TODO: I hate having individual exceptions like this. This is raptor boost.
            # This should be handled by range_forward/back. It doesn't do locomotion currently
            if opponent_state.character in [Character.GANONDORF, Character.CPTFALCON] and opponent_state.action == Action.SWORD_DANCE_1:
                bufferzone += 25

            """ This will be adjustable based on difficulty """
            # If it's a getup attack, just get in there and shield it. It's safe
            if opponent_state.action in [Action.GROUND_ATTACK_UP, Action.GETUP_ATTACK]:
                self.chain = None
                self.pickchain(Chains.DashDance, [opponent_state.position.x])
                return

            # Add some extra buffer for horizontal movement
            if opponent_state.speed_y_self < 0:
                pivotpoint += abs(opponent_state.position.y // opponent_state.speed_y_self) * opponent_state.speed_air_x_self

            """ This will be adjustable based on difficulty """
            # Dash to a point away from the opponent, out of range
            if opponent_state.position.x < custombot_state.position.x:
                # Dash right
                pivotpoint += bufferzone
                # But don't run off the edge
                pivotpoint = min(melee.stages.EDGE_GROUND_POSITION[gamestate.stage]-5, pivotpoint)
            else:
                # Dash Left
                pivotpoint -= bufferzone
                # But don't run off the edge
                pivotpoint = max(-melee.stages.EDGE_GROUND_POSITION[gamestate.stage] + 5, pivotpoint)
            self.chain = None
            self.pickchain(Chains.DashDance, [pivotpoint])
