import melee
import math
import random
from GeneralBot.CharacterData import CharacterData
from GeneralBot.GeneralizedAgent import GeneralizedAgent

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
                continue

            if console.processingtime * 1000 > 12:
                print("WARNING: Last frame took " + str(console.processingtime*1000) + "ms to process.")

            if gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
                    
                ga.nextState(gamestate)
                ga.endState(controller)
                ga.printAgent(controller, att)
                
                rng = random.choice([0, 0, 0, 0, 0, 1, 1, 1, 2, 3])
    
                ### NON INTERUPTABLE ###
                # TODO
                # put interupting actions here
                # i.e. if hit, or l-cancel, shield, slideoff response

                ### INTERUPTABLE ####

                if waitFrame <= gamestate.frame: # post-wait chains
                    
                    if ga.callback != False: # callback chains, can modify waitFrame
                        print("LOOPING", end="\r")
                        waitFrame = gamestate.frame + ga.callback(controller)
                                   
                    if ga.ps.action == melee.Action.EDGE_HANGING:
                        ga.callback = ga.looping_ledgeDash
                        waitFrame = gamestate.frame + ga.looping_ledgeDash(controller)

                    # TODO: Off stage, can be separated into Tactic
                    elif ga.ps.off_stage:
                        edgeVec = positionVector(ga.ps.position.x, ga.ps.position.y, ga.cd.RIGHT_EDGE_X*(1 if ga.ps.position.x > 0 else -1), 0) # vector to nearest edge
                        print("OFF STAGE", end="\r")
                        if ga.ps.jumps_left > 0: # we have jumps
                            if ga.at == melee.AttackState.COOLDOWN or ga.es.hitstun_frames_left > 0: # off stage and attempted hit
                                controller.tilt_analog(melee.Button.BUTTON_MAIN, edgeVec[0], edgeVec[1])
                            elif ga.at == melee.AttackState.ATTACKING or ga.at == melee.AttackState.WINDUP: # we're attacking and haven't hit, drift into enemy
                                p = positionVector(ga.ps.position.x, ga.ps.position.y, ga.es.position.x, ga.es.position.y)
                                controller.tilt_analog_unit(melee.Button.BUTTON_MAIN, p[0], p[1])
                            else:  # we have not attempted an attack
                                if abs(ga.es.position.x) > abs(ga.ps.position.x) and ga.gs.distance < 50 and ga.ps.position.y > 15: # enemy is further off edge, were above 0, and close
                                    if ga.Acts[ga.cd.aerialAtt_short[0].action](controller):
                                        print("EDGE ATTACK", end="\r")
                                        waitFrame = gamestate.frame + 2
                                else: # jump to ledge
                                    if ga.ps.position.x < 0 and not ga.ps.facing and not ga.hop_to_y(controller, 10, 10):
                                        ga.shorthop(controller, True)
                                        controller.tilt_analog_unit(melee.Button.BUTTON_MAIN, int(ga.ps.position.x < 0), 0.5)
                                    else:
                                        controller.tilt_analog(melee.Button.BUTTON_MAIN, edgeVec[0], edgeVec[1])
                        else: # no jumps
                            controller.tilt_analog_unit(melee.Button.BUTTON_MAIN, edgeVec[0], edgeVec[1])
                            if abs(ga.ps.position.x) - ga.cd.RIGHT_EDGE_X < 25 and ga.ps.y > 10: # if we're near edge, make sure we don't hold down and fall through
                                controller.tilt_analog_unit(melee.Button.BUTTON_MAIN,edgeVec[0], max(edgeVec[1], 0.5))
                            elif ga.cd.FD.frames_until_dj_apex(ga.ps) > 0:
                                ga.hop_to_y(controller, 0, 10) # continue jump
                            elif not ga.upb(controller): # up B to edge
                                controller.tilt_analog_unit(melee.Button.BUTTON_MAIN, edgeVec[0], edgeVec[1])
                                waitFrame = gamestate.frame + 4
                    
                    # TODO: Enemy death, can be separated into Tactic
                    elif ga.es.action.value < 14: # Death animations, or on halo
                        controller.tilt_analog(melee.Button.BUTTON_MAIN, int(0 > ga.ps.position.x), int(ga.ps.position.y < 0))    
                        ga.hop_to_y(controller, 25, 50)     

                    # TODO: Below can be separated into an approach Tactic
                    # attacking, fast fall
                    elif ga.at in [melee.AttackState.ATTACKING or melee.AttackState.WINDUP]:
                        ga.ffall(controller)
                    
                    # Approach
                    else:
                        controller.tilt_analog(melee.Button.BUTTON_MAIN, int(ga.es.position.x > ga.ps.position.x), 0.5)
                        ga.hop_to_y(controller, ga.es.position.y, 5)
                        waitFrame = gamestate.frame + 2
                        
                        if ga.es.position.y < ga.ps.position.y and ga.ps.position.y > 10:
                            ga.platFall(controller)
                            waitFrame = gamestate.frame + 2
                        
                        elif ga.gs.distance < 20 and ga.at not in []:
                            if ga.ps.on_ground:
                                if ga.ps.position.x < ga.es.position.x:
                                    if ga.es.iasa > 0 and (ga.es.iasa - ga.cd.groundAtt_less60[rng].firstHit) > -4:
                                        if ga.ps.facing:
                                            if ga.es.percent < 60:
                                                ga.Acts[ga.cd.groundAtt_less60[rng].action](controller)
                                            else:
                                                ga.Acts[ga.cd.groundAtt_abov60[rng].action](controller)
                                        else:
                                            ga.bsmash(controller)
                                    else:
                                        ga.Acts[ga.cd.groundAtt_short[rng].action](controller)
                                else:
                                    if ga.es.iasa > 0 and (ga.es.iasa - ga.cd.groundAtt_less60[rng].firstHit) > -4:
                                        if not ga.ps.facing:
                                            if ga.es.percent < 60:
                                                ga.Acts[ga.cd.groundAtt_less60[rng].action](controller)
                                            else:
                                                ga.Acts[ga.cd.groundAtt_abov60[rng].action](controller)
                                        else:
                                            ga.bsmash(controller)
                                    else:
                                        ga.Acts[ga.cd.groundAtt_short[rng].action](controller)
                            else:
                                if ga.ps.position.x < ga.es.position.x:
                                    if ga.es.iasa > 0 and (ga.es.iasa - ga.cd.aerialAtt_less60[rng].firstHit) > -4:
                                        if ga.ps.facing:
                                            if ga.es.percent < 60:
                                                ga.Acts[ga.cd.aerialAtt_less60[rng].action](controller)
                                            else:
                                                ga.Acts[ga.cd.aerialAtt_abov60[rng].action](controller)
                                        else:
                                            ga.bair(controller)
                                    else:
                                        ga.Acts[ga.cd.aerialAtt_short[rng].action](controller)
                                else:
                                    if ga.es.iasa > 0 and (ga.es.iasa - ga.cd.aerialAtt_less60[rng].firstHit) > -4:
                                        if not ga.ps.facing:
                                            if ga.es.percent < 60:
                                                ga.Acts[ga.cd.aerialAtt_less60[rng].action](controller)
                                            else:
                                                ga.Acts[ga.cd.aerialAtt_abov60[rng].action](controller)
                                        else:
                                            ga.bair(controller)
                                    else:
                                        ga.Acts[ga.cd.aerialAtt_short[rng].action](controller)
                                
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