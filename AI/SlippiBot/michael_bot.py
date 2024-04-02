import melee

#mom said it's my turn to be player 1
PORT_PLR = 1
PORT_BOT = 2

#setup
console = melee.Console(path="C:/Users/micha/AppData/Roaming/Slippi Launcher/netplay")

controller = melee.Controller(console=console, port=PORT_BOT)
controller_human = melee.Controller(console=console,
                                    port=PORT_PLR,
                                    type=melee.ControllerType.STANDARD)

console.run()
console.connect()


controller_human.connect()
controller.connect()

while True:
    gamestate = console.step() 
    if gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
            pass
    else:
        melee.MenuHelper.menu_helper_simple(gamestate,
                                            controller,
                                            melee.Character.LINK,
                                            melee.Stage.RANDOM_STAGE,
                                            "",
                                            costume=0,
                                            autostart=False,
                                            swag=True)