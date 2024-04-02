import melee

class GeneralizedAgent:
    def __init__(self, fd: melee.FrameData, port_self: int, port_enemy: int):
        
        self.PORT_SELF = port_self
        self.PORT_ENEMY = port_enemy
        self.FD = fd
        
        self.gs = melee.GameState()
        self.ps = melee.PlayerState()
        self.es = melee.PlayerState()
                        
        self.release_buffer = { 0 : [] }
        self.tilt_buffer = { 0 : [(melee.Button.BUTTON_MAIN, 0, 0)] } # [ (button, x , y) , (button, x, y) ]
        
    def nextState(self, _gs: melee.GameState):
        self.gs = _gs
        self.ps = self.gs.players[self.PORT_SELF]
        self.es = self.gs.players[self.PORT_ENEMY]
        
    def endState(self, _gs: melee.GameState, ct: melee.Controller):
        bframes = list(self.release_buffer.keys())
        for bframe in bframes:# in all buffered frames
            if bframe <= self.gs.frame: # if buffer is <= the current frame
                buttons = self.release_buffer.pop(bframe)
                if buttons == None: continue
                for button in buttons: # pop buffer, release buttons
                    print(button)
                    ct.release_button(button)
            else: break # future release, leave alone
            
        btframes = list(self.tilt_buffer.keys())
        for btframe in btframes:# in all buffered frames
            if btframe <= self.gs.frame: # if buffer is <= the current frame
                tuples = self.tilt_buffer.pop(btframe)
                if tuples == None: continue
                for tuple in tuples: # pop buffer, release buttons
                    print(tuple)
                    ct.tilt_analog_unit(tuple[0], tuple[1], tuple[2])
            else: break # future release, leave alone 
    
    def checkButtonRelease(self, ct: melee.Controller, button: melee.Button):
        if ct.current.button[button]:
            ct.release_button(button)
            return True
        return False
    
    def checkCStickRelease(self, ct: melee.Controller):
        if ct.current.c_stick != tuple[0.5, 0.5]:
            ct.tilt_analog_unit(melee.Button.BUTTON_C,0, 0)
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
        if self.ps.jumps_left > 0 and not ct.current.button[melee.Button.BUTTON_Y]:
            if (not allowDoubleJump and not self.ps.on_ground): return False
            ct.press_button(melee.Button.BUTTON_Y)
            self.appendRelease(1, melee.Button.BUTTON_Y)
            return True
        else: 
            return False
        
    def fullhop(self, ct: melee.Controller): # use BUTTON_X for buffered release
        if self.checkButtonRelease(ct, melee.Button.BUTTON_X): return False
        if self.ps.jumps_left > 0 and not ct.current.button[melee.Button.BUTTON_X]:
            ct.press_button(melee.Button.BUTTON_X)
            self.appendRelease(self.FD.frames_until_dj_apex(self.ps), melee.Button.BUTTON_X)
        else:
            return False
        
    def hop(self, ct: melee.Controller, amt: float = 0.5):
        if self.checkButtonRelease(ct, melee.Button.BUTTON_X): return False
        if self.ps.jumps_left > 0 and not ct.current.button[melee.Button.BUTTON_X]:
            ct.press_button(melee.Button.BUTTON_X)
            self.appendRelease(int(self.FD.frames_until_dj_apex(self.ps) * amt), melee.Button.BUTTON_X)
        else:
            return False
        
    def hop_to_y(self, ct: melee.Controller, yval: int, minDist: int):
        if self.ps.position.y + minDist >= yval:
            ct.release_button(melee.Button.BUTTON_X)
            return True
        elif self.ps.jumps_left > 0 and not ct.current.button[melee.Button.BUTTON_X]:
            if self.checkButtonRelease(ct, melee.Button.BUTTON_X): return False
            ct.press_button(melee.Button.BUTTON_X)
            self.appendRelease(self.FD.frames_until_dj_apex(self.ps), melee.Button.BUTTON_X)
            return True
        else:
            return False
        
        
    ### AERIALS ###      
    def uair(self, ct: melee.Controller): # up air (uses c-stick)
        if self.checkCStickRelease(ct): return False
        if not self.ps.on_ground and self.FD.iasa(self.ps.character,self.ps.action) <= 0:
            ct.tilt_analog_unit(melee.Button.BUTTON_C, 0, 1)
            self.appendTilt(1, melee.Button.BUTTON_C, 0, 0)
            return True
        else: 
            ct.tilt_analog_unit(melee.Button.BUTTON_C, 0, 0)
            return False
        
    def dair(self, ct: melee.Controller): # down air (uses c-stick)
        if self.checkCStickRelease(ct): return False
        if not self.ps.on_ground and self.FD.iasa(self.ps.character,self.ps.action) <= 0:
            ct.tilt_analog_unit(melee.Button.BUTTON_C, 0, -1)
            self.appendTilt(1, melee.Button.BUTTON_C, 0, 0)
            return True
        else: 
            ct.tilt_analog_unit(melee.Button.BUTTON_C, 0, 0)
            return False
        
    def fair(self, ct: melee.Controller): # forward air (uses c-stick)
        if self.checkCStickRelease(ct): return False
        if not self.ps.on_ground and self.FD.iasa(self.ps.character,self.ps.action) <= 0:
            ct.tilt_analog_unit(melee.Button.BUTTON_C, 1, 0)
            self.appendTilt(1, melee.Button.BUTTON_C, 0, 0)
            return True
        else: 
            ct.tilt_analog_unit(melee.Button.BUTTON_C, 0, 0)
            return False
        
    def bair(self, ct: melee.Controller): # back air (uses c-stick)
        if self.checkCStickRelease(ct): return False
        if not self.ps.on_ground and self.FD.iasa(self.ps.character,self.ps.action) <= 0:
            ct.tilt_analog_unit(melee.Button.BUTTON_C, -1, 0)
            self.appendTilt(1, melee.Button.BUTTON_C, 0, 0)
            return True
        else: 
            ct.tilt_analog_unit(melee.Button.BUTTON_C, 0, 0)
            return False
        
    def nair(self, ct: melee.Controller): # neutral air (cannot c-stick)
        if self.checkButtonRelease(ct, melee.Button.BUTTON_A): return False
        if not self.ps.on_ground and self.FD.iasa(self.ps.character,self.ps.action) <= 0:
            startPos = ct.current.main_stick
            ct.tilt_analog_unit(melee.Button.BUTTON_MAIN, 0, 0)
            ct.press_button(melee.Button.BUTTON_A)
            return True
        else: 
            ct.release_button(melee.Button.BUTTON_A)
            return False       
            
    ### GROUND ATTACKS ###
    def dashAttack(self, ct: melee.Controller): # should usually be prioritized if dashing
        if self.checkButtonRelease(ct, melee.Button.BUTTON_A): return False
        if self.ps.action == melee.Action.DASHING and self.FD.iasa(self.ps.character,self.ps.action) <= 0:
            ct.press_button(melee.Button.BUTTON_A)
            return True
        else: # either in an attack or airborne, just release A
            ct.release_button(melee.Button.BUTTON_A)
            return False
        
    def jab(self, ct: melee.Controller):
        if self.ps.action == melee.Action.DASHING: # dont dash attack, slow down
            ct.release_button(melee.Button.BUTTON_A)
            ct.tilt_analog_unit(melee.Button.BUTTON_MAIN, 0, -1)
            return False
        if self.checkButtonRelease(ct, melee.Button.BUTTON_A): return False
        if self.ps.on_ground and self.FD.iasa(self.ps.character,self.ps.action) <= 0: # jab if we can
            ct.tilt_analog_unit(melee.Button.BUTTON_MAIN, 0, 0)
            ct.press_button(melee.Button.BUTTON_A)
            return True
        else: # either in an attack or airborne, just release A
            ct.release_button(melee.Button.BUTTON_A)
            return False
        
    def dtilt(self, ct: melee.Controller): # forward tilt
        if self.ps.action == melee.Action.DASHING: # dont dash attack, slow down
            ct.release_button(melee.Button.BUTTON_A)
            ct.tilt_analog_unit(melee.Button.BUTTON_MAIN, -1, 0)
            return False
        if self.checkButtonRelease(ct, melee.Button.BUTTON_A): return False
        if self.ps.on_ground and self.FD.iasa(self.ps.character,self.ps.action) <= 0:
            startPos = ct.current.main_stick
            ct.tilt_analog_unit(melee.Button.BUTTON_MAIN, -0.5, 0)
            ct.press_button(melee.Button.BUTTON_A)
            return True
        else:
            ct.release_button(melee.Button.BUTTON_A)
            return False
    
    def ftilt(self, ct: melee.Controller): # forward tilt
        if self.ps.action == melee.Action.DASHING: # dont dash attack, slow down
            ct.release_button(melee.Button.BUTTON_A)
            ct.tilt_analog_unit(melee.Button.BUTTON_MAIN, -1, 0)
            return False
        if self.checkButtonRelease(ct, melee.Button.BUTTON_A): return False
        if self.ps.on_ground and self.FD.iasa(self.ps.character,self.ps.action) <= 0:
            startPos = ct.current.main_stick
            ct.tilt_analog_unit(melee.Button.BUTTON_MAIN, 0, 0.7)
            ct.press_button(melee.Button.BUTTON_A)
            return True
        else:
            ct.release_button(melee.Button.BUTTON_A)
            return False
        
    def uaft(self, ct: melee.Controller): # upward angled forward tilt
        if self.ps.action == melee.Action.DASHING: # dont dash attack, slow down
            ct.release_button(melee.Button.BUTTON_A)
            ct.tilt_analog_unit(melee.Button.BUTTON_MAIN, -1, 0)
            return False
        if self.checkButtonRelease(ct, melee.Button.BUTTON_A): return False
        if self.ps.on_ground and self.FD.iasa(self.ps.character,self.ps.action) <= 0:
            startPos = ct.current.main_stick
            ct.tilt_analog_unit(melee.Button.BUTTON_MAIN, 0.5, 0.7)
            ct.press_button(melee.Button.BUTTON_A)
            return True
        else:
            ct.release_button(melee.Button.BUTTON_A)
            return False
        
    def daft(self, ct: melee.Controller): # downward angled forward tilt
        if self.ps.action == melee.Action.DASHING: # dont dash attack, slow down
            ct.release_button(melee.Button.BUTTON_A)
            ct.tilt_analog_unit(melee.Button.BUTTON_MAIN, -1, 0)
            return False
        if self.checkButtonRelease(ct, melee.Button.BUTTON_A): return False
        if self.ps.on_ground and self.FD.iasa(self.ps.character,self.ps.action) <= 0:
            startPos = ct.current.main_stick
            ct.tilt_analog_unit(melee.Button.BUTTON_MAIN, -0.5, 0.7)
            ct.press_button(melee.Button.BUTTON_A)
            return True
        else:
            ct.release_button(melee.Button.BUTTON_A)
            return False
        
    ### SMASH ATTACKS ###
    def chargeSmash(self, ct: melee.Controller, distToRelease: int, x: float, y: float):
        if self.FD.attack_state(self.ps.character, self.ps.action, self.ps.action_frame) == 0: # already charging
            if self.gs.distance > distToRelease:
                    ct.press_button(melee.Button.BUTTON_A)
            else:
                    ct.release_button(melee.Button.BUTTON_A)
            return True
        if self.checkButtonRelease(ct, melee.Button.BUTTON_A): return False
        if self.ps.on_ground and self.FD.iasa(self.ps.character,self.ps.action) <= 0: # not charging, can charge
            ct.tilt_analog_unit(melee.Button.BUTTON_MAIN, x, y)
            ct.press_button(melee.Button.BUTTON_A)
            self.appendRelease(60, melee.Button.BUTTON_A) # max charge time
            return True
        else: # not charging and cannot charge
            ct.release_button(melee.Button.BUTTON_A)
            return False
    
    
    def usmash(self, ct: melee.Controller, distToRelease: int = 0):
        if self.ps.action == melee.Action.DASHING: # dont dash attack, slow down
            ct.release_button(melee.Button.BUTTON_A)
            ct.tilt_analog_unit(melee.Button.BUTTON_MAIN, -1, 0)
            return False
        if distToRelease == 0:  # instant up-smash
            if self.checkCStickRelease(ct): return False
            if self.ps.on_ground and self.FD.iasa(self.ps.character,self.ps.action) <= 0:
                ct.tilt_analog_unit(melee.Button.BUTTON_C, 0, 1)
                self.appendTilt(1, melee.Button.BUTTON_C, 0, 0)
                return True
            else: 
                ct.tilt_analog_unit(melee.Button.BUTTON_C, 0, 0)
                return False
        
        else: # charge smash
            self.chargeSmash(ct, distToRelease, 0, 1)
            
    def dsmash(self, ct: melee.Controller, distToRelease: int = 0):
        if self.ps.action == melee.Action.DASHING: # dont dash attack, slow down
            ct.release_button(melee.Button.BUTTON_A)
            ct.tilt_analog_unit(melee.Button.BUTTON_MAIN, -1, 0)
            return False
        if distToRelease == 0:  # instant down-smash
            if self.checkCStickRelease(ct): return False
            if self.ps.on_ground and self.FD.iasa(self.ps.character,self.ps.action) <= 0:
                ct.tilt_analog_unit(melee.Button.BUTTON_C, 0, -1)
                self.appendTilt(1, melee.Button.BUTTON_C, 0, 0)
                return True
            else: 
                ct.tilt_analog_unit(melee.Button.BUTTON_C, 0, 0)
                return False
        
        else: # charge smash
            self.chargeSmash(ct, distToRelease, 0, -1)
            
    def fsmash(self, ct: melee.Controller, distToRelease: int = 0):
        if self.ps.action == melee.Action.DASHING: # dont dash attack, slow down
            ct.release_button(melee.Button.BUTTON_A)
            ct.tilt_analog_unit(melee.Button.BUTTON_MAIN, -1, 0)
            return False
        if distToRelease == 0:  # instant forward-smash
            if self.checkCStickRelease(ct): return False
            if self.ps.on_ground and self.FD.iasa(self.ps.character,self.ps.action) <= 0:
                ct.tilt_analog_unit(melee.Button.BUTTON_C, 1, 0)
                self.appendTilt(1, melee.Button.BUTTON_C, 0, 0)
                return True
            else: 
                ct.tilt_analog_unit(melee.Button.BUTTON_C, 0, 0)
                return False
        
        else: # charge smash
            self.chargeSmash(ct, distToRelease, 1, 0)
    
    def bsmash(self, ct: melee.Controller, distToRelease: int = 0):
        if self.ps.action == melee.Action.DASHING: # dont dash attack, slow down
            ct.release_button(melee.Button.BUTTON_A)
            ct.tilt_analog_unit(melee.Button.BUTTON_MAIN, -1, 0)
            return False
        if distToRelease == 0:  # instant back-smash
            if self.checkCStickRelease(ct): return False
            if self.ps.on_ground and self.FD.iasa(self.ps.character,self.ps.action) <= 0:
                ct.tilt_analog_unit(melee.Button.BUTTON_C, -1, 0)
                self.appendTilt(1, melee.Button.BUTTON_C, 0, 0)
                return True
            else: 
                ct.tilt_analog_unit(melee.Button.BUTTON_C, 0, 0)
                return False
        
        else: # charge smash
            self.chargeSmash(ct, distToRelease, -1, 0)
            
    
    ### GRABS ###
    def grab(self, ct: melee.Controller):
        if self.checkButtonRelease(ct, melee.Button.BUTTON_Z): return False
        if not self.ps.on_ground: return False
        