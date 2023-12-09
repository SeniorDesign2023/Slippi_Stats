import melee

print('starting dk')

console = melee.Console(path="C:/Users/sonic/AppData/Roaming/Slippi Launcher/netplay")
# C:\Users\sonic\AppData\Roaming\Slippi Launcher\netplay

controller = melee.Controller(console=console, port=1)
controller_human = melee.Controller(console=console,
                                    port=2,
                                    type=melee.ControllerType.GCN_ADAPTER)

console.run()
console.connect()

controller.connect()
controller_human.connect()

while True:
    gamestate = console.step()
    if gamestate is None:
        continue
    
    if console.processingtime * 1000 > 12:
        print("WARNING: Last frame took " + str(console.processingtime*1000) + "ms to process.")

    if gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
        if gamestate.distance < 20:
            controller.press_button(melee.Button.BUTTON_B)
            controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0.9)
        else:
            controller.empty_input()
        pass
    else:
        melee.MenuHelper.menu_helper_simple(gamestate,
                                            controller,
                                            melee.Character.DK,
                                            melee.Stage.NO_STAGE,
                                            "",
                                            costume=2,
                                            autostart=False,
                                            swag=False)



