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
#link is aggressive. he (vert/hrzt) pursues you until he is close enough to upB you
#if he is out of melee range, he throws boomerangs while he approaches
    #optional: he randomly decides which attack he does 
#on your last stock, he taunts when you spawn

#issues:
#link doesn't see you if you are right behind him
    #for that matter, he does nothing if you are right next to him on either side
#link will happily chase you straight off the stage
    #detect edge somehow?
#also he lacks any sort of edge recovery
    #ibid
#link will simply kneel instead of dropping through platforms
#when he approaches, instead of hitting he jumps, falls left, and boomerangs
    #worth noting that he always falls left
#he will not double jump
    #i'm thinking make a framedata object because it has a method that checks double jump height
#he will not taunt
mocked = False
while True:
    gamestate = console.step() 
    if gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
            heightDif = gamestate.player[PORT_BOT].y - gamestate.player[PORT_HUMAN].y
            sideDif = gamestate.player[PORT_BOT].x - gamestate.player[PORT_HUMAN].x
            direction = gamestate.player[PORT_BOT].x < gamestate.player[PORT_HUMAN].x
            if (gamestate.distance < 21): #if close, jump and up B. ps eat shit beckham 21 is better than 20
                 #controller.release_button(melee.Button.BUTTON_MAIN)
                 #controller.release_button(melee.Button.BUTTON_B)
                 #controller.press_button(melee.Button.BUTTON_X)
                 #controller.flush()
                 controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 1)
                 controller.press_button(melee.Button.BUTTON_B)
            elif  (heightDif > -21) and (heightDif < 21): #if on the same height, throw boomerang
                 controller.release_button(melee.Button.BUTTON_MAIN)
                 controller.simple_press(int(direction), 0.5, melee.Button.BUTTON_B)
            elif (gamestate.player[PORT_HUMAN].stock > 1) or mocked:
                 if (sideDif > -21) and (sideDif < 21): #if in the same "column"
                      if heightDif > 21: #player is lower
                           controller.release_button(melee.Button.BUTTON_MAIN)
                           controller.release_button(melee.Button.BUTTON_X)
                           controller.release_button(melee.Button.BUTTON_B)
                           controller.tilt_analog(melee.Button.BUTTON_MAIN, 0, 0)
                      elif heightDif < -21: #player is higher
                            controller.release_button(melee.Button.BUTTON_MAIN)
                            controller.release_button(melee.Button.BUTTON_X)
                            controller.release_button(melee.Button.BUTTON_B)
                            controller.press_button(melee.Button.BUTTON_Y)
                 else: #not the same height. find which direction to go and go there
                     controller.tilt_analog(melee.Button.BUTTON_MAIN, int(direction), 0.5)
                     controller.release_button(melee.Button.BUTTON_X)
                     controller.release_button(melee.Button.BUTTON_B)
                     controller.release_button(melee.Button.BUTTON_Y)
            else: #one stock left. nerd
                 mocked = True
                 controller.release_button(melee.Button.BUTTON_X)
                 controller.release_button(melee.Button.BUTTON_B)
                 controller.release_button(melee.Button.BUTTON_Y)
                 controller.release_button(melee.Button.BUTTON_MAIN)
                 controller.press_button(melee.Button.BUTTON_D_UP)
                 controller.press_button(melee.Button.BUTTON_L)
                 controller.flush()
                 controller.release_button(melee.Button.BUTTON_D_UP)
                 controller.release_button(melee.Button.BUTTON_L)

                 
    else:
        melee.MenuHelper.menu_helper_simple(gamestate,
                                            controller,
                                            melee.Character.LINK,
                                            melee.Stage.RANDOM_STAGE,
                                            "",
                                            costume=0,
                                            autostart=False,
                                            swag=False)