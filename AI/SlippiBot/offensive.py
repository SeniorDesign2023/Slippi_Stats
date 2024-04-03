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
#link is aggressive. he (vert/hrzt) pursues you until he is close enough to attack you with A
#if he is out of melee range, he throws boomerangs while he approaches
    #optional: he randomly decides which attack he does 
#on your last stock, he taunts when you spawn

#issues:
#link doesn't see you if you are right behind him
    #for that matter, he does nothing if you are right next to him on either side
#when he runs off the left side, he won't up B to get back on
    #right side works fine, but not terribly well
#sometimes, unprompted, he just runs off one of the sides and tries to kill himself
    #relatable
#also he lacks any sort of edge recovery
    #edge detection?
#link will simply kneel instead of dropping through platforms
#when he approaches, he will simply hit once and then continue
    #make him stop and continue to attack
#he will not double jump
    #i'm thinking make a framedata object because it has a method that checks double jump height
#he will not taunt
mocked = False
while True:
    gamestate = console.step() 
    if gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
            heightDif = gamestate.players[PORT_BOT].y - gamestate.players[PORT_HUMAN].y
            sideDif = gamestate.players[PORT_BOT].x - gamestate.players[PORT_HUMAN].x
            xdirection = gamestate.players[PORT_BOT].x < gamestate.players[PORT_HUMAN].x
            ydirection = gamestate.players[PORT_BOT].y < gamestate.players[PORT_HUMAN].y
            if (gamestate.distance < 15): #if close, throw cstick
                 controller.release_button(melee.Button.BUTTON_MAIN)
                 controller.release_button(melee.Button.BUTTON_B)
                 controller.tilt_analog(melee.Button.BUTTON_C, int(xdirection), int(ydirection))

            if  (heightDif > -21) and (heightDif < 21): #if on the same height
                 #controller.release_button(melee.Button.BUTTON_MAIN)
                 controller.release_button(melee.Button.BUTTON_C)
                 #if the bot is between the stage borders
                 if(gamestate.players[PORT_BOT].x > ((melee.stages.EDGE_GROUND_POSITION[melee.Stage.POKEMON_STADIUM] * -1) + 42)) and ((gamestate.players[PORT_BOT].x < melee.stages.EDGE_GROUND_POSITION[melee.Stage.POKEMON_STADIUM]) - 42):
                    if gamestate.distance > 30: #if far away, throw boomerang
                         controller.press_button(melee.Button.BUTTON_B)
                         controller.tilt_analog(melee.Button.BUTTON_MAIN, int(xdirection), 0.5) #run at player
                    elif gamestate.distance < 15: #if close, stop moving
                         controller.release_button(melee.Button.BUTTON_MAIN)
                         controller.release_button(melee.Button.BUTTON_C)
           
            elif gamestate.players[PORT_BOT].off_stage: #if we've fallen off
                if gamestate.players[PORT_BOT].y < -21: #if we're below the stage level
                    if gamestate.players[PORT_BOT].x < ((melee.stages.EDGE_POSITION[melee.Stage.POKEMON_STADIUM] * -1) + 42): #left side
                        controller.release_button(melee.Button.BUTTON_MAIN)
                        controller.simple_press(1, 1, melee.Button.BUTTON_B)
                    elif gamestate.players[PORT_BOT].x > melee.stages.EDGE_POSITION[melee.Stage.POKEMON_STADIUM] - 42: #right side
                        controller.release_button(melee.Button.BUTTON_MAIN)
                        controller.simple_press(0, 1, melee.Button.BUTTON_B)
                else: #if we've just barely walked off
                    if gamestate.players[PORT_BOT].x < ((melee.stages.EDGE_POSITION[melee.Stage.POKEMON_STADIUM] * -1) + 42): #left side
                        controller.tilt_analog(melee.Button.BUTTON_MAIN, 1, .5)
                    elif gamestate.players[PORT_BOT].x > melee.stages.EDGE_POSITION[melee.Stage.POKEMON_STADIUM] - 42: #right side
                        controller.tilt_analog(melee.Button.BUTTON_MAIN, 0, .5)
            
            #elif on the edge:
            
            elif (gamestate.players[PORT_HUMAN].stock > 1) or mocked: #just to make sure we've taunted if the person is down to 1 stock
                 if (sideDif > -21) and (sideDif < 21): #if in the same "column"
                      if heightDif > 21: #player is lower
                           controller.release_button(melee.Button.BUTTON_MAIN)
                           controller.release_button(melee.Button.BUTTON_X)
                           controller.release_button(melee.Button.BUTTON_B)
                           controller.release_button(melee.Button.BUTTON_C)
                           controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
                      elif heightDif < -21: #player is higher
                            controller.release_button(melee.Button.BUTTON_MAIN)
                            controller.release_button(melee.Button.BUTTON_X)
                            controller.release_button(melee.Button.BUTTON_B)
                            controller.release_button(melee.Button.BUTTON_C)
                            controller.press_button(melee.Button.BUTTON_Y)
                            controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 1)
                 else: #not the same column. find which xdirection to go and go there
                     controller.release_button(melee.Button.BUTTON_X)
                     controller.release_button(melee.Button.BUTTON_B)
                     controller.release_button(melee.Button.BUTTON_C)
                     controller.release_button(melee.Button.BUTTON_Y)
                     controller.tilt_analog(melee.Button.BUTTON_MAIN, int(xdirection), 0.5)
            
            else: #one stock left. nerd
                 mocked = True
                 controller.release_button(melee.Button.BUTTON_X)
                 controller.release_button(melee.Button.BUTTON_B)
                 controller.release_button(melee.Button.BUTTON_Y)
                 controller.release_button(melee.Button.BUTTON_C)
                 controller.release_button(melee.Button.BUTTON_MAIN)
                 controller.press_button(melee.Button.BUTTON_D_UP)
            

                 
    else:
        melee.MenuHelper.menu_helper_simple(gamestate,
                                            controller,
                                            melee.Character.LINK,
                                            melee.Stage.POKEMON_STADIUM,
                                            "",
                                            costume=0,
                                            autostart=False,
                                            swag=False)