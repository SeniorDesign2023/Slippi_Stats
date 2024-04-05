import melee

class ActionData:
    def __init__(self, FD: melee.FrameData, character: int, action: int, hitFrames: list, totalFrames: int = None, 
                 chargeFrame: int = None, iasa: int = None, landingLag: int = None, lcancelled: int = None):
    
        self.character = character
        self.action  = action
        
        self.frange = FD.range_forward(character, action, 1)
        self.brange = FD.range_backward(character, action, 1)
        
        self.totalFrames = totalFrames
        self.chargeFrame = chargeFrame
        self.iasa        = iasa
        self.landingLag  = landingLag
        self.lcancelled  = lcancelled
        
        self.firstHit = hitFrames[0].get("start", FD.first_hitbox_frame(character, action))
        self.lastHit = hitFrames[-1].get("end", FD.last_hitbox_frame(character, action))
        
        dmg = -1
        kb = -1
        kbscale = -1
        angle = None
        score = 1
        
        # Hitboxes from the first hitframe
        for hbox in hitFrames[0].get("hitboxes", { None : None }): # i stg if python gives me a "cant iterate none" error jesus python just skip it
            dmg = hbox.get("damage", -1) if hbox.get("damage", -1) > dmg else dmg
            kb = hbox.get("baseKb", -1) if hbox.get("baseKb", -1) > kb else kb
            kbscale = hbox.get("kbGrowth", 0) if hbox.get("kbGrowth", -1) > kbscale else kbscale

            prevScore = score
            score = (hbox.get("damage", -1)+1) * (hbox.get("baseKb", -1)+1) * (hbox.get("kbGrowth", -1)+1)
            angle = hbox.get("angle", None) if prevScore > score else angle

        self.dmg = dmg
        self.kb = kb
        self.kbscale = kbscale
        self.angle = score