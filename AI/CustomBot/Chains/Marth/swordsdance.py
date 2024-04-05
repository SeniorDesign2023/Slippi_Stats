import melee
from melee.enums import Action, Button
from Chains.chain import Chain


""" May need to add another section for using the first attack in the air as part of a recovery. """
class SwordsDance(Chain):
    def __init__(self, sequence=['neutral']):
        self.sequence = sequence
        self.current_step = 0

    def step(self, gamestate, custombot_state, opponent_state):
        controller = self.controller

        # We're done here if the sequence is complete or if Marth is grabbing the ledge
        if self.current_step >= len(self.sequence) or custombot_state.action in [Action.EDGE_CATCHING, Action.EDGE_HANGING]:
            self.interruptible = True
            controller.empty_input()
            return

        # If Marth is already in the Swords Dance animation, advance to the next step
        if custombot_state.action in [Action.SWORD_DANCE_1, Action.SWORD_DANCE_2_HIGH, Action.SWORD_DANCE_2_MID, Action.SWORD_DANCE_3_HIGH,
                                      Action.SWORD_DANCE_3_LOW, Action.SWORD_DANCE_3_MID, Action.SWORD_DANCE_4_HIGH, Action.SWORD_DANCE_4_LOW,
                                      Action.SWORD_DANCE_4_MID]:
            self.current_step += 1
            return
        
        if custombot_state.action in [Action.SWORD_DANCE_1_AIR, Action.SWORD_DANCE_2_HIGH_AIR, Action.SWORD_DANCE_2_MID_AIR,
                                      Action.SWORD_DANCE_3_HIGH_AIR, Action.SWORD_DANCE_3_LOW_AIR, Action.SWORD_DANCE_3_MID_AIR,
                                      Action.SWORD_DANCE_4_HIGH_AIR, Action.SWORD_DANCE_4_LOW_AIR, Action.SWORD_DANCE_4_MID_AIR]:
            self.current_step += 1
            return

        # Press and hold the B button to start and continue Swords Dance
        controller.press_button(Button.BUTTON_B)
        self.interruptible = False

        # Choose the appropriate action based on the current step and direction
        direction = self.sequence[self.current_step]
        if self.current_step == 0:  # First attack
            controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0.5)
        elif self.current_step == 1:  # Second attack
            if direction == 'up':
                controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 1)
            else:  # neutral or forward
                controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0.5)
        elif self.current_step >= 2:  # Third and fourth attacks
            if direction == 'up':
                controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 1)
            elif direction == 'down':
                controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0)
            else:  # neutral or forward
                controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0.5)
