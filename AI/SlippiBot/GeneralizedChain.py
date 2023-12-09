class CharacterChain:
    __metaclass__ = ABCMeta
    
    CharacterChain = None
    # during __init__: self.CharacterChain = CharacterChain(botJSON)
    
    interruptible = True
    logger = None
    controller = None
    framedata = None
    
    def searchMoves(self, gamestate, slippibot_state, opponent_state): ...
    
    def step(self, gamestate, slippibot_state, opponent_state): ...
    
    


