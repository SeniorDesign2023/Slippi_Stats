import melee
import math
from CharacterData import CharacterData
from GeneralizedActions import GeneralizedAgent

SLP_PATH = "C:/Users/micha/AppData/Roaming/Slippi Launcher/netplay" # C:\Users\sonic\AppData\Roaming\Slippi Launcher\netplay
PORT_BOT = 1
PORT_PLR = 2

# Init framedata class
FrameData = melee.framedata.FrameData()
                
print('starting dk')

# Init melee classes
console = melee.Console(path=SLP_PATH)
character_bot = melee.Character.DK
stage_selected = melee.Stage.BATTLEFIELD
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

botData.testRun(console, controller)
    



