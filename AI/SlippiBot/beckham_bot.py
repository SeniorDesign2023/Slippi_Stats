import melee
import math
from CharacterData import CharacterData
from GeneralizedActions import GA

SLP_PATH = "C:/Users/sonic/AppData/Roaming/Slippi Launcher/netplay" # C:\Users\sonic\AppData\Roaming\Slippi Launcher\netplay
PORT_BOT = 1
PORT_PLR = 2

# Init framedata class
FrameData = melee.framedata.FrameData()
                
print('starting dk')

# Init melee classes
console = melee.Console(path=SLP_PATH)
character_bot = melee.Character.DK
stage_selected = melee.Stage.POKEMON_STADIUM
controller = melee.Controller(console=console, port=PORT_BOT)
controller_human = melee.Controller(console=console,
                                    port=PORT_PLR,
                                    type=melee.ControllerType.GCN_ADAPTER)

# Init and check bot data
botData = CharacterData(FrameData, character_bot, stage_selected, PORT_BOT, PORT_PLR)
print("Max jumps is " + str(botData.MAX_JUMPS))
print(botData.ATTACK_FIRSTFRAME)
print(botData.ATTACK_LEASTFRAME)

# shorthand
def attackState(attacker: melee.PlayerState):
    return FrameData.attack_state(attacker.character, attacker.action, attacker.action_frame)
    
# returns normalized vector from bot to opponent
def playerVector(gameState: melee.GameState):
    distance = [gameState.players[PORT_BOT].x - gameState.players[PORT_PLR].x, gameState.players[PORT_BOT].y - gameState.players[PORT_PLR].y]
    norm = math.sqrt(distance[0] ** 2 + distance[1] ** 2)
    return [distance[0] / norm, distance[1] / norm] 
    

# Connect and run bot
console.run()
console.connect()
controller.connect()
controller_human.connect()

botData.testAllInput(console, controller)

while True:
    gamestate = console.step()
    if gamestate is None:
        continue
    
    if console.processingtime * 1000 > 12:
        print("WARNING: Last frame took " + str(console.processingtime*1000) + "ms to process.")

    if gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
        
        botState = melee.PlayerState(gamestate.players[1])
        playerState = melee.PlayerState(gamestate.players[2])
        print("BOT: " + str(botState.action))
        print("PLR: " + str(playerState.action))
        
        botAttackState = attackState(botState)
        playerAttackState = attackState(playerState)
        
        # Player is in one of: ATTACKING / WINDUP / COOLDOWN
        if playerAttackState != 3:
            frameAdvantage = FD.in_range(playerState, botState, gamestate.stage)
            
            if frameAdvantage > 0:
                controller.press_shoulder(1)
            else:
                controller.release_all
                
        # Bot is in one of: ATTACKING / WINDUP / COOLDOWN
        if botAttackState != 3:
            plrVec = playerVector(gamestate)
            controller.tilt_analog_unit(melee.Button.BUTTON_MAIN, plrVec[0], plrVec[1]) 
            
        if gamestate.distance < 20:
            controller.press_button(melee.Button.BUTTON_B)
            controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 1)
            
        else:
            controller.empty_input()
        pass
    else:
        melee.MenuHelper.menu_helper_simple(gamestate,
                                            controller,
                                            character_bot,
                                            stage_selected,
                                            "",
                                            costume=2,
                                            autostart=False,
                                            swag=False)
    



