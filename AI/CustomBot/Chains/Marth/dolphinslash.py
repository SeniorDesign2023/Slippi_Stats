import melee
from melee.enums import Action, Button
from Chains.chain import Chain

class DolphinSlash(Chain):
    def get_nearest_platform_edge(self, gamestate, custombot_state):
        # Find the nearest platform edge
        nearest_edge_x = None
        nearest_edge_distance = float('inf')
        for platform in gamestate.platforms:
            for edge_x in [platform.left_edge, platform.right_edge]:
                distance = abs(custombot_state.position.x - edge_x)
                if distance < nearest_edge_distance:
                    nearest_edge_distance = distance
                    nearest_edge_x = edge_x
        return nearest_edge_x

    def step(self, gamestate, custombot_state, opponent_state):
        controller = self.controller

        # We're done here if Marth is grabbing the ledge
        if custombot_state.action in [Action.EDGE_CATCHING, Action.EDGE_HANGING]:
            self.interruptible = True
            controller.empty_input()
            return

        # If Marth is already in the Dolphin Slash animation, do nothing
        if custombot_state.action in [Action.MARTH_COUNTER, Action.MARTH_COUNTER_FALL]:
            self.interruptible = False
            controller.empty_input()
            return

        # Calculate the direction towards the nearest platform edge
        nearest_edge_x = self.get_nearest_platform_edge(gamestate, custombot_state)
        if nearest_edge_x is not None:
            direction = 0.5 + (0.5 * (nearest_edge_x - custombot_state.position.x) / abs(nearest_edge_x - custombot_state.position.x))
        else:
            direction = 0.5

        # Press the B button and tilt the control stick towards the nearest platform edge to start Dolphin Slash
        controller.press_button(Button.BUTTON_B)
        controller.tilt_analog(Button.BUTTON_MAIN, direction, 1)
        self.interruptible = False
