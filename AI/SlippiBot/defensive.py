import melee

#mom said it's not my turn to be player 1
PORT_BOT = 1
PORT_HUMAN = 3
#setup
console = melee.Console(path="C:/Users/micha/AppData/Roaming/Slippi Launcher/netplay")

controller = melee.Controller(console=console, port=PORT_BOT)



console.run()
console.connect()



controller.connect()
#idea:
#GW is elusive. if he is grabbed, he escapes
#if he sees an attack coming, he blocks
#he tries to get away from the player at all times

while True:
    gamestate = console.step() 
    if gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
            heightDif = gamestate.players[PORT_BOT].y - gamestate.players[PORT_HUMAN].y
            sideDif = gamestate.players[PORT_BOT].x - gamestate.players[PORT_HUMAN].x
            direction = gamestate.players[PORT_BOT].x < gamestate.players[PORT_HUMAN].x
            
            pass
    else:
        melee.MenuHelper.menu_helper_simple(gamestate,
                                            controller,
                                            melee.Character.GAMEANDWATCH,
                                            melee.Stage.BATTLEFIELD,
                                            "",
                                            costume=0,
                                            autostart=False,
                                            swag=False)