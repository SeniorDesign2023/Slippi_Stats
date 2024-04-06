import melee
import math
import random
#from GeneralBot.GeneralizedAgent import GeneralizedAgent
from CharacterData import CharacterData
from GeneralizedAgent import GeneralizedAgent

# get vector from position
def positionVector(start_x: float, start_y: float, end_x: float, end_y: float):
    distance = [start_x - end_x, start_y - end_y]
    norm = math.sqrt(distance[0] ** 2 + distance[1] ** 2)
    return (-distance[0] / norm, -distance[1] / norm)

# Test run agent
def testRun(path: str, character: melee.Character, stage: melee.Stage, port_self: int, port_opp: int):
        print("TESTING (console & controllers must already be connected to test!)")
        
        console = melee.Console(path=path)
        controller = melee.Controller(console=console, port=port_self)
        controller_h = melee.Controller(console=console, port=port_opp, type=melee.ControllerType.GCN_ADAPTER)
                
        cd = CharacterData(character, stage, port_self, port_opp)
        ga = GeneralizedAgent(cd)
        
        print("Connecting to console")
        console.run()
        if not console.connect():
            print("ERROR: Failed to connect to the console.")
            return("failed: couldn't connect to console" , None)

        print("Connecting controller(s)")
        if not controller.connect() and controller_h.connect():
            print("ERROR: Failed to connect the controller(s).")
            return("failed: couldn't connect controllers" , None)
        
        # TODO: Utilize new CharacterData and ActionData features to generate and verify proper action list
        actionsGround = [ga.jab, ga.ftil_l, ga.fsmash, ga.dsmash]
        actionsAir = [ga.uair, ga.nair, ga.bair, ga.dair]
        doGround = False
        att = actionsAir[0]
        waitFrame = -1
        
        while(True):
            gamestate = console.step()
            
            if gamestate is None:
                continue

            if console.processingtime * 1000 > 12:
                print("WARNING: Last frame took " + str(console.processingtime*1000) + "ms to process.")

            if gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
                ga.nextState(gamestate)
                ga.printAgent(controller, att)
                
                if waitFrame <= gamestate.frame: # non-interupting decisions
                    
                    # TODO: Enemy death, can be separated into Tactic
                    if ga.es.action.value < 14: # Death animations, or on halo
                        controller.tilt_analog(melee.Button.BUTTON_MAIN, int(0 > ga.ps.position.x), int(ga.ps.position.y < 0))    
                        ga.hop_to_y(controller, 25, 50)
                                   
                    # TODO: Off stage, can be separated into Tactic
                    if ga.ps.off_stage:
                        print("OFF STAGE", end="\r")
                        if ga.ps.jumps_left > 0: # we have jumps
                            if ga.at == melee.AttackState.COOLDOWN or ga.es.hitstun_frames_left > 0: # off stage and attempted hit
                                controller.tilt_analog(melee.Button.BUTTON_MAIN, int(0 > ga.ps.position.x), int(ga.ps.position.y < 0))
                            elif ga.at == melee.AttackState.ATTACKING or ga.at == melee.AttackState.WINDUP: # we're attacking and haven't hit, drift into enemy
                                p = positionVector(ga.ps.position.x, ga.ps.position.y, ga.es.position.x, ga.es.position.y)
                                controller.tilt_analog_unit(melee.Button.BUTTON_MAIN, p[0], p[1])
                                ga.hop_to_y(controller, ga.es.position.y, 50)
                            else:  # we have not attempted an attack
                                if abs(ga.es.position.x) > abs(ga.ps.position.x) and ga.gs.distance < 50: # enemy is further off edge, and close
                                    if ga.nair(controller): #TODO: choose longest lasting aerial
                                        print("EDGE ATTACK", end="\r")
                                        waitFrame = gamestate.frame + 2
                                else: # jump to ledge
                                    p = positionVector(ga.ps.position.x, ga.ps.position.y, ga.cd.RIGHT_EDGE_X*int(ga.ps.position.x > 0), 0) # vector to nearest edge
                                    controller.tilt_analog_unit(melee.Button.BUTTON_MAIN, p[0], max(p[1], -0.5))
                                    ga.hop_to_y(controller, 0, 10)
                        else: # no jumps
                            if abs(ga.ps.position.x) - ga.cd.RIGHT_EDGE_X < 25 and ga.ps.y > 10: # if we're near edge, make sure we don't hold down and fall through
                                p = positionVector(ga.ps.position.x, ga.ps.position.y, ga.cd.RIGHT_EDGE_X*int(ga.ps.position.x > 0), 0) # vector to nearest edge
                                controller.tilt_analog_unit(melee.Button.BUTTON_MAIN,p[0], max(p[1], -0.5))
                            elif ga.cd.FD.frames_until_dj_apex(ga.ps) > 0:
                                ga.hop_to_y(controller, 0, 10) # continue jump
                            elif not ga.upb(controller): # up B to edge
                                p = positionVector(ga.ps.position.x, ga.ps.position.y, ga.cd.RIGHT_EDGE_X*int(ga.ps.position.x > 0), 0) # vector to nearest edge
                                controller.tilt_analog_unit(melee.Button.BUTTON_MAIN, p[0], p[1])
                                waitFrame = gamestate.frame + 4
                            

                    # TODO: Below can be separated into an approach Tactic
                    # attacking, fast fall
                    elif not ga.ps.on_ground and (ga.at == melee.AttackState.ATTACKING or melee.AttackState.WINDUP):
                        if ga.ffall(controller):
                            p = positionVector(ga.ps.position.x, ga.ps.position.y, ga.es.position.x, ga.es.position.y)
                            controller.tilt_analog_unit(melee.Button.BUTTON_MAIN, p[0], p[1])
                            
                    # Approach
                    else:
                        controller.tilt_analog(melee.Button.BUTTON_MAIN, int(ga.es.position.x > ga.ps.position.x), 0.5)
                        ga.hop_to_y(controller, ga.es.position.y, 30)
                        waitFrame = gamestate.frame + 2
                        
                        if ga.es.position.y < ga.ps.position.y and ga.ps.position.y > 10:
                            ga.platFall(controller)
                        
                        elif ga.gs.distance < 50:
                            if not ga.ps.on_ground:
                                random.choice(actionsAir)(controller)
                            else:
                                random.choice(actionsGround)(controller)

                else:
                    if waitFrame == -1:  # new game            
                        controller.release_all()
                ga.endState(controller)
                pass
            else:
                # TODO: Check with UI for new parameters on game end
                if waitFrame != -1:
                    # Game has ended, new one has started during the same session, break out
                    return True
                    
                melee.MenuHelper.menu_helper_simple(
                    gamestate=gamestate,
                    controller=controller,
                    character_selected=ga.cd.CHARACTER,
                    stage_selected=ga.cd.STAGE_SELECTED,
                    connect_code="",
                    cpu_level=0,
                    costume=2,
                    autostart=True,
                    swag=False
                )
                waitFrame = -1 # reset on new game

# Test with entry point at this file
testRun("C:/Users/sonic/AppData/Roaming/Slippi Launcher/netplay", melee.Character.DK, melee.Stage.BATTLEFIELD, 1, 2) 