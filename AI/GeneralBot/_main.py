import melee
from CharacterData import CharacterData
from GeneralizedAgent import GeneralizedAgent
from TestBot import testRun

class BotManager:
  def __init__(self):
    self.config = None
    self.console = None
    self.SLF_controller = None
    self.OP1_controller = None
    self.OP2_controller = None
    self.AL1_controller = None
    self.AL2_controller = None

  def readConfigs(self, filePaths: list):
    for fp in filePaths:
    f = open(fp, "r")
    c: dict = json.load(f)
    f.close
    return c

  def connect(self):
    # Init Slippi classes
    if self.console == None:
      console = melee.Console(path=self.config["SLP"]["PATH"])

    if self.config["PORTS"]["SELF"] == None
    controller = melee.Controller(console=console, port=self.config["SLP"]["PORT_BOT"])
    controller_human = melee.Controller(console=console,
                                        port=self.config["SLP"]["PORT_PLR"],
                                        type=melee.ControllerType.GCN_ADAPTER)
        
    # Connect and run bot
    console.run()
    console.connect()
    controller.connect()
    controller_human.connect()

  def run(self, callBack):
    print('Starting GeneralBot')
    self.config = self.readConfig(configPath)
    if self.config == None:
      return "No config"
    
    
    
    # Init Melee classes
    character_bot = self.config["SELECTED"]["STAGE"]
    stage_selected = self.config["SELECTED"]["STAGE"]
    
    # Init and check bot data
    charData = CharacterData(character_bot, stage_selected, PORT_BOT, PORT_PLR)
    agent = GeneralizedAgent(charData)
    
    # Run bot until passed back
    gameState = testRun(agent, console, controller)
    if self.callBack(gameState)

