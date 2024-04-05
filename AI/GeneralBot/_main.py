import melee
from CharacterData import CharacterData
from GeneralizedAgent import GeneralizedAgent
from TestBot import testRun

SLP_PATH = "C:/Users/sonic/AppData/Roaming/Slippi Launcher/netplay" # C:\Users\sonic\AppData\Roaming\Slippi Launcher\netplay
PORT_BOT = 1
PORT_PLR = 2
                
print('Starting GeneralBot')

# Init melee classes
console = melee.Console(path=SLP_PATH)
character_bot = melee.Character.DK
stage_selected = melee.Stage.BATTLEFIELD
controller = melee.Controller(console=console, port=PORT_BOT)
controller_human = melee.Controller(console=console,
                                    port=PORT_PLR,
                                    type=melee.ControllerType.GCN_ADAPTER)
    
# Connect and run bot
console.run()
console.connect()
controller.connect()
controller_human.connect()

# Init and check bot data
charData = CharacterData(character_bot, stage_selected, PORT_BOT, PORT_PLR)
agent = GeneralizedAgent(charData)

# Perform test run
testRun(agent, console, controller)

