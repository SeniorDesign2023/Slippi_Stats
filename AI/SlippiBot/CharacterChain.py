import melee

class CharacterChain:
    __metaclass__ = ABCMeta
    
    def __init__(botJSON):
        characterData = botJSON[melee.Character(bot_state.character)]
        moveSubset = characterData[moveSubset]
        
    moveSubset = None
    
    interruptible = True
    logger = None
    controller = None
    framedata = None
    
    def searchMoves(self, gamestate, bot_state, opponent_state): ...
    
    def step(self, gamestate, bot_state, opponent_state): ...


