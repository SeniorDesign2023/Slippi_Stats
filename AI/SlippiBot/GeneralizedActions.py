import melee

class GA:
    def __init__(self, fd: melee.FrameData, port_self: int, port_enemy: int):
        
        self.PORT_SELF = port_self
        self.PORT_ENEMY = port_enemy
        self.FD = fd
        
        self.gs = melee.GameState()
        self.ps = melee.PlayerState()
        
        self.release_buffer = { 0 : [] }
        self.tilt_buffer = { 0 : [] } # [ (button, x , y) , (button, x, y) ]
        self.press_callback = lambda x: None
        
    def appendRelease(self, framedAdded: int, button: melee.Button):
        prev = self.release_buffer.get(self.gs.frame + framedAdded, None)
        if prev == None: self.release_buffer[self.gs.frame + framedAdded] = [button]
        else: self.release_buffer[self.gs.frame + framedAdded] = prev.append(button)
        
    def appendTilt(self, framedAdded: int, button: melee.Button, x: float, y: float):
        prev = self.tilt_buffer.get(self.gs.frame + framedAdded, None)
        if prev == None: self.tilt_buffer[self.gs.frame + framedAdded] = [(button, x, y)]
        else: self.tilt_buffer[self.gs.frame + framedAdded] = prev.append((button, x, y))
        
    def nextState(self, _gs: melee.GameState, ct: melee.Controller):
        self.gs = _gs
        self.ps = self.gs.players[self.PORT_SELF]
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
                    ct.tilt_analog(tuple[0], tuple[1], tuple[2])
            else: break # future release, leave alone 
        
        self.press_callback(ct)
        
    def shorthop(self, ct: melee.Controller): # use BUTTON_Y when immediate release
        if self.ps.jumps_left > 0:
            ct.press_button(melee.Button.BUTTON_Y)
            self.appendRelease(1, melee.Button.BUTTON_Y)
            return True
        else: 
            return False
        
    def fullhop(self, ct: melee.Controller): # use BUTTON_X for buffered release
        if self.ps.jumps_left > 0:
            ct.press_button(melee.Button.BUTTON_X)
            self.appendRelease(self.FD.frames_until_dj_apex(self.gs.players[self.PORT_SELF]), melee.Button.BUTTON_X)
        else:
            return False
        
    def hop(self, ct: melee.Controller, amt: float):
        if self.ps.jumps_left > 0:
            ct.press_button(melee.Button.BUTTON_X)
            self.appendRelease(self.FD.frames_until_dj_apex(self.gs.players[self.PORT_SELF]), melee.Button.BUTTON_X)
        else:
            return False
        
    def uair(self, ct: melee.Controller):
        if not self.ps.on_ground:
            ct.tilt_analog_unit(melee.Button.BUTTON_C, 0, 1)
            self.press_callback = lambda x: None
        else: 
            # TODO: verify the minimum height needed to get active frames on uair
            self.fullhop(ct)
            self.press_callback = self.uair
            
    def jab(self, ct: melee.Controller):
        if self.ps.on_ground:
            startPos = ct.current.main_stick
            ct.tilt_analog_unit(melee.Button.BUTTON_MAIN, 0, 0)
            ct.press_button(melee.Button.BUTTON_A)
            self.appendRelease(1, melee.Button.BUTTON_A)
            self.appendTilt(1, melee.Button.BUTTON_MAIN, startPos[0], startPos[1])
        