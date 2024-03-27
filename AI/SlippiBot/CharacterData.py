import melee
import math
from GeneralizedActions import GA

def playerVector(gameState: melee.GameState):
    distance = [gameState.players[1].x - gameState.players[2].x, gameState.players[1].y - gameState.players[2].y]
    norm = math.sqrt(distance[0] ** 2 + distance[1] ** 2)
    return [-distance[0] / norm, -distance[1] / norm] 

class CharacterData:
    def __init__(self, FD: melee.FrameData, character: melee.Character, stage_selected: melee.Stage, PORT_SELF: int, PORT_ENEMY: int):
        self.FD = FD
        self.CHARACTER = character
        self.STAGE_SELECTED = stage_selected
        self.PORT_SELF = PORT_SELF
        self.PORT_ENEMY = PORT_ENEMY
        
        self.MAX_JUMPS = FD.max_jumps(character)
        
        attacks = []
        for Action in melee.Action:
            if FD.is_attack(character, Action):
                attacks.append(Action)
        
        ATTACK_FIRSTFRAME = sorted(attacks, key = lambda ac: FD.first_hitbox_frame(character, ac))
        self.ATTACK_FIRSTFRAME = list(map(lambda ac: (ac.name, FD.first_hitbox_frame(character, ac)), ATTACK_FIRSTFRAME))
         
        ATTACK_LEASTFRAME = sorted(attacks, key = lambda ac: FD.iasa(character, ac))
        self.ATTACK_LEASTFRAME = list(map(lambda ac: (ac.name, FD.iasa(character, ac)), ATTACK_LEASTFRAME))
        
        # Can change the sorted portion to start with any prior list, i.e. set second level sorting priority
        ATTACK_FRANGE = sorted(ATTACK_FIRSTFRAME, key = lambda ac: FD.range_forward(character, ac, 1), reverse=True)
        self.ATTACK_FRANGE = list(map(lambda ac: (ac.name, FD.range_forward(character, ac, 1)), ATTACK_FRANGE))
        
        ATTACK_BRANGE = sorted(ATTACK_FIRSTFRAME, key = lambda ac: FD.range_backward(character, ac, 1), reverse=True)
        self.ATTACK_BRANGE = list(map(lambda ac: (ac.name, FD.range_backward(character, ac, 1)), ATTACK_BRANGE))
        
        ATTACK_MOSTFRAME = sorted(ATTACK_FIRSTFRAME, key = lambda ac: FD.last_hitbox_frame(character, ac) - FD.first_hitbox_frame(character, ac))
        self.ATTACK_MOSTFRAME = list(map(lambda ac: (ac.name, FD.last_hitbox_frame(character, ac) - FD.first_hitbox_frame(character, ac)), ATTACK_MOSTFRAME))
        
    def testAllInput(self, console: melee.Console, controller: melee.Controller):
        print("TESTING (console & controllers must already be connected to test!)")
        ga = GA(self.FD, self.PORT_SELF, self.PORT_ENEMY)
        nextAction = 200
        actions = [ga.shorthop, ga.fullhop, ga.jab, ga.uair, lambda x: print("end! " + str(type(x)))]
        index = 0
        while(True):
            gamestate = console.step()
            
            if gamestate is None:
                continue
            
            if console.processingtime * 1000 > 12:
                print("WARNING: Last frame took " + str(console.processingtime*1000) + "ms to process.")

            if gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
                ga.nextState(gamestate, controller)
                if gamestate.frame >= nextAction:
                    print(controller.current.button)
                    print(controller.current.c_stick)
                    print(controller.current.main_stick)
                    print(actions[index%4])
                    print(dict(ga.release_buffer))
                    nextAction += 200
                    actions[index%4](controller)
                    index += 1
                    
                plrVec = playerVector(gamestate)
                controller.tilt_analog_unit(melee.Button.BUTTON_MAIN, plrVec[0], plrVec[1]) 
                pass
            else:
                melee.MenuHelper.menu_helper_simple(gamestate,
                                                    controller,
                                                    self.CHARACTER,
                                                    melee.Stage.FINAL_DESTINATION,
                                                    "",
                                                    costume=2,
                                                    autostart=True,
                                                    swag=False)