import melee
import math
from GeneralizedActions import GeneralizedAgent

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
        
    def testRun(self, console: melee.Console, controller: melee.Controller):
        print("TESTING (console & controllers must already be connected to test!)")
        ga = GeneralizedAgent(self.FD, self.PORT_SELF, self.PORT_ENEMY)
        nextAction = 200
        actionsGround = [ga.jab, ga.daft, ga.usmash, ga.dsmash]
        actionsAir = [ga.uair, ga.dair, ga.bair]
        indexG = 0
        indexA = 0
        doGround = True
        while(True):
            gamestate = console.step()
            
            if gamestate is None:
                continue
            
            if console.processingtime * 1000 > 12:
                print("WARNING: Last frame took " + str(console.processingtime*1000) + "ms to process.")

            if gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
                plrVec = playerVector(gamestate)
                ga.nextState(gamestate)
                controller.tilt_analog(melee.Button.BUTTON_MAIN, int(ga.es.position.x > ga.ps.position.x), 0.5) # fuck this 0.5
                ga.hop_to_y(controller, ga.es.position.y, 50)
                print(ga.ps.action)
                print(ga.ps.jumps_left)
                print(controller.current.button[melee.Button.BUTTON_A])
                if doGround:
                    if ga.jab(controller):
                        indexG += 1
                        doGround = False
                else:
                    if actionsAir[indexA%4](controller):
                        indexA += 1
                #controller.tilt_analog_unit(melee.Button.BUTTON_MAIN, plrVec[0], plrVec[1]) 
                ga.endState(gamestate, controller)
                pass
            else:
                melee.MenuHelper.menu_helper_simple(gamestate,
                                                    controller,
                                                    self.CHARACTER,
                                                    self.STAGE_SELECTED,
                                                    "",
                                                    costume=2,
                                                    autostart=True,
                                                    swag=False)