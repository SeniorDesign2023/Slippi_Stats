##
## Created by: Michael Stoll
## Last Updated: 4/3/2024 12:31am
##
import melee
import melee.gamestate

#mom said it's not my turn to be player 1
PORT_BOT = 1
PORT_HUMAN = 2
#setup
console = melee.Console(path="C:/Users/micha/AppData/Roaming/Slippi Launcher/netplay")
controller = melee.Controller(console=console, port=PORT_BOT)
console.run()
console.connect()
controller.connect()

#idea:
#link is aggressive. he (vert/hrzt) pursues you until he is close enough to attack you with C and A
#if he is out of melee range, he throws boomerangs while he approaches
    #optional: he randomly decides which attack he does 
#if he falls off the stage, he up-B's to recover, with the intention of hitting you 
#on your last stock, he taunts while you spawn
#the fight takes place in the Pokemon Stadium

#issues:
#he won't edge recover until he falls
#link will simply kneel instead of dropping through platforms
#the player can camp behind him if he begins a combo while facing away from them
    #as soon as they move or attack, the spell is broken
#sometimes he temporarily freezes somewhere in the second "if"
#he will not double jump to save himself from the void
    #i'm thinking make a framedata object because it has a method that checks double jump height
    #or, and hear me out, this is his achilles' heel

print("rise, achilles")
mocked = False
stagnant = False
while True:
    gamestate = console.step() 
    if gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
            heightDif = gamestate.players[PORT_BOT].y - gamestate.players[PORT_HUMAN].y
            sideDif = gamestate.players[PORT_BOT].x - gamestate.players[PORT_HUMAN].x
            xdirection = gamestate.players[PORT_BOT].x < gamestate.players[PORT_HUMAN].x
            ydirection = gamestate.players[PORT_BOT].y < gamestate.players[PORT_HUMAN].y
            controller.release_button(melee.Button.BUTTON_A)
            controller.release_button(melee.Button.BUTTON_C)
            if (gamestate.distance < 15): #if close, throw cstick
                 controller.release_button(melee.Button.BUTTON_B)
                 controller.tilt_analog(melee.Button.BUTTON_C, int(xdirection), int(ydirection))
                 if stagnant:
                      controller.release_button(melee.Button.BUTTON_C)
                      controller.press_button(melee.Button.BUTTON_A)
                      controller.tilt_analog(melee.Button.BUTTON_MAIN, int(xdirection), .5)
                      stagnant = False
                 else : 
                      stagnant = True
                      #remember to turn and face your opponent
                      if gamestate.players[PORT_BOT].facing != int(xdirection):
                           controller.tilt_analog(melee.Button.BUTTON_MAIN, int(xdirection), .5)
                      else:
                           controller.release_button(melee.Button.BUTTON_MAIN)

            elif (heightDif > -5) and (heightDif < 5): #if on the same height
                 #controller.release_button(melee.Button.BUTTON_MAIN)
                 controller.release_button(melee.Button.BUTTON_C)
                 #if the bot is between the stage borders
                 if(gamestate.players[PORT_BOT].x > ((melee.stages.EDGE_GROUND_POSITION[melee.Stage.POKEMON_STADIUM] * -1) + 42)) and ((gamestate.players[PORT_BOT].x < melee.stages.EDGE_GROUND_POSITION[melee.Stage.POKEMON_STADIUM]) - 42):
                    if gamestate.distance > 30: #if far away, throw boomerang
                         controller.press_button(melee.Button.BUTTON_B)
                         controller.tilt_analog(melee.Button.BUTTON_MAIN, int(xdirection), 0.5) #run at player
                    else: 
                         controller.tilt_analog(melee.Button.BUTTON_MAIN, int(xdirection), .5)
                         controller.tilt_analog(melee.Button.BUTTON_C, int(xdirection), int(ydirection))
            #if edge_hanging currently
            #doesn't work. leaving in case we figure out how to check actions        
            elif melee.gamestate.PlayerState.action == melee.gamestate.enums.Action.EDGE_HANGING: 
                print("on ege")
                #if on left edge
                if(gamestate.players[PORT_BOT].x < (melee.stages.EDGE_POSITION[melee.Stage.POKEMON_STADIUM] * -1) + 6):
                     print("on left ege")
                     controller.press_button(melee.Button.BUTTON_X)
                     controller.tilt_analog(melee.Button.BUTTON_MAIN, 1, .5)
                #if on right edge
                elif (gamestate.players[PORT_BOT].x > melee.stages.EDGE_POSITION[melee.Stage.POKEMON_STADIUM] - 6):
                     print("on right ege")
                     controller.press_button(melee.Button.BUTTON_X)
                     controller.tilt_analog(melee.Button.BUTTON_MAIN, 0, .5)

            elif gamestate.players[PORT_BOT].off_stage: #if we've fallen off
                if gamestate.players[PORT_BOT].y < -21: #if we're below the stage level
                    if gamestate.players[PORT_BOT].x < ((melee.stages.EDGE_POSITION[melee.Stage.POKEMON_STADIUM] * -1) + 42): #left side
                        controller.release_button(melee.Button.BUTTON_MAIN)
                        controller.simple_press(1, 1, melee.Button.BUTTON_B)
                    elif gamestate.players[PORT_BOT].x > melee.stages.EDGE_POSITION[melee.Stage.POKEMON_STADIUM] - 42: #right side
                        controller.release_button(melee.Button.BUTTON_MAIN)
                        controller.simple_press(0, 1, melee.Button.BUTTON_B)
                else: #if we've just barely walked off
                    #in theory, these would enable you to just pop up real quick.
                    #in practice, nothing happens
                    if gamestate.players[PORT_BOT].x < ((melee.stages.EDGE_POSITION[melee.Stage.POKEMON_STADIUM] * -1) + 42): #left side
                        controller.press_button(melee.Button.BUTTON_Y)
                        controller.tilt_analog(melee.Button.BUTTON_MAIN, 1, .5)
                    elif gamestate.players[PORT_BOT].x > melee.stages.EDGE_POSITION[melee.Stage.POKEMON_STADIUM] - 42: #right side
                        controller.press_button(melee.Button.BUTTON_Y)
                        controller.tilt_analog(melee.Button.BUTTON_MAIN, 0, .5)
            elif (gamestate.players[PORT_HUMAN].stock > 1) or mocked: #just to make sure we've taunted if the person is down to 1 stock
                 if (sideDif > -21) and (sideDif < 21): #if in the same "column"
                      if heightDif > 5: #player is lower
                           controller.release_all()
                           controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
                           controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
                      elif heightDif < -5: #player is higher
                            controller.release_all()
                            controller.press_button(melee.Button.BUTTON_Y)
                            controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 1)
                 else: #not the same column. find which xdirection to go and go there
                     controller.release_all()
                     controller.tilt_analog(melee.Button.BUTTON_MAIN, int(xdirection), 0.5)
            
            else: #one stock left. time to meme
                 mocked = True
                 controller.release_all()
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
        