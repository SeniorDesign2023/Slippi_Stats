import melee
import sys
import math
from GeneralBot.CharacterData import CharacterData

# A GeneralizedAgent contains a action map (Acts) that maps actions to generally
# programmed functions that can work on any character.

# NOTE!!!: The generalized agent can either be provided a damageResponseFunction
# or will use a default one. This is checked at the start of each frame.

def positionVector(start_x: float, start_y: float, end_x: float, end_y: float): # should probably make a 'tools' file
    distance = [start_x - end_x, start_y - end_y]
    norm = math.sqrt(distance[0] ** 2 + distance[1] ** 2)
    return (-distance[0] / norm, -distance[1] / norm)

class GeneralizedAgent:
    def __init__(self, cd: CharacterData):
        
        self.cd = cd
        
        # maps from Actions to GeneralizedAgent functions
        self.Acts   = {
            melee.Action.GETUP_ATTACK       : self.getupAttack,
            melee.Action.EDGE_ATTACK_QUICK  : self.getupAttack,
            melee.Action.EDGE_ATTACK_SLOW   : self.getupAttack,
            melee.Action.GROUND_ATTACK_UP   : self.getupAttack,
            melee.Action.NEUTRAL_ATTACK_1 : self.jab, 
            melee.Action.DASH_ATTACK    : self.dashAttack,
            melee.Action.DOWNSMASH      : self.dsmash, 
            melee.Action.UPSMASH        : self.usmash, 
            melee.Action.FSMASH_MID     : self.fsmash, 
            melee.Action.DOWNTILT       : self.dtilt, 
            melee.Action.UPTILT         : self.utilt, 
            melee.Action.FTILT_MID      : self.ftilt, 
            melee.Action.FTILT_LOW      : self.ftil_l, 
            melee.Action.FTILT_HIGH     : self.ftilt_h,
            melee.Action.DAIR : self.dair, 
            melee.Action.UAIR : self.uair, 
            melee.Action.FAIR : self.fair, 
            melee.Action.NAIR : self.nair
            }
        
        self.gs : melee.GameState   = melee.GameState()         # game state
        self.ps : melee.PlayerState = melee.PlayerState()       # self player state
        self.es : melee.PlayerState = melee.PlayerState()       # enemy player state
        self.at : melee.AttackState = melee.AttackState(3)      # Attack state
                        
        self.release_buffer = { 0 : [] }    # framenum : [ (button) ]
        self.tilt_buffer = {                # framenum : [ (button, x , y) , (button, x, y) ]
            0 : [(melee.Button.BUTTON_MAIN, 0.5, 0.5)], 
            1 : [(melee.Button.BUTTON_C, 0.5, 0.5)] 
            }
        
        self.callback: function = False     # False if no callback, otherwise called ahead of other funcs

    def printAgent(self, ct: melee.Controller, func, file = sys.stdout):
        act = str(self.ps.action.value)+"-"+str(self.ps.action)+"(" + str(self.ps.action_frame) +")"
        iasa = str(self.iasa)
        jmps = str(self.ps.jumps_left)
        grnd = str(self.ps.on_ground) 
        bts = "BTS:["
        for btn in ct.current.button: bts += str(btn)[14]+" " if ct.current.button[btn] else ""
        m = "MS:" + str(ct.current.main_stick)
        c = "CS:" + str(ct.current.c_stick)
        shld = str(ct.current.l_shoulder) + "/" + str(ct.current.r_shoulder)
        print('{0:8} {1:>35} {2:>8} {3:>8} {4:>8} {5:>8} {6:>8} {7:>8} {8:>8} {9:>12} {10:>10}'.format(
            "",act,  "iasa:" + iasa, "jmp:" + jmps ,  "grnd:" + grnd , bts+"]", m, c, "L/R:" + shld, "fn:" + str(func)[33:38], "as:"+str(self.at)[12:]), end="\r", file=file)
        
    def nextState(self, _gs: melee.GameState):
        self.gs = _gs
        self.ps = self.gs.players[self.cd.PORT_SELF]
        self.es = self.gs.players[self.cd.PORT_ENEMY]
        self.at = self.cd.FD.attack_state(self.cd.CHARACTER, self.ps.action, self.ps.action_frame)
        self.iasa = self.cd.FD.iasa(self.ps.character,self.ps.action)
        
    def endState(self, ct: melee.Controller):
        bframes = list(self.release_buffer.keys())
        for bframe in bframes:# in all buffered frames
            if bframe <= self.gs.frame: # if buffer is <= the current frame
                buttons = self.release_buffer.pop(bframe)
                if buttons == None: continue
                for button in buttons: # pop buffer, release buttons
                    print("BufRelease: " + str(button), end="\r")
                    ct.release_button(button)
            else: break # future release, leave alone
            
        btframes = list(self.tilt_buffer.keys())
        for btframe in btframes:# in all buffered frames
            if btframe <= self.gs.frame: # if buffer is <= the current frame
                tuples = self.tilt_buffer.pop(btframe)
                if tuples == None: continue
                for tuple in tuples: # pop buffer, release buttons
                    print("BufTilt: " + str(tuple[0]) + str(tuple[1]) + str(tuple[2]), end="\r")
                    ct.tilt_analog(tuple[0], tuple[1], tuple[2])
            else: break # future release, leave alone 
    
    def checkButtonRelease(self, ct: melee.Controller, button: melee.Button):
        if ct.current.button[button]:
            ct.release_button(button)
            print("release X", end="\r")
            return True
        return False
    
    def checkCStickRelease(self, ct: melee.Controller):
        if not (ct.current.c_stick[0] == 0.5 and ct.current.c_stick[1] == 0.5):
            print("release C", end="\r")
            ct.tilt_analog(melee.Button.BUTTON_C,0.5, 0.5)
            return True
        return False
    
    def checkMStickRelease(self, ct: melee.Controller):
        if not (ct.current.main_stick[0] == 0.5 and ct.current.main_stick[1] == 0.5):
            ct.tilt_analog(melee.Button.BUTTON_MAIN,0.5, 0.5)
            print("release M", end="\r")
            return True
        return False
    
    def checkRShoulderRelease(self, ct: melee.Controller):
        if ct.current.r_shoulder != 0:
            ct.press_shoulder(melee.Button.BUTTON_L, 0)
            return True
        return False
        
    def appendRelease(self, framedAdded: int, button: melee.Button):
        prev = self.release_buffer.get(self.gs.frame + framedAdded, None)
        if prev == None: self.release_buffer[self.gs.frame + framedAdded] = [button]
        else: self.release_buffer[self.gs.frame + framedAdded] = prev.append(button)
        
    def appendTilt(self, framedAdded: int, button: melee.Button, x: float, y: float):
        prev = self.tilt_buffer.get(self.gs.frame + framedAdded, None)
        if prev == None: self.tilt_buffer[self.gs.frame + framedAdded] = [(button, x, y)]
        else: self.tilt_buffer[self.gs.frame + framedAdded] = prev.append((button, x, y))
       
    ### JUMPS ###         
    def shorthop(self, ct: melee.Controller, allowDoubleJump: bool = False): # use BUTTON_Y when immediate release
        if self.checkButtonRelease(ct, melee.Button.BUTTON_Y): return False
        if self.ps.jumps_left > 0 and self.iasa < 0:
            if (not allowDoubleJump and not self.ps.on_ground): return False
            ct.press_button(melee.Button.BUTTON_Y)
            self.appendRelease(2, melee.Button.BUTTON_Y)
            return True
        else: 
            return False
        
    def fullhop(self, ct: melee.Controller): # use BUTTON_X for buffered release
        if self.checkButtonRelease(ct, melee.Button.BUTTON_X): return False
        if self.ps.jumps_left > 0 and self.iasa < 0:
            ct.press_button(melee.Button.BUTTON_X)
            self.appendRelease(self.cd.FD.frames_until_dj_apex(self.ps), melee.Button.BUTTON_X)
            return True
        else:
            return False
        
    def hop(self, ct: melee.Controller, amt: float = 0.5):
        if self.checkButtonRelease(ct, melee.Button.BUTTON_X): return False
        if self.ps.jumps_left > 0 and self.iasa < 0:
            ct.press_button(melee.Button.BUTTON_X)
            self.appendRelease(int(self.cd.FD.frames_until_dj_apex(self.ps) * amt), melee.Button.BUTTON_X)
            return True
        else:
            return False
        
    def hop_to_y(self, ct: melee.Controller, yval: int, minDist: int):
        if self.ps.position.y + minDist >= yval:
            ct.release_button(melee.Button.BUTTON_X)
            return False
        elif self.ps.jumps_left > 0 and self.iasa < 0:
            ct.press_button(melee.Button.BUTTON_X)
            self.appendRelease(self.cd.FD.frames_until_dj_apex(self.ps), melee.Button.BUTTON_X)
            return True
        else:
            return False
        
    ### MOVEMENT ###
    def ffall(self, ct: melee.Controller):
        if self.ps.action.value > 29 and self.ps.action.value < 38: # falling values
            if self.checkMStickRelease(ct): return False
            ct.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
            return True
        else:
            return False
            
    
    def platFall(self, ct: melee.Controller):
        print("PLAT START", end="\r")
        if self.ps.position.y >= melee.stages.left_platform_position(self.gs)[0]:
            if self.ps.on_ground:
                # We want to plat fall, implies we will perform a move after the fall, release everything BUT main stick
                ct.release_button(melee.Button.BUTTON_A)
                ct.release_button(melee.Button.BUTTON_B)
                ct.release_button(melee.Button.BUTTON_X)
                ct.release_button(melee.Button.BUTTON_Z)
                ct.tilt_analog(melee.Button.BUTTON_C, 0.5, 0.5)
                if ct.current.main_stick[1] < 0.35 or self.ps.action == melee.Action.CROUCHING: 
                    ct.tilt_analog(melee.Button.BUTTON_MAIN, ct.current.main_stick[0], 0.5) # move to stick up before smashing stick down
                    self.appendTilt(1, melee.Button.BUTTON_MAIN, 0.5, 0.5) # because we return false, outside code does not know to waitFrames, enforce 0.5,0.5 on next frame
                    print("PLAT CENTERING", end="\r")
                elif self.iasa < 0:
                    print("PLAT READY", end="\r")
                    ct.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
                return False
            else:
                # no grounded, but above plat, keep x and tilt down
                print("PLAT ABOVE", end="\r")
                ct.tilt_analog(melee.Button.BUTTON_MAIN, ct.current.main_stick[0], 0.2)
                return False
        else:
            print("PLAT TRUE!", end="\r")
            # below platform, assume we fell through
            ct.tilt_analog(melee.Button.BUTTON_MAIN, ct.current.main_stick[0], 0.5)
            return True
        
        
    ### AERIALS ###      
    def uair(self, ct: melee.Controller): # up air (uses c-stick)
        if self.checkCStickRelease(ct) or self.checkButtonRelease(ct, melee.Button.BUTTON_A): return False
        print("uair btns free", end="\r")
        if not self.ps.on_ground and self.iasa < 0:
            print("uair true", end="\r")
            ct.tilt_analog(melee.Button.BUTTON_C, 0.5, 1)
            #self.appendTilt_unit(2, melee.Button.BUTTON_C, 0, 0)
            return True
        else: 
            ct.tilt_analog(melee.Button.BUTTON_C, 0.5, 0.5)
            return False
        
    def dair(self, ct: melee.Controller): # down air (uses c-stick)
        if self.checkCStickRelease(ct) or self.checkButtonRelease(ct, melee.Button.BUTTON_A): return False
        if not self.ps.on_ground and self.iasa < 0:
            ct.tilt_analog(melee.Button.BUTTON_C, 0.5, 0)
            #self.appendTilt_unit(2, melee.Button.BUTTON_C, 0, 0)
            return True
        else: 
            ct.tilt_analog(melee.Button.BUTTON_C, 0.5, 0.5)
            return False
        
    def fair(self, ct: melee.Controller): # forward air (uses c-stick)
        if self.checkCStickRelease(ct) or self.checkButtonRelease(ct, melee.Button.BUTTON_A): return False
        if not self.ps.on_ground and self.iasa < 0:
            ct.tilt_analog(melee.Button.BUTTON_C, int(self.ps.facing), 0.5)
            #self.appendTilt_unit(2, melee.Button.BUTTON_C, 0, 0)
            return True
        else: 
            ct.tilt_analog(melee.Button.BUTTON_C, 0, 0)
            return False
        
    def bair(self, ct: melee.Controller): # back air (uses c-stick)
        if self.checkCStickRelease(ct) or self.checkButtonRelease(ct, melee.Button.BUTTON_A): return False
        if not self.ps.on_ground and self.iasa < 0:
            ct.tilt_analog(melee.Button.BUTTON_C, int(not self.ps.facing), 0.5)
            #self.appendTilt_unit(2, melee.Button.BUTTON_C, 0, 0)
            return True
        else: 
            ct.tilt_analog(melee.Button.BUTTON_C, 0.5, 0.5)
            return False
        
    def nair(self, ct: melee.Controller): # neutral air (cannot c-stick)
        if self.checkCStickRelease(ct) or self.checkButtonRelease(ct, melee.Button.BUTTON_A): return False
        if not self.ps.on_ground and self.iasa < 0:
            startPos = ct.current.main_stick
            ct.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0.5)
            ct.press_button(melee.Button.BUTTON_A)
            return True
        else: 
            ct.release_button(melee.Button.BUTTON_A)
            return False       
            
    ### GROUND ATTACKS ###
    def dashAttack(self, ct: melee.Controller): # should usually be prioritized if dashing
        if self.checkCStickRelease(ct) or self.checkButtonRelease(ct, melee.Button.BUTTON_A): return False
        if self.ps.action.value > 18 and self.ps.action.value < 24:
            ct.press_button(melee.Button.BUTTON_A)
            return True
        else: # either in an attack or airborne, just release A
            ct.release_button(melee.Button.BUTTON_A)
            return False
        
    def jab(self, ct: melee.Controller):
        if self.ps.action.value > 18 and self.ps.action.value < 24: # dont dash attack, slow down
            ct.release_button(melee.Button.BUTTON_A)
            ct.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0.5)
            print("dashing", end="\r")
            return False
        if self.checkCStickRelease(ct) or self.checkButtonRelease(ct, melee.Button.BUTTON_A): return False
        print("jabbing!", end="\r")
        if self.ps.on_ground and self.iasa < 0: # jab if we can
            ct.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0.5)
            ct.press_button(melee.Button.BUTTON_A)
            return True
        else: # either in an attack or airborne, just release A
            print("just kidding :(", end="\r")
            ct.release_button(melee.Button.BUTTON_A)
            return False
        
    def dtilt(self, ct: melee.Controller): # down tilt
        if self.ps.action.value > 18 and self.ps.action.value < 24: # dont dash attack, slow down
            ct.release_button(melee.Button.BUTTON_A)
            ct.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0.5)
            return False
        if self.checkCStickRelease(ct) or self.checkButtonRelease(ct, melee.Button.BUTTON_A): return False
        if self.ps.on_ground and self.iasa < 0:
            ct.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0.2)
            ct.press_button(melee.Button.BUTTON_A)
            return True
        else:
            ct.release_button(melee.Button.BUTTON_A)
            return False
        
    def utilt(self, ct: melee.Controller): # up tilt
        if self.ps.action.value > 18 and self.ps.action.value < 24: # dont dash attack, slow down
            ct.release_button(melee.Button.BUTTON_A)
            ct.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0.5)
            return False
        if self.checkCStickRelease(ct) or self.checkButtonRelease(ct, melee.Button.BUTTON_A): return False
        if self.ps.on_ground and self.iasa < 0:
            startPos = ct.current.main_stick
            ct.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0.8)
            ct.press_button(melee.Button.BUTTON_A)
            return True
        else:
            ct.release_button(melee.Button.BUTTON_A)
            return False
    
    def ftilt(self, ct: melee.Controller): # forward tilt
        if self.ps.action.value > 18 and self.ps.action.value < 24: # dont dash attack, slow down
            ct.release_button(melee.Button.BUTTON_A)
            ct.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0.5)
            return False
        if self.checkCStickRelease(ct) or self.checkButtonRelease(ct, melee.Button.BUTTON_A): return False
        if self.ps.on_ground and self.iasa < 0:
            x = 0.7 if self.ps.facing else 0.3
            ct.tilt_analog(melee.Button.BUTTON_MAIN, x, 0.5)
            ct.press_button(melee.Button.BUTTON_A)
            return True
        else:
            ct.release_button(melee.Button.BUTTON_A)
            return False
        
    def ftilt_h(self, ct: melee.Controller): # upward angled forward tilt
        if self.ps.action.value > 18 and self.ps.action.value < 24: # dont dash attack, slow down
            ct.release_button(melee.Button.BUTTON_A)
            ct.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0.5)
            return False
        if self.checkCStickRelease(ct) or self.checkButtonRelease(ct, melee.Button.BUTTON_A): return False
        if self.ps.on_ground and self.iasa < 0:
            x = 0.7 if self.ps.facing else 0.3
            ct.tilt_analog(melee.Button.BUTTON_MAIN, x, 0.75)
            ct.press_button(melee.Button.BUTTON_A)
            return True
        else:
            ct.release_button(melee.Button.BUTTON_A)
            return False
        
    def ftil_l(self, ct: melee.Controller): # downward angled forward tilt
        if self.ps.action.value > 18 and self.ps.action.value < 24: # dont dash attack, slow down
            ct.release_button(melee.Button.BUTTON_A)
            ct.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0.5)
            return False
        if self.checkCStickRelease(ct) or self.checkButtonRelease(ct, melee.Button.BUTTON_A): return False
        if self.ps.on_ground and self.iasa < 0:
            x = 0.7 if self.ps.facing else 0.3
            ct.tilt_analog(melee.Button.BUTTON_MAIN, x, 0.25)
            ct.press_button(melee.Button.BUTTON_A)
            return True
        else:
            ct.release_button(melee.Button.BUTTON_A)
            return False
        
    ### SMASH ATTACKS ###
    def chargeSmash(self, ct: melee.Controller, distToRelease: int, x: float, y: float):
        if self.at == melee.AttackState.WINDUP: # already charging
            if self.gs.distance > distToRelease:
                ct.press_button(melee.Button.BUTTON_A)
            else:
                ct.release_button(melee.Button.BUTTON_A)
            return True
        if self.checkMStickRelease(ct) or self.checkCStickRelease(ct) or self.checkButtonRelease(ct, melee.Button.BUTTON_A): return False
        if self.ps.on_ground and self.iasa < 0: # not charging, can charge
            ct.tilt_analog(melee.Button.BUTTON_MAIN, x, y)
            ct.press_button(melee.Button.BUTTON_A)
            self.appendRelease(60, melee.Button.BUTTON_A) # max charge time
            return True
        else: # not charging and cannot charge
            ct.release_button(melee.Button.BUTTON_A)
            return False
    
    
    def usmash(self, ct: melee.Controller, distToRelease: int = 0):
        if self.ps.action.value > 18 and self.ps.action.value < 24: # dont dash attack, slow down
            ct.release_button(melee.Button.BUTTON_A)
            ct.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0.5)
            return False
        if distToRelease == 0:  # instant up-smash
            if self.checkCStickRelease(ct) or self.checkButtonRelease(ct, melee.Button.BUTTON_A): return False
            if self.ps.on_ground and self.iasa < 0:
                ct.tilt_analog(melee.Button.BUTTON_C, 0.5, 1)
                #self.appendTilt_unit(2, melee.Button.BUTTON_C, 0, 0)
                return True
            else: 
                ct.tilt_analog(melee.Button.BUTTON_C, 0.5, 0.5)
                return False
        
        else: # charge smash
            self.chargeSmash(ct, distToRelease, 0.5, 1)
            
    def dsmash(self, ct: melee.Controller, distToRelease: int = 0):
        if self.ps.action.value > 18 and self.ps.action.value < 24: # dont dash attack, slow down
            ct.release_button(melee.Button.BUTTON_A)
            ct.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0.5)
            return False
        if distToRelease == 0:  # instant down-smash
            if self.checkCStickRelease(ct) or self.checkButtonRelease(ct, melee.Button.BUTTON_A): return False
            if self.ps.on_ground and self.iasa < 0:
                ct.tilt_analog(melee.Button.BUTTON_C, 0.5, 0)
                #self.appendTilt_unit(2, melee.Button.BUTTON_C, 0, 0)
                return True
            else: 
                ct.tilt_analog(melee.Button.BUTTON_C, 0.5, 0.5)
                return False
        
        else: # charge smash
            self.chargeSmash(ct, distToRelease, 0.5, 0)
            
    def fsmash(self, ct: melee.Controller, distToRelease: int = 0):
        if self.ps.action.value > 18 and self.ps.action.value < 24: # dont dash attack, slow down
            ct.release_button(melee.Button.BUTTON_A)
            ct.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0.5)
            return False
        if distToRelease == 0:  # instant forward-smash
            if self.checkCStickRelease(ct) or self.checkButtonRelease(ct, melee.Button.BUTTON_A): return False
            if self.ps.on_ground and self.iasa < 0:
                ct.tilt_analog(melee.Button.BUTTON_C, int(self.ps.facing), 0.5)
                #self.appendTilt_unit(2, melee.Button.BUTTON_C, 0, 0)
                return True
            else: 
                ct.tilt_analog(melee.Button.BUTTON_C, 0.5, 0.5)
                return False
        
        else: # charge smash
            self.chargeSmash(ct, distToRelease, int(self.ps.facing), 0.5)
    
    def bsmash(self, ct: melee.Controller, distToRelease: int = 0):
        if self.ps.action.value > 18 and self.ps.action.value < 24: # dont dash attack, slow down
            ct.release_button(melee.Button.BUTTON_A)
            ct.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0.5)
            return False
        if distToRelease == 0:  # instant back-smash
            if self.checkCStickRelease(ct) or self.checkButtonRelease(ct, melee.Button.BUTTON_A): return False
            if self.ps.on_ground and self.iasa < 0:
                ct.tilt_analog(melee.Button.BUTTON_C, int(not self.ps.facing), 0)
                #self.appendTilt_unit(2, melee.Button.BUTTON_C, 0, 0)
                return True
            else: 
                ct.tilt_analog(melee.Button.BUTTON_C, 0.5, 0.5)
                return False
        
        else: # charge smash
            self.chargeSmash(ct, distToRelease, int(not self.ps.facing), 0.5)
            
    
    ### GRABS ###
    def grab(self, ct: melee.Controller):
        if self.checkButtonRelease(ct, melee.Button.BUTTON_Z): return False
        if not self.ps.on_ground: return False
        
    ### SPECIALS ###
    def upb(self, ct: melee.Controller):
        if self.checkButtonRelease(ct, melee.Button.BUTTON_B): return False
        if self.cd.FD.iasa(self.ps.character, self.ps.action) < 0:
            ct.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 1)
            ct.tilt_analog(melee.Button.BUTTON_C, 0.5, 0.5) # you can technically do B moves with the c-stick, avoid
            ct.press_button(melee.Button.BUTTON_B)
            return True
        else:
            ct.release_button(melee.Button.BUTTON_B)
            return False
        
    ### GETUP/EDGE ###
    def getupAttack(self, ct: melee.Controller):
        if self.checkButtonRelease(ct, melee.Button.BUTTON_A): return False
        if self.cd.FD.iasa(self.ps.character, self.ps.action) < 0 and self.ps.action.value in [192, 252, 253]: # TODO: might need 193 too
            ct.press_button(melee.Button.BUTTON_A)
            return True
        else:
            return False
        
    def ledgeDrop(self, ct: melee.Controller):
        if self.ps.action == melee.Action.EDGE_HANGING:
            ct.tilt_analog(melee.Button.BUTTON_C, int(not self.ps.facing), 0)
            return True
        else:
            return False
        
    ### SHOULDERS ###
    def rightShoulder(self, amt, ct: melee.Controller):
        if self.checkRShoulderRelease(ct): return False
        ct.press_shoulder(melee.Button.BUTTON_R, amt)
        return True
    

    # TODO: Looping methods should become their own chains/tactics at some point
    ### LOOPING ### 
    def looping_ledgeDash(self, ct: melee.Controller):
        if self.ps.action == melee.Action.EDGE_HANGING:     # Hanging
            if self.checkCStickRelease(ct) or self.checkMStickRelease(ct) or self.checkButtonRelease(ct, melee.Button.BUTTON_A): 
                print("EDGE HANGING: stick down, reset and wait: 2")
                return 2
            else:
                ct.tilt_analog(melee.Button.BUTTON_C, int(not self.ps.position.x < 0), 0.5)
                print("EDGE HANGING: dropping, tilt stick: 1")
                return 1
                                                            # Jumping
        if self.ps.action.value > 24 and self.ps.action.value < 29: 
            print("ALREADY JUMPING")

            if (self.ps.ecb_bottom[1] + self.ps.position.y) > 0:   # Above ledge, this 0 height varies by character
                ct.tilt_analog(melee.Button.BUTTON_MAIN, int(self.ps.facing), 0.4)
                ct.release_button(melee.Button.BUTTON_X)
                ct.press_button(melee.Button.BUTTON_R)
                self.appendRelease(5, melee.Button.BUTTON_R)
                print("LEDGEDASH: 2")
                return 2
            else:                                           # Below ledge
                print("BELOW LEDGE: 0")
                self.hop_to_y(ct, 50, 10)
                return 0
        
        if self.ps.position.y < -50 or self.ps.on_ground:   # Fell too far or on ground
            print("fell too far or on ground: 0, reset callback")
            self.callback = False
            ct.release_all()
            return 0
                                                            # Falling
        if self.ps.jumps_left > 0 and self.ps.action.value < 35 and self.ps.action.value > 28:
            print("FALLING")
            ct.tilt_analog(melee.Button.BUTTON_MAIN, int(self.ps.facing)*0.5, 1)
            if self.hop_to_y(ct, 25, 0):
                print("START JUMP: 2")
                return 2
            else: 
                print("CANNOT JUMP: 0")
                return 0
        else:                                               # Uh oh
            print("UH OH")
            self.callback = False
            ct.release_all()
            return 0
        
    def looping_platFall(self, ct: melee.Controller):
        print("PLAT START", end="\r")
        if self.ps.position.y >= melee.stages.left_platform_position(self.gs)[0]:
            if self.ps.on_ground:
                # We want to plat fall, implies we will perform a move after the fall, release everything BUT main stick
                ct.release_button(melee.Button.BUTTON_A)
                ct.release_button(melee.Button.BUTTON_B)
                ct.release_button(melee.Button.BUTTON_X)
                ct.release_button(melee.Button.BUTTON_Z)
                ct.tilt_analog(melee.Button.BUTTON_C, 0.5, 0.5)
                if ct.current.main_stick[1] < 0.4 or self.ps.action == melee.Action.CROUCHING: 
                    ct.tilt_analog(melee.Button.BUTTON_MAIN, ct.current.main_stick[0], 0.5) # move to stick up before smashing stick down
                    self.appendTilt(1, melee.Button.BUTTON_MAIN, 0.5, 0.5) # because we return false, outside code does not know to waitFrames, enforce 0.5,0.5 on next frame
                    print("PLAT CENTERING", end="\r")
                    return 2
                elif self.iasa < 0:
                    print("PLAT READY", end="\r")
                    ct.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
                return 2
            else:
                # no grounded, but above plat, keep x and tilt down
                print("PLAT ABOVE", end="\r")
                ct.tilt_analog(melee.Button.BUTTON_MAIN, ct.current.main_stick[0], 0.2)
                self.callback = False
                return 0
        else:
            print("PLAT TRUE!", end="\r")
            # below platform, assume we fell through
            ct.tilt_analog(melee.Button.BUTTON_MAIN, ct.current.main_stick[0], 0.5)
            self.callback = False
            return 0

        

        
        
        