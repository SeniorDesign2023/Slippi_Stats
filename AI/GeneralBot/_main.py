import melee
from CharacterData import CharacterData
from GeneralizedAgent import GeneralizedAgent
from TestBot import testRun

defaultCfg = {
  "REL_PATH" : "configs/dk.json"
  "CHARACTER" : melee.Character.FOX,
  "STAGE" : melee.Stages.BATTLEFIELD,
  "PORT_BOT" : 0,
  "PORT_PLR" : 1,
  "FRAME_DELAY" : 0,
  "LCNCL_RATE" : 0.8,
  "TECH_RATE" : 0.8,
  "PLAYSTYLE" : "aggressive",
  "ATTACK_STYLE" : "aerial",
  "PERFECT_RECOVERY" : True,
  "EDGE_GUARD" : "high",
  "WAVESHINE" : True,   # Must select Fox/Falco to set this either of these as True
  "MULTISHINE" : False, #
}

class BotManager:
  def __init__(self, configFilePath: str):
    self.configPath = configFilePath
    self.config = self.readConfig(configFilePath)
    
  def readConfig(self, fp: str):
    f = open(fp, "r")
    c: dict = json.load(f)
    f.close
    return c

  
    

SLP_PATH = "C:/Users/sonic/AppData/Roaming/Slippi Launcher/netplay" # C:\Users\sonic\AppData\Roaming\Slippi Launcher\netplay
PORT_BOT = 1
PORT_PLR = 2
                
print('Starting GeneralBot')

# Init Slippi classes
console = melee.Console(path=SLP_PATH)
controller = melee.Controller(console=console, port=PORT_BOT)
controller_human = melee.Controller(console=console,
                                    port=PORT_PLR,
                                    type=melee.ControllerType.GCN_ADAPTER)
    
# Connect and run bot
console.run()
console.connect()
controller.connect()
controller_human.connect()

# Init Melee classes
character_bot = melee.Character.DK
stage_selected = melee.Stage.BATTLEFIELD

# Init and check bot data
charData = CharacterData(character_bot, stage_selected, PORT_BOT, PORT_PLR)
agent = GeneralizedAgent(charData)

# Run bot until passed back
gameState = testRun(agent, console, controller)

