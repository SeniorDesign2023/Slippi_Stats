import melee
import json
from CharacterData import CharacterData
from GeneralizedAgent import GeneralizedAgent
from TestBot import testRun

class BotManager:
    def __init__(self):
        self.config: dict = None
        self.console: melee.Console = None
        self.controller: melee.Controller = None

    def readConfig(self, fp: str):
        try:
            f = open(fp, "r")
            c: dict = json.load(f)
            f.close
            return c
        except:
            return None
        
    def run(self, fp: str):
        print('Running GeneralBot')
        
        self.config = self.readConfig(fp)
        if self.config == None:
            return ("fail: failed to read json", None)
          
        try:
          port_bot = self.config["SLP"]["PORT_BOT"]
          port_opp = self.config["SLP"]["PORT_OPP"]
          selected_character : melee.Character = self.config["SELECTED"]["CHARACTER"]
          selected_stage : melee.Stage = self.config["SELECTED"]["STAGE"]
        except:
          return ("fail: json missing elements") 

        # Init Slippi classes
        if self.console == None:
            self.console = melee.Console(path=self.config["SLP"]["PATH"])
            self.console.run()
            self.console.connect()

        if self.controller != None:
            self.controller.disconnect()
        self.controller.connect(console=self.console, port=port_bot)


        # Init and check bot data
        charData = CharacterData(selected_character, selected_stage, port_bot, port_opp)
        agent = GeneralizedAgent(charData)

        # Run bot until passed back
        gameState = testRun(agent, self.console, self.controller)
        return ("success", gameState)