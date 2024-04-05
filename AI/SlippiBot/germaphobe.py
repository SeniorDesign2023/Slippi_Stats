##
## Created by: Michael Stoll
## Last Updated: 4/3/2024 3:19am
##
import melee
import melee.gamestate

#mom said it's my turn to be player 1 because that's how smashbot does it
PORT_BOT = 2
PORT_HUMAN = 1
#saves chars later and allows easy portability to a different map
groundEdge = melee.stages.EDGE_GROUND_POSITION[melee.Stage.BATTLEFIELD]
outEdge = melee.stages.EDGE_POSITION[melee.Stage.BATTLEFIELD]
console = melee.Console(path="C:/Users/micha/AppData/Roaming/Slippi Launcher/netplay")
controller = melee.Controller(console=console, port=PORT_BOT)
console.run()
console.connect()
controller.connect()
#idea:
#GW is elusive. if he is grabbed, he escapes
#if he sees an attack coming, he avoids it
#if a projectile is fired at him he blocks it
#he tries to get away from the player if they get anywhere close
#if the player chose the ice climbers he won't even bother, he will just kill himself as quickly as possible

#issues:
#He is a little too suicidal for my liking
    #he's supposed to be germaphobic but with a desire to live
    #unless those fucking ice climbers are around
#No edge recovery
#no double jump recovery
#when he escapes from the edge he doesn't do it very well
#no projectile avoidance
while True:
    gamestate = console.step() 
    if gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
            heightDif = gamestate.players[PORT_BOT].y - gamestate.players[PORT_HUMAN].y
            sideDif = gamestate.players[PORT_BOT].x - gamestate.players[PORT_HUMAN].x
            xdirection = gamestate.players[PORT_BOT].x > gamestate.players[PORT_HUMAN].x
            ydirection = gamestate.players[PORT_BOT].y > gamestate.players[PORT_HUMAN].y
            #no ice climbers. bad.
            if (gamestate.players[PORT_HUMAN].nana != None):
                print("nightmarenightmarenightmarenightmarenightmarenightmarenightmarenightmarenightmarenightmarenightmare")
                controller.press_button(melee.Button.BUTTON_X)
                controller.tilt_analog(melee.Button.BUTTON_MAIN, 0, .5)
            elif (gamestate.distance < 40): #if close, run away
                #controller.empty_input()
                #basically if being grappled (which should never happen tbh)
                if(gamestate.distance < 3):
                     controller.press_button(melee.Button.BUTTON_X)
                     controller.tilt_analog(melee.Button.BUTTON_MAIN, .5, 1)
                     controller.press_button(melee.Button.BUTTON_B)
                #if in melee attack range
                elif(gamestate.distance < 25):
                    #if at end of stage
                    if(gamestate.players[PORT_BOT].x < ((groundEdge * -1) + 15)) or (gamestate.players[PORT_BOT].x > (groundEdge - 15)):
                        controller.tilt_analog(melee.Button.BUTTON_MAIN, int(not xdirection), .5)
                        controller.press_button(melee.Button.BUTTON_L)
                    else:
                        controller.tilt_analog(melee.Button.BUTTON_MAIN, int(xdirection), .5)
                #still close enough to be concerned and run
                else:
                    if(gamestate.players[PORT_BOT].x < ((groundEdge * -1) + 15)) or (gamestate.players[PORT_BOT].x > (groundEdge - 15)):
                        controller.tilt_analog(melee.Button.BUTTON_MAIN, .5, .5)
                    else: 
                        controller.tilt_analog(melee.Button.BUTTON_MAIN, int(xdirection), .5)

            elif gamestate.players[PORT_BOT].action == melee.gamestate.enums.Action.EDGE_HANGING: 
                #if on left edge
                if(gamestate.players[PORT_BOT].x < (melee.stages.EDGE_POSITION[melee.Stage.POKEMON_STADIUM] * -1) + 6):
                     controller.press_button(melee.Button.BUTTON_X)
                     controller.tilt_analog(melee.Button.BUTTON_MAIN, 1, .5)
                #if on right edge
                elif (gamestate.players[PORT_BOT].x > melee.stages.EDGE_POSITION[melee.Stage.POKEMON_STADIUM] - 6):
                     controller.press_button(melee.Button.BUTTON_X)
                     controller.tilt_analog(melee.Button.BUTTON_MAIN, 0, .5)        
            
            elif gamestate.players[PORT_BOT].off_stage: #fell off map
                 controller.press_button(melee.Button.BUTTON_X)
                 controller.tilt_analog(melee.Button.BUTTON_MAIN, int(not xdirection), 1)
                 controller.press_button(melee.Button.BUTTON_B)
            else: #just crouch and keep your head down
                 controller.empty_input()                 
                 controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0) 

    else:
        melee.MenuHelper.menu_helper_simple(gamestate,
                                            controller,
                                            melee.Character.GAMEANDWATCH,
                                            melee.Stage.BATTLEFIELD,
                                            "",
                                            costume=0,
                                            autostart=False,
                                            swag=False)