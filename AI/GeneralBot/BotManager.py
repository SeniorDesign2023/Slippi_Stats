import melee
import json

import melee.controller
#rom GeneralBot.CharacterData import CharacterData
#from GeneralBot.GeneralizedAgent import GeneralizedAgent
#from GeneralBot.TestBot import testRun

from CharacterData import CharacterData
from GeneralizedAgent import GeneralizedAgent
from TestBot import testRun

shit = {
    5 : melee.Character.BOWSER,
    2 : melee.Character.CPTFALCON,
    3 : melee.Character.DK,
    21 : melee.Character.DOC,
    22 : melee.Character.FALCO,
    1 : melee.Character.FOX,
    24 : melee.Character.GAMEANDWATCH,
    25 : melee.Character.GANONDORF,
    15 : melee.Character.JIGGLYPUFF,
    4 : melee.Character.KIRBY,
    6 : melee.Character.LINK,
    17 : melee.Character.LUIGI,
    0 : melee.Character.MARIO,
    18 : melee.Character.MARTH,
    16 : melee.Character.MEWTWO,
    11 : melee.Character.NANA,
    8 : melee.Character.NESS,
    9 : melee.Character.PEACH,
    23 : melee.Character.PICHU,
    12 : melee.Character.PIKACHU,
    10 : melee.Character.POPO,
    26 : melee.Character.ROY,
    13 : melee.Character.SAMUS,
    7 : melee.Character.SHEIK,
    20 : melee.Character.YLINK,
    14 : melee.Character.YOSHI,
    19 : melee.Character.ZELDA,
}

shit2 = {
    24:melee.Stage.BATTLEFIELD ,
    26:melee.Stage.DREAMLAND ,
    25:melee.Stage.FINAL_DESTINATION ,
    8:melee.Stage.FOUNTAIN_OF_DREAMS,
    0:melee.Stage.NO_STAGE ,
    18:melee.Stage.POKEMON_STADIUM ,
    29:melee.Stage.RANDOM_STAGE ,
    6:melee.Stage.YOSHIS_STORY
}

class BotManager:
    def __init__(self):
        self.config: dict = None

    def readConfig(self, fp: str):
        try:
            f = open(fp, "r")
            c: dict = json.load(f)
            f.close
            return c
        except:
            return None
        
    def run(self, fp: str = 'C:/Users/sonic/Documents/Senior Design/Slippi_Stats/AI/GeneralBot/configs/beckham_dk.json'):
        print('Running GeneralBot')
        self.config = self.readConfig(fp)
        if self.config == None:
            return ("fail: failed to read json", None)
          
        port_bot = self.config["SLP"]["PORT_BOT"]
        port_opp = self.config["SLP"]["PORT_OPP"]
        selected_character : melee.Character = shit[self.config["SELECTED"]["CHARACTER"]]
        selected_stage : melee.Stage = shit2[self.config["SELECTED"]["STAGE"]]
        path=self.config["SLP"]["PATH"]

        testRun(path, selected_character, selected_stage, port_bot, port_opp)
        return ("success", None)
    
    
bm = BotManager()
bm.run()