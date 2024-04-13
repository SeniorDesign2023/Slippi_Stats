import melee
from GeneralBot.CharacterData import weights

class ActionData:
    def __init__(self, FD: melee.FrameData, character: melee.Character, action: melee.Action, hitFrames: list, totalFrames: int = None, 
                 chargeFrame: int = None, landingLag: int = None, lcancelled: int = None):
    
        self.character = character
        self.action  = action
        
        self.frange = FD.range_forward(character, action, 1)
        self.brange = FD.range_backward(character, action, 1)
        
        self.totalFrames = totalFrames
        self.chargeFrame = chargeFrame
        self.landingLag  = landingLag
        self.lcancelled  = lcancelled
        
        self.firstHit = hitFrames[0].get("start", FD.first_hitbox_frame(character, action))
        self.lastHit = hitFrames[-1].get("end", FD.last_hitbox_frame(character, action))
        
        dmg = -1
        kb = -1
        kbGrowth = -1
        kbWeight = -1
        angle = None
        electric = False
        
        # Hitboxes from the first hitframe
        tmp = 0
        for hbox in hitFrames[0].get("hitboxes", { None : None }): # i stg if python gives me a "cant iterate none" error jesus python just skip it
            dmg = hbox.get("damage", -1) if hbox.get("damage", -1) > dmg else dmg
            kb = hbox.get("baseKb", -1) if hbox.get("baseKb", -1) > kb else kb
            kbGrowth = hbox.get("kbGrowth", -1) if hbox.get("kbGrowth", -1) > kbGrowth else kbGrowth
            kbWeight = hbox.get("weightDepKb", -1) if hbox.get("weightDepKb", -1) > kbWeight else kbWeight
            electric = True if hbox.get("element", "normal") == "electric" else False
            angle = hbox.get("angle", None) if dmg > tmp else angle
            tmp = dmg

        self.dmg = dmg
        self.kb = kb
        self.kbGrowth = kbGrowth
        self.kbWeight = kbWeight
        self.angle = angle
        self.electric = electric
        self.kb1 = trueKb(self, weights[character], 1)
        self.kb60 = trueKb(self, weights[character], 60)
    
    def print(self):
        print(
            '{0:25} {1:>25}'.format(str(self.action), 
                "firstHit:" + str(self.firstHit or "NA")  
                + "\tlastHit:" + str(self.lastHit or "NA") 
                + "\ttotalFrames:" + str(self.totalFrames or "NA")
                + "\tchargeFrame:" + str(self.chargeFrame or "NA")
                + "\tlandingLag:" + str(self.landingLag or "NA")
                + "\tlcancelled:" + str(self.lcancelled or "NA")
                + "\tdmg:" + str(self.dmg or "NA")
                + "\tKB/GRW/WT: [" + str(self.kb or "NA") + "/"
                    + str(self.kbGrowth or "NA") + "/" + str(self.kbWeight or "NA") + "]"
                + "\tangle:" + str(self.angle or "NA")
                + "\telectric:" +str(self.electric or "NA")
                + "\tkb1/kb60: " + str(self.kb1)[0:4]+"-"+str(self.kb60)[0:4]
                )
            )
        
def trueKb(action: ActionData, weight: int = 80, percent: int = 1):
    if percent == 0: percent = 1
    if action.kbWeight > 0:
        return (((action.kbWeight * 10 * 0.05) + 1) * 1.4 * (200 / (weight + 100)) + 18)
    else:
        return (((percent * 0.1) + (action.dmg * percent * 0.05)) * 1.4 * (200 / (weight + 100)) + 18)