import melee
import json
import os
from ActionData import ActionData

# dict of Character ID from libmelee to filenames
characterDict = {
    melee.Character.BOWSER	 : 	'framedata-json-fullhitboxes\\Bowser.framedata.json',
    melee.Character.CPTFALCON	 :'framedata-json-fullhitboxes\\Captain Falcon.framedata.json',
    melee.Character.DK:'framedata-json-fullhitboxes\\Donkey Kong.framedata.json',
    melee.Character.DOC	 : 	'framedata-json-fullhitboxes\\Dr Mario.framedata.json'	,
    melee.Character.FALCO	 : 	'framedata-json-fullhitboxes\\Falco.framedata.json'	,
    melee.Character.FOX	 : 	'framedata-json-fullhitboxes\\Fox.framedata.json'	,
    melee.Character.GAMEANDWATCH	 : 	'framedata-json-fullhitboxes\\Game & Watch.framedata.json'	,
    melee.Character.GANONDORF	 : 	'framedata-json-fullhitboxes\\Ganondorf.framedata.json'	,
    melee.Character.JIGGLYPUFF	 : 	'framedata-json-fullhitboxes\\Jigglypuff.framedata.json'	,
    melee.Character.KIRBY	 : 	'framedata-json-fullhitboxes\\Kirby.framedata.json'	,
    melee.Character.LINK	 : 	'framedata-json-fullhitboxes\\Link.framedata.json'	,
    melee.Character.LUIGI	 : 	'framedata-json-fullhitboxes\\Luigi.framedata.json'	,
    melee.Character.MARIO	 : 	'framedata-json-fullhitboxes\\Mario.framedata.json'	,
    melee.Character.MARTH	 : 	'framedata-json-fullhitboxes\\Marth.framedata.json'	,
    melee.Character.MEWTWO	 : 	'framedata-json-fullhitboxes\\Mewtwo.framedata.json'	,
    melee.Character.NANA	 : 	'framedata-json-fullhitboxes\\Ice Climbers - Nana.framedata.json'	,
    melee.Character.NESS	 : 	'framedata-json-fullhitboxes\\Ness.framedata.json'	,
    melee.Character.PEACH	 : 	'framedata-json-fullhitboxes\\Peach.framedata.json'	,
    melee.Character.PICHU	 : 	'framedata-json-fullhitboxes\\Pichu.framedata.json'	,
    melee.Character.PIKACHU	 : 	'framedata-json-fullhitboxes\\Pikachu.framedata.json'	,
    melee.Character.POPO	 : 	'framedata-json-fullhitboxes\\Ice Climbers - Popo.framedata.json'	,
    melee.Character.ROY	 : 	'framedata-json-fullhitboxes\\Roy.framedata.json'	,
    melee.Character.SAMUS	 : 	'framedata-json-fullhitboxes\\Samus.framedata.json'	,
    melee.Character.SHEIK	 : 	'framedata-json-fullhitboxes\\Sheik.framedata.json'	,
    melee.Character.YLINK	 : 	'framedata-json-fullhitboxes\\Young Link.framedata.json'	,
    melee.Character.YOSHI	 : 	'framedata-json-fullhitboxes\\Yoshi.framedata.json'	,
    melee.Character.ZELDA	 : 	'framedata-json-fullhitboxes\\Zelda.framedata.json'
    }



# Maps from Actions to framdata.json names
defensiveAttacks = {
    melee.Action.GETUP_ATTACK : None,
    melee.Action.EDGE_ATTACK_QUICK: None,
    melee.Action.EDGE_ATTACK_SLOW: None,
    melee.Action.GROUND_ATTACK_UP: None
    }

groundedAttacks =   {
    melee.Action.NEUTRAL_ATTACK_1: "jab1",
    melee.Action.DASH_ATTACK: "dashattack",
    melee.Action.DOWNSMASH: "dsmash",
    melee.Action.UPSMASH: "usmash",
    melee.Action.FSMASH_MID: "fsmash_m", 
    melee.Action.DOWNTILT: "dtilt",
    melee.Action.UPTILT: "utilt",
    melee.Action.FTILT_MID: "ftilt_m",
    melee.Action.FTILT_LOW: "ftilt_l",
    melee.Action.FTILT_HIGH: "ftilt_h",
    }
    
aerialAttacks = {
    melee.Action.DAIR: "dair",
    melee.Action.UAIR: "uair",
    melee.Action.FAIR: "fair",
    melee.Action.NAIR: "nair",
    }

class CharacterData:
    def __init__(self, character: melee.Character, stage_selected: melee.Stage, PORT_SELF: int, PORT_ENEMY: int):
        self.FD             = melee.framedata.FrameData()
        self.CHARACTER      = character
        self.STAGE_SELECTED = stage_selected
        self.PORT_SELF      = PORT_SELF
        self.PORT_ENEMY     = PORT_ENEMY
        self.MAX_JUMPS      = self.FD.max_jumps(character)
        self.RIGHT_EDGE_X   = melee.stages.EDGE_POSITION[self.STAGE_SELECTED]
        self.LEFT_EDGE_X    = -melee.stages.EDGE_POSITION[self.STAGE_SELECTED]
        self.PLAT_RIGHT     = melee.stages.right_platform_position(self.STAGE_SELECTED)
        self.PLAT_LEFT      = melee.stages.left_platform_position(self.STAGE_SELECTED)
        
        GR_ATTACK_FIRSTFRAME = sorted(groundedAttacks, key = lambda ac: self.FD.first_hitbox_frame(character, ac.value))
        self.GR_ATT_FIRSTFRAME = dict(map(lambda ac: (ac.name, self.FD.first_hitbox_frame(character, ac)), GR_ATTACK_FIRSTFRAME))
            
        GR_ATTACK_LEASTFRAME = sorted(GR_ATTACK_FIRSTFRAME, key = lambda ac: self.FD.iasa(character, ac))
        self.GR_ATT_LEASTFRAME = dict(map(lambda ac: (ac.name, self.FD.iasa(character, ac)), GR_ATTACK_LEASTFRAME))
        
        GR_ATTACK_MOSTFRAME = sorted(GR_ATTACK_FIRSTFRAME, key = lambda ac: self.FD.last_hitbox_frame(character, ac) - self.FD.first_hitbox_frame(character, ac))
        self.GR_ATT_MOSTFRAME = dict(map(lambda ac: (ac.name, self.FD.last_hitbox_frame(character, ac) - self.FD.first_hitbox_frame(character, ac)), GR_ATTACK_MOSTFRAME))
        
        print(self.GR_ATT_FIRSTFRAME)
        print(self.GR_ATT_LEASTFRAME)
        print(self.GR_ATT_MOSTFRAME)
        
        f = open(os.path.join(os.path.dirname(__file__), characterDict[self.CHARACTER]), "r")
        betterFrameData: dict = json.load(f)
        f.close
        
        self.groundAtt = dict(groundedAttacks,)
        self.aerialAtt = dict(aerialAttacks)
        #self.defensAtt = dict(defensiveAttacks)
        
        for key, val in groundedAttacks.items():
            att: dict = betterFrameData.get(val, None)
            totalFrames = att.get("totalFrames"         , None)
            chargeFrame = att.get("chargeFrame"         , None)
            iasa        = att.get("iasa"                , None)
            landingLag  = att.get("landingLag"          , None)
            lcancelled  = att.get("lcancelledLandingLag", None)
            hitFrames   = att.get("hitFrames", None)
            self.groundAtt[key] = ActionData(self.FD, character, key, hitFrames, totalFrames, 
                                             chargeFrame, iasa, landingLag, lcancelled)
            
        for key, val in aerialAttacks.items():
            att: dict = betterFrameData.get(val, None)
            totalFrames = att.get("totalFrames"         , None)
            chargeFrame = att.get("chargeFrame"         , None)
            iasa        = att.get("iasa"                , None)
            landingLag  = att.get("landingLag"          , None)
            lcancelled  = att.get("lcancelledLandingLag", None)
            hitFrames   = att.get("hitFrames", None)
            self.aerialAtt[key] = ActionData(self.FD, character, key, hitFrames, totalFrames, 
                                             chargeFrame, iasa, landingLag, lcancelled)
        
        self.groundAtt_first = sorted(self.groundAtt.values(), key = lambda att: att.firstHit)
        for actionData in self.groundAtt_first: print(str(actionData.firstHit) + "  " + str(actionData.action))    
        
            
        
