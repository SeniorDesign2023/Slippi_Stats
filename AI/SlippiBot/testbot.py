import melee
import melee.gamestate
import math
from CharacterData import CharacterData
from GeneralizedActions import GeneralizedAgent

PORT_BOT = 2
PORT_HUMAN = 1
#remember to change the path to be yours
console = melee.Console(path="C:/Users/micha/AppData/Roaming/Slippi Launcher/netplay")
controller = melee.Controller(console=console, port=PORT_BOT)

FrameData = melee.framedata.FrameData()
character_bot = melee.Character.MARIO
stage_selected = melee.Stage.BATTLEFIELD
botData = CharacterData(FrameData, character_bot, stage_selected, PORT_BOT, PORT_HUMAN)
#print(botData.ATTACK_FIRSTFRAME)
#print(botData.ATTACK_LEASTFRAME)


console.run()
console.connect()
controller.connect()

#botData.testRun(console, controller)

#just for testing. tells you their current states. remember to pause the game to read the output

while True:
    gamestate = console.step() 
    if gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
        print("Bot State: " + gamestate.players[PORT_BOT].action.name)
        print("Player State: " + gamestate.players[PORT_HUMAN].action.name)
        pass
    else: 
        melee.MenuHelper.menu_helper_simple(gamestate,
                                            controller,
                                            melee.Character.MARIO,
                                            melee.Stage.FOUNTAIN_OF_DREAMS,
                                            "",
                                            costume=0,
                                            autostart=False,
                                            swag=False)