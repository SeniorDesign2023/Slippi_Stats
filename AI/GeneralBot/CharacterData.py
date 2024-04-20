import melee
    
# dict of Character ID from libmelee to filenames
characterDict = {
    melee.Character.BOWSER: 	'framedata-json-fullhitboxes/Bowser.framedata.json',
    melee.Character.CPTFALCON: 'framedata-json-fullhitboxes/Captain Falcon.framedata.json',
    melee.Character.DK:     'framedata-json-fullhitboxes/Donkey Kong.framedata.json',
    melee.Character.DOC: 	'framedata-json-fullhitboxes/Dr Mario.framedata.json',
    melee.Character.FALCO: 	'framedata-json-fullhitboxes/Falco.framedata.json',
    melee.Character.FOX: 	'framedata-json-fullhitboxes/Fox.framedata.json',
    melee.Character.GAMEANDWATCH: 	'framedata-json-fullhitboxes/Game & Watch.framedata.json',
    melee.Character.GANONDORF: 	'framedata-json-fullhitboxes/Ganondorf.framedata.json',
    melee.Character.JIGGLYPUFF: 	'framedata-json-fullhitboxes/Jigglypuff.framedata.json',
    melee.Character.KIRBY: 	'framedata-json-fullhitboxes/Kirby.framedata.json',
    melee.Character.LINK: 	'framedata-json-fullhitboxes/Link.framedata.json',
    melee.Character.LUIGI: 	'framedata-json-fullhitboxes/Luigi.framedata.json',
    melee.Character.MARIO: 	'framedata-json-fullhitboxes/Mario.framedata.json',
    melee.Character.MARTH: 	'framedata-json-fullhitboxes/Marth.framedata.json',
    melee.Character.MEWTWO: 	'framedata-json-fullhitboxes/Mewtwo.framedata.json',
    melee.Character.NANA: 	'framedata-json-fullhitboxes/Ice Climbers - Nana.framedata.json',
    melee.Character.NESS: 	'framedata-json-fullhitboxes/Ness.framedata.json',
    melee.Character.PEACH: 	'framedata-json-fullhitboxes/Peach.framedata.json',
    melee.Character.PICHU: 	'framedata-json-fullhitboxes/Pichu.framedata.json',
    melee.Character.PIKACHU: 	'framedata-json-fullhitboxes/Pikachu.framedata.json',
    melee.Character.POPO: 	'framedata-json-fullhitboxes/Ice Climbers - Popo.framedata.json',
    melee.Character.ROY: 	'framedata-json-fullhitboxes/Roy.framedata.json',
    melee.Character.SAMUS: 	'framedata-json-fullhitboxes/Samus.framedata.json',
    melee.Character.SHEIK: 	'framedata-json-fullhitboxes/Sheik.framedata.json',
    melee.Character.YLINK: 	'framedata-json-fullhitboxes/Young Link.framedata.json',
    melee.Character.YOSHI: 	'framedata-json-fullhitboxes/Yoshi.framedata.json',
    melee.Character.ZELDA: 	'framedata-json-fullhitboxes/Zelda.framedata.json'
}

# Maps from Characters to Weight Values
weights = {
    melee.Character.BOWSER:	117,
    melee.Character.CPTFALCON:	104,
    melee.Character.DK:	    114,
    melee.Character.DOC:	100,
    melee.Character.FALCO:	80,
    melee.Character.FOX:	75,
    melee.Character.GAMEANDWATCH:60,
    melee.Character.GANONDORF:	109,
    melee.Character.JIGGLYPUFF:	60,
    melee.Character.KIRBY:	70,
    melee.Character.LINK:	104,
    melee.Character.LUIGI:	100,
    melee.Character.MARIO:	100,
    melee.Character.MARTH:	87,
    melee.Character.MEWTWO:	85,
    melee.Character.NANA:	88,
    melee.Character.NESS:	94,
    melee.Character.PEACH:	90,
    melee.Character.PICHU:	55,
    melee.Character.PIKACHU:80,
    melee.Character.POPO:	88,
    melee.Character.ROY:	85,
    melee.Character.SAMUS:	110,
    melee.Character.SHEIK:	90,
    melee.Character.YLINK:	108,
    melee.Character.YOSHI:	85,
    melee.Character.ZELDA:	90
}



# Maps from Actions to framdata.json names
defensiveAttacks = {
    melee.Action.GETUP_ATTACK: None,
    melee.Action.EDGE_ATTACK_QUICK: None,
    melee.Action.EDGE_ATTACK_SLOW: None,
    melee.Action.GROUND_ATTACK_UP: None
}

groundedAttacks = {
    melee.Action.NEUTRAL_ATTACK_1: "jab1",
    melee.Action.DASH_ATTACK: "dashattack",
    melee.Action.DOWNSMASH: "dsmash",
    melee.Action.UPSMASH: "usmash",
    melee.Action.FSMASH_MID: "fsmash_m",
    melee.Action.DOWNTILT: "dtilt",
    melee.Action.UPTILT: "utilt",
    melee.Action.FTILT_MID: "ftilt_m",
}

aerialAttacks = {
    melee.Action.DAIR: "dair",
    melee.Action.UAIR: "uair",
    melee.Action.FAIR: "fair",
    melee.Action.NAIR: "nair",
}

import json
import os
from GeneralBot.ActionData import ActionData

class CharacterData:
    def __init__(self, character: melee.Character, opp_character: melee.Character, stage_selected: melee.Stage, PORT_SELF: int, PORT_ENEMY: int):
        self.FD = melee.framedata.FrameData()
        self.CHARACTER = character
        self.STAGE_SELECTED = stage_selected
        self.PORT_SELF = PORT_SELF
        self.PORT_ENEMY = PORT_ENEMY
        
        self.MAX_JUMPS = self.FD.max_jumps(character)
        self.RIGHT_EDGE_X = melee.stages.EDGE_POSITION[self.STAGE_SELECTED]
        self.LEFT_EDGE_X = -melee.stages.EDGE_POSITION[self.STAGE_SELECTED]
        
        print("RIGHT: " + str(self.RIGHT_EDGE_X))
        print("LEFT: " + str(self.LEFT_EDGE_X))
        
        self.ENEMY_CHARACTER = opp_character 
        self.ENEMY_WEIGHT = characterDict[opp_character]
        
        print(characterDict[character])
        f = open(os.path.join(os.path.dirname(__file__),characterDict[self.CHARACTER]), "r")
        betterFrameData: dict = json.load(f)
        f.close
        
        self.groundAtt = dict(groundedAttacks)
        self.aerialAtt = dict(aerialAttacks)
        
        

        for key, val in groundedAttacks.items():
            att: dict = betterFrameData.get(val, None)
            if att == None: continue
            totalFrames = att.get("totalFrames", None)
            chargeFrame = att.get("chargeFrame", None)
            iasa = att.get("iasa", None)
            landingLag = att.get("landingLag", None)
            lcancelled = att.get("lcancelledLandingLag", None)
            hitFrames = att.get("hitFrames", None)
            
            totalFrames = iasa if iasa is not None else totalFrames # iasa means move can be interupted before totalFrames
            self.groundAtt[key] = ActionData(self.FD, character, key, hitFrames, totalFrames,
                                             chargeFrame, landingLag, lcancelled)
        
        for key, val in aerialAttacks.items():
            att: dict = betterFrameData.get(val, None)
            totalFrames = att.get("totalFrames", None)
            chargeFrame = att.get("chargeFrame", None)
            iasa = att.get("iasa", None)
            landingLag = att.get("landingLag", None)
            lcancelled = att.get("lcancelledLandingLag", None)
            hitFrames = att.get("hitFrames", None)
            
            totalFrames = iasa if iasa is not None else totalFrames
            self.aerialAtt[key] = ActionData(self.FD, character, key, hitFrames, totalFrames,
                                             chargeFrame, landingLag, lcancelled)

        self.groundAtt_first : list[ActionData]  = sorted(self.groundAtt.values(), key=lambda att: att.firstHit)
        self.groundAtt_short : list[ActionData]  = sorted(self.groundAtt_first, key=lambda att: att.totalFrames)
        self.groundAtt_less60 : list[ActionData] = sorted(self.groundAtt_first, key=lambda att: att.kb1, reverse=True)
        self.groundAtt_abov60 : list[ActionData] = sorted(self.groundAtt_first, key=lambda att: att.kb60, reverse=True)
        
        self.aerialAtt_first : list[ActionData]  = sorted(self.aerialAtt.values(), key=lambda att: att.firstHit)
        self.aerialAtt_short : list[ActionData]  = sorted(self.aerialAtt_first, key=lambda att: att.lcancelled + att.firstHit)
        self.aerialAtt_lcncl : list[ActionData]  = sorted(self.aerialAtt_first, key=lambda att: att.totalFrames) 
        self.aerialAtt_less60 : list[ActionData] = sorted(self.aerialAtt_first, key=lambda att: att.kb1, reverse=True)
        self.aerialAtt_abov60 : list[ActionData] = sorted(self.aerialAtt_first, key=lambda att: att.kb60, reverse=True)
        
        print("\n--BOT (" + str(character) + ") vs. PLR (" + str(opp_character) + ")")
        print("\ngroundAtt_first")
        for action in self.groundAtt_first: action.print()
        print("\ngroundAtt_short")
        for action in self.groundAtt_short: action.print()
        print("\ngroundAtt_less60")
        for action in self.groundAtt_less60: action.print()
        print("\ngroundAtt_abov60")
        for action in self.groundAtt_abov60: action.print()
        
        print("\naerialAtt_first")
        for action in self.aerialAtt_first: action.print()
        print("\naerialAtt_short")
        for action in self.aerialAtt_short: action.print()
        print("\naerialAtt_lcncl")
        for action in self.aerialAtt_short: action.print()
        print("\naerialAtt_less60")
        for action in self.aerialAtt_less60: action.print()
        print("\naerialAtt_abov60")
        for action in self.aerialAtt_abov60: action.print()  
        