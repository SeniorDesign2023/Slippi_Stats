import melee
import math
import random
from GeneralBot.CharacterData import CharacterData
from GeneralBot.GeneralizedAgent import GeneralizedAgent

# All damaging states, https://libmelee.readthedocs.io/en/latest/enums.html
DAMAGED_ACTIONS = [melee.Action.DAMAGE_HIGH_1, melee.Action.DAMAGE_HIGH_2,melee.Action.DAMAGE_HIGH_3, melee.Action.DAMAGE_NEUTRAL_1,melee.Action.DAMAGE_NEUTRAL_2,
melee.Action.DAMAGE_NEUTRAL_3,melee.Action.DAMAGE_LOW_1,melee.Action.DAMAGE_LOW_2,melee.Action.DAMAGE_LOW_3,melee.Action.DAMAGE_AIR_1, melee.Action.DAMAGE_AIR_2,
melee.Action.DAMAGE_AIR_3, melee.Action.DAMAGE_FLY_HIGH, melee.Action.DAMAGE_FLY_NEUTRAL, melee.Action.DAMAGE_FLY_LOW, melee.Action.DAMAGE_FLY_TOP,
melee.Action.DAMAGE_FLY_ROLL, melee.Action.GRABBED, melee.Action.GRAB_PUMMELED, melee.Action.GRAB_PULL, melee.Action.GRAB_PULLING_HIGH, 
melee.Action.GRABBED_WAIT_HIGH, melee.Action.PUMMELED_HIGH, melee.Action.CAPTURE_WAIT_KIRBY, melee.Action.CAPTURE_KIRBY, melee.Action.SHOULDERED_WAIT, 
melee.Action.SHOULDERED_WALK_SLOW, melee.Action.SHOULDERED_WALK_MIDDLE, melee.Action.SHOULDERED_TURN, melee.Action.CAPTURE_WAIT_KOOPA, melee.Action.CAPTURE_DAMAGE_KOOPA,
melee.Action.THROWN_FORWARD, melee.Action.THROWN_BACK, melee.Action.THROWN_UP, melee.Action.THROWN_DOWN, melee.Action.THROWN_DOWN_2]

# get vector from position
def positionVector(start_x: float, start_y: float, end_x: float, end_y: float):
    distance = [start_x - end_x, start_y - end_y]
    norm = math.sqrt(distance[0] ** 2 + distance[1] ** 2)
    return (-distance[0] / norm, -distance[1] / norm)

# Test run agent
def testStrategy(path: str, character: melee.Character, stage: melee.Stage, port_self: int, port_opp: int):
        print("TESTING (console & controllers must already be connected to test!)")
        
        console = melee.Console(path=path)
        controller = melee.Controller(console=console, port=port_self)
        
        # controller_h = melee.Controller(console=console, port=port_opp, type=melee.ControllerType.GCN_ADAPTER)
        # non necessary, creates bugs for non GCC users
        
        print("Connecting to console")
        console.run()
        if not console.connect():
            print("ERROR: Failed to connect to the console.")
            return("failed: couldn't connect to console" , None)

        print("Connecting controller(s)")
        if not controller.connect():
            print("ERROR: Failed to connect the controller(s).")
            return("failed: couldn't connect controllers" , None)
        
        # TODO: Utilize new CharacterData and ActionData features to generate and verify proper action list
        # Dogshit functions below for testing, not to be duplicated in further bots
        #actionsGround = [ga.jab, ga.ftil_l, ga.fsmash, ga.dsmash]
        #actionsAir = [ga.uair, ga.nair, ga.bair, ga.dair]
        att = lambda x: True # Needs to return true on first call, gets replaced
        cd = None       # Will initialize on stageSelect
        ga = None       # 
        waitFrame = 0   # DO NOT init to -1, used to detect stageSelect
        opp_char_selected = melee.Character.UNKNOWN_CHARACTER
        rng = 0
        
        while(True):
            gamestate = console.step()
            
            if gamestate is None:
                return "Done"
                continue

            if console.processingtime * 1000 > 12:
                print("WARNING: Last frame took " + str(console.processingtime*1000) + "ms to process.")

            if gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
                    
                ga.nextState(gamestate)
                ga.endState(controller) # Releases buffered buttons, is okay to go at start of gameState
                ga.printAgent(controller, att)
                
                if gamestate.frame % 90:
                    rng = random.choice([0, 0, 0, 0, 0, 1, 1, 1, 2, 2, 3])
                ### NON INTERUPTABLE ###
                # put interupting actions here
                # i.e. if hit, or l-cancel, shield, slideoff response.
                
                # Hit response
                if ga.ps.action in DAMAGED_ACTIONS:         
                    print("damaged", end="\r")          
                    # Been hit, forget whatever we've been doing
                    waitFrame = gamestate.frame
                    ga.callback = False
                    
                    # Tech Code below is from https://github.com/altf4/SmashBot/blob/main/Tactics/mitigate.py
                    # is the only directly sourced code from SmashBot.
                    #
                    # Tech if we need to
                    # Calculate when we will land
                    if ga.ps.position.y > -4 and not ga.ps.on_ground and \
                            melee.Action.DAMAGE_HIGH_1.value <= ga.ps.action.value <= melee.Action.DAMAGE_FLY_ROLL.value:
                        framesuntillanding = 0
                        speed = ga.ps.speed_y_attack + ga.ps.speed_y_self
                        height = ga.ps.position.y
                        gravity = ga.cd.FD.characterdata[ga.ps.character]["Gravity"]
                        termvelocity = ga.cd.FD.characterdata[ga.ps.character]["TerminalVelocity"]
                        while height > 0:
                            height += speed
                            speed -= gravity
                            speed = max(speed, -termvelocity)
                            framesuntillanding += 1
                            # Shortcut if we get too far
                            if framesuntillanding > 120:
                                break
                        # Do the tech
                        if framesuntillanding < 4:
                            print("TECHING")
                            controller.release_all() # ensure generally fresh state after teching
                            controller.press_button(melee.Button.BUTTON_R)
                            ga.appendRelease(4, melee.Button.BUTTON_R)
                            controller.tilt_analog(melee.Button.BUTTON_C, 0.5, 0.5)
                    
                    elif ga.ps.action in [melee.Action.GRABBED, melee.Action.GRAB_PUMMELED, melee.Action.GRAB_PULL, # Grabbed
                        melee.Action.GRAB_PUMMELED, melee.Action.GRAB_PULLING_HIGH, melee.Action.GRABBED_WAIT_HIGH, melee.Action.PUMMELED_HIGH, 
                        melee.Action.CAPTURE_WAIT_KIRBY, melee.Action.CAPTURE_KIRBY, melee.Action.SHOULDERED_WAIT, melee.Action.SHOULDERED_WALK_SLOW, # Donkey Kong and Kirby stuff
                        melee.Action.SHOULDERED_WALK_MIDDLE, melee.Action.SHOULDERED_TURN]:
                        if gamestate.frame % 3 == 0:
                            if not controller.current.button[melee.Button.BUTTON_A]:
                                controller.tilt_analog(melee.Button.BUTTON_MAIN, 0, 0)
                                controller.tilt_analog(melee.Button.BUTTON_C, 0.125, 0.125)
                                for btn in [melee.Button.BUTTON_A, melee.Button.BUTTON_B, melee.Button.BUTTON_X, melee.Button.BUTTON_Y]:
                                    controller.press_button(btn)
                            else:
                                controller.release_all()
                                controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.25, 0.25)
                                controller.tilt_analog(melee.Button.BUTTON_C, 0.875, 0.125)
                    else:
                        # DI to stage
                        controller.release_all()
                        centerStage = positionVector(ga.ps.position.x, ga.ps.position.y, 0, 0)
                        controller.tilt_analog_unit(melee.Button.BUTTON_MAIN, centerStage[0], centerStage[1])
                        controller.tilt_analog_unit(melee.Button.BUTTON_MAIN, abs(centerStage[0]-0.25), abs(centerStage[1]-0.25))
                        controller.release_button(melee.Button.BUTTON_L)
                        controller.release_button(melee.Button.BUTTON_R)               
                
                ### INTERUPTABLE ####
                elif waitFrame <= gamestate.frame: # post-wait chains
                    controller.release_button(melee.Button.BUTTON_L)
                    controller.release_button(melee.Button.BUTTON_R)
                    
                    if ga.callback != False: # callback chains, can modify waitFrame
                        waitFrame = gamestate.frame + ga.callback(controller)
                        print("LOOPING: waitFrame = " + str(waitFrame - gamestate.frame))
                                   
                    elif ga.ps.action == melee.Action.EDGE_HANGING:
                        if rng == 1:
                            ga.callback = ga.looping_ledgeDash
                            waitFrame = gamestate.frame + ga.looping_ledgeDash(controller)
                        elif ga.ps.percent < 100:
                            if gamestate.frame % 2 == 0:
                                ga.getupAttack(controller)
                                waitFrame = gamestate.frame + 4
                            else:
                                ga.shorthop(controller)
                                waitFrame = gamestate.frame + 4
                        else:
                            controller.press_button(melee.Button.BUTTON_R)
                            waitFrame = gamestate.frame + 4
                                

                    # TODO: Off stage, can be separated into Tactic
                    elif ga.ps.position.x < ga.cd.LEFT_EDGE_X or ga.ps.position.x > ga.cd.RIGHT_EDGE_X and not ga.ps.action == melee.Action.EDGE_HANGING:
                        edgeVec = positionVector(ga.ps.position.x, ga.ps.position.y, ga.cd.RIGHT_EDGE_X*(1 if ga.ps.position.x > 0 else -1), 0) # vector to nearest edge
                        print("OFF STAGE")
                        if ga.ps.jumps_left > 0: # we have jumps
                            if ga.at == melee.AttackState.COOLDOWN or ga.es.hitstun_frames_left > 0: # off stage and attempted hit
                                centerStage = positionVector(ga.ps.position.x, ga.ps.position.y, 0, 0)
                                controller.tilt_analog_unit(melee.Button.BUTTON_MAIN, centerStage[0], centerStage[1])
                            elif ga.at == melee.AttackState.ATTACKING or ga.at == melee.AttackState.WINDUP: # we're attacking and haven't hit, drift into enemy
                                p = positionVector(ga.ps.position.x, ga.ps.position.y, ga.es.position.x, ga.es.position.y)
                                controller.tilt_analog_unit(melee.Button.BUTTON_MAIN, p[0], 1)
                            else:  # we have not attempted an attack
                                #if ga.gs.distance < 5 and ga.ps.position.y > 50 and (ga.cd.LEFT_EDGE_X - abs(ga.ps.position.x)) < 15: # enemy is further off edge, were above 0, and close
                                #    if ga.Acts[ga.cd.aerialAtt_short[0].action](controller):
                                #        print("EDGE ATTACK", end="\r")
                                #        waitFrame = gamestate.frame + 2
                                #else: # jump to ledge
                                ga.hop_to_y(controller, 20, 20)
                                controller.tilt_analog(melee.Button.BUTTON_MAIN, int(ga.ps.position.x < 0), 0.75)
                        else: # no jumps
                            print("NO JUMPS PLEASE GOD")
                            if abs(ga.ps.position.x) < ga.cd.RIGHT_EDGE_X:
                                controller.tilt_analog(melee.Button.BUTTON_MAIN, int(not ga.ps.position.x > 0), 0.5) # under stage, pin to side pointing to ledge
                                print("under stage")
                            if (abs(ga.ps.position.x) - ga.cd.RIGHT_EDGE_X) < 15 and ga.ps.y > 0: # if we're near edge, make sure we don't hold down and fall through
                                controller.tilt_analog_unit(melee.Button.BUTTON_MAIN,edgeVec[0], max(edgeVec[1], 0.5))
                                print("no fall through")
                                
                            elif ga.cd.FD.frames_until_dj_apex(ga.ps) > 0:
                                ga.hop_to_y(controller, 20, 0) # continue jump
                                print("still jumping")
                            elif ga.upb(controller): # up B to edge
                                controller.tilt_analog(melee.Button.BUTTON_MAIN, int(ga.ps.position.x < 0), 1) # Some up-b need the stick to tilt right
                                waitFrame = gamestate.frame + 2
                                print("UP B SUCCESS!")
                            else:
                                print("UP TRIED :(")
                                controller.tilt_analog_unit(melee.Button.BUTTON_MAIN, edgeVec[0], edgeVec[1])
                                
                    
                    # TODO: Enemy death, can be separated into Tactic
                    elif ga.es.action.value < 14: # Death animations, or on halo
                        controller.tilt_analog(melee.Button.BUTTON_MAIN, int(0 > ga.ps.position.x), int(ga.ps.position.y < 0))    
                        ga.hop_to_y(controller, 25, 50)     

                    # TODO: Below can be separated into an approach Tactic
                    # attacking, fast fall
                    elif ga.at in [melee.AttackState.ATTACKING or melee.AttackState.WINDUP] and abs(ga.ps.position.x) < 50:
                        ga.ffall(controller)
                    
                    # Approach or pre-empt defense
                    else:
                        esAt = ga.cd.FD.attack_state(ga.cd.ENEMY_CHARACTER, ga.es.action, ga.es.action_frame)
                        esIasa = ga.cd.FD.iasa(ga.cd.ENEMY_CHARACTER, ga.es.action)
                        
                        controller.tilt_analog(melee.Button.BUTTON_MAIN, int(ga.es.position.x > ga.ps.position.x), 0.5)
                        ga.hop_to_y(controller, ga.es.position.y, 5)
                        waitFrame = gamestate.frame + 2
                        
                        if ga.es.position.y + 10 < ga.ps.position.y and ga.ps.position.y > 10:
                            ga.callback = ga.looping_platFall
                            waitFrame = gamestate.frame + ga.looping_platFall(controller)
                        
                        elif ga.gs.distance < 30:
                            fn = ga.jab
                            if ga.ps.on_ground:
                                if ga.ps.position.x < ga.es.position.x:
                                    if esIasa > 0 and (esIasa - ga.cd.groundAtt_less60[rng].firstHit) > -4:
                                        if ga.ps.facing:
                                            if ga.es.percent < 60:
                                                fn = ga.Acts[ga.cd.groundAtt_less60[rng].action]
                                            else:
                                                fn = ga.Acts[ga.cd.groundAtt_abov60[rng].action]
                                        else:
                                            ga.bsmash
                                    else:
                                        fn = ga.Acts[ga.cd.groundAtt_short[rng].action]
                                else:
                                    if esIasa > 0 and (esIasa - ga.cd.groundAtt_less60[rng].firstHit) > -4:
                                        if not ga.ps.facing:
                                            if ga.es.percent < 60:
                                                fn = ga.Acts[ga.cd.groundAtt_less60[rng].action]
                                                
                                            else:
                                                fn = ga.Acts[ga.cd.groundAtt_abov60[rng].action]

                                        else:
                                            ga.bsmash
                                    else:
                                        fn = ga.Acts[ga.cd.groundAtt_short[rng].action]
                            else:
                                if ga.ps.position.x < ga.es.position.x:
                                    if esIasa > 0 and (esIasa - ga.cd.aerialAtt_less60[rng].firstHit) > -4:
                                        if ga.ps.facing:
                                            if ga.es.percent < 60:
                                                fn = ga.Acts[ga.cd.aerialAtt_less60[rng].action]
                                            else:
                                                fn = ga.Acts[ga.cd.aerialAtt_abov60[rng].action]
                                        else:
                                            ga.bair
                                    else:
                                        fn = ga.Acts[ga.cd.aerialAtt_short[rng].action]
                                else:
                                    if esIasa > 0 and (esIasa - ga.cd.aerialAtt_less60[rng].firstHit) > -4:
                                        if not ga.ps.facing:
                                            if ga.es.percent < 60:
                                                fn = ga.Acts[ga.cd.aerialAtt_less60[rng].action]
                                            else:
                                                fn = ga.Acts[ga.cd.aerialAtt_abov60[rng].action]
                                        else:
                                            ga.bair
                                    else:
                                        fn = ga.Acts[ga.cd.aerialAtt_short[rng].action]
                            # Execute chosen move
                            print(str(fn)[30:35] + "  " + str(fn(controller)), end="\r")
                                
                else:
                    if waitFrame == -1:  # new game            
                        controller.release_all()

                pass
            else:
                # Characters have been chosen, update character data
                if waitFrame != -1 and gamestate.players.get(port_opp, None) is not None:
                    print(gamestate.players[port_opp].character, end="\r")
                    
                    if opp_char_selected != melee.Character.UNKNOWN_CHARACTER and gamestate.menu_state == melee.Menu.STAGE_SELECT:
                        print(gamestate.players[port_opp].character)
                        cd = CharacterData(character, opp_char_selected,stage, port_self, port_opp)
                        ga = GeneralizedAgent(cd)
                        waitFrame = -1
                    else:
                        opp_char_selected = gamestate.players[port_opp].character
                
                # TODO: Check with UI for new parameters on game end
                # if waitFrame != -1: return True
                # Game has ended, new one has started during the same session, break out
                    
                melee.MenuHelper.menu_helper_simple(
                    gamestate=gamestate,
                    controller=controller,
                    character_selected=character,
                    stage_selected=stage,
                    connect_code="",
                    cpu_level=0,
                    costume=2,
                    autostart=False,
                    swag=False
                )

# Test with entry point at this file
#testRun("C:/Users/sonic/AppData/Roaming/Slippi Launcher/netplay", melee.Character.DK, melee.Stage.BATTLEFIELD, 1, 2) 