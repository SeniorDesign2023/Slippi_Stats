import melee
import Chains
import random
from melee.enums import Action, Button, Character
from Tactics.tactic import Tactic
from Chains.firefox import FIREFOX

class Mitigate(Tactic):
    def __init__(self, logger, controller, framedata, difficulty):
        Tactic.__init__(self, logger, controller, framedata, difficulty)
        self.random_di = random.randint(0, 1)

    def needsmitigation(custombot_state):
        # Always interrupt if we got hit. Whatever chain we were in will have been broken anyway
        if custombot_state.action in [Action.GRABBED, Action.GRAB_PUMMELED, Action.GRAB_PULL, \
                Action.GRAB_PUMMELED, Action.GRAB_PULLING_HIGH, Action.GRABBED_WAIT_HIGH, Action.PUMMELED_HIGH, \
                Action.CAPTURE_WAIT_KIRBY, Action.CAPTURE_KIRBY, Action.SHOULDERED_WAIT, Action.SHOULDERED_WALK_SLOW, \
                Action.SHOULDERED_WALK_MIDDLE, Action.SHOULDERED_TURN, Action.CAPTURE_WAIT_KOOPA, Action.CAPTURE_DAMAGE_KOOPA]:
            return True

        # Thrown action
        if custombot_state.action in [Action.THROWN_FORWARD, Action.THROWN_BACK, \
                Action.THROWN_UP, Action.THROWN_DOWN, Action.THROWN_DOWN_2]:
            return True

        if custombot_state.hitstun_frames_left == 0:
            return False

        if Action.DAMAGE_HIGH_1.value <= custombot_state.action.value <= Action.DAMAGE_FLY_ROLL.value:
            return True
        if custombot_state.action == Action.TUMBLING:
            return True

        return False

    def step(self, gamestate, custombot_state, opponent_state):
        self._propagate  = (gamestate, custombot_state, opponent_state)

        #If we can't interrupt the chain, just continue it
        if self.chain != None and not self.chain.interruptible:
            self.chain.step(gamestate, custombot_state, opponent_state)
            return

        # Did we get grabbed?
        if custombot_state.action in [Action.GRABBED, Action.GRAB_PUMMELED, Action.GRAB_PULL, \
                Action.GRAB_PUMMELED, Action.GRAB_PULLING_HIGH, Action.GRABBED_WAIT_HIGH, Action.PUMMELED_HIGH, \
                Action.CAPTURE_WAIT_KIRBY, Action.CAPTURE_KIRBY, Action.SHOULDERED_WAIT, Action.SHOULDERED_WALK_SLOW, \
                Action.SHOULDERED_WALK_MIDDLE, Action.SHOULDERED_TURN, Action.CAPTURE_WAIT_KOOPA, Action.CAPTURE_DAMAGE_KOOPA]:
            self.pickchain(Chains.Struggle)
            return

        # For throws, randomize the TDI
        if custombot_state.action in [Action.THROWN_FORWARD, Action.THROWN_BACK, Action.THROWN_DOWN, Action.THROWN_DOWN_2]:
            self.chain = None
            self.pickchain(Chains.DI, [random.choice([0, 0.5, 1]), random.choice([0, 0.5, 1])])
            return
        # Up throws are a little different. Don't DI up and down
        if custombot_state.action == Action.THROWN_UP:
            self.chain = None
            self.pickchain(Chains.DI, [random.choice([0, 0.3, 0.5, 0.7, 1]), 0.5])
            return

        # Trajectory DI
        if custombot_state.hitlag_left == 1:
            self.pickchain(Chains.TDI)
            return

        # Smash DI
        if custombot_state.hitlag_left > 1:
            self.pickchain(Chains.SDI)
            return

        """ Adjustable based on difficulty """
        # Tech if we need to
        #   Calculate when we will land
        if custombot_state.position.y > -4 and not custombot_state.on_ground and \
                Action.DAMAGE_HIGH_1.value <= custombot_state.action.value <= Action.DAMAGE_FLY_ROLL.value:
            framesuntillanding = 0
            speed = custombot_state.speed_y_attack + custombot_state.speed_y_self
            height = custombot_state.position.y
            gravity = self.framedata.characterdata[custombot_state.character]["Gravity"]
            termvelocity = self.framedata.characterdata[custombot_state.character]["TerminalVelocity"]
            while height > 0:
                height += speed
                speed -= gravity
                speed = max(speed, -termvelocity)
                framesuntillanding += 1
                # Shortcut if we get too far
                if framesuntillanding > 120:
                    break
            # Do the tech
            if framesuntillanding < 4:
                self.pickchain(Chains.Tech)
                return

        """ This uses Firefox, either change so it does up-b or set it to only Fox/Falco """
        # Meteor cancel 8 frames after hitlag ended
        # TODO: Don't SDI an up input if we want to meteor cancel
        if custombot_state.speed_y_attack < 0 and custombot_state.action_frame == 8:
            if custombot_state.jumps_left > 0:
                if gamestate.custom["meteor_jump_lockout"] == 0:
                    self.pickchain(Chains.Jump, [int(custombot_state.position.x < 0)])
                    return
            elif gamestate.custom["meteor_ff_lockout"] == 0:
                self.pickchain(Chains.Firefox, [FIREFOX.SAFERANDOM])
                return

        if custombot_state.action == Action.TUMBLING:
            x = gamestate.frame % 2
            self.chain = None
            self.pickchain(Chains.DI, [x, 0.5])
            return

        # DI randomly as a fallback
        self.pickchain(Chains.DI, [self.random_di, 0.5])
        return
