from time import clock
import random, sys
import traci
import subprocess, sys, socket, time, struct, random
from xml.sax import saxutils, make_parser, handler
import sumolib
import shutil
import os

PORT= 8350
RUNS= range(1)

def hasCapacity(vehEdge, vehNextEdge, edgeLength):
    if (edgeLength -((vehEdge + vehNextEdge) * 7.5)) <0:
        #no capacity too much vehicles on both edges
        return False
    else:
        return True

def calculateTrafficJam(vehID, edgeID, tlss):
    veh_number= 0
    #todo automatically
    #edge2lane= {'166445405#0': 5, 'e1': 2, 's1': 2, '61734682#3.75': 3, '61734682#3.115': 5, '318881710#0': 3, 'n1': 2, '314915850#0': 5, '314915843': 4, 'w1': 3}
    #moreLanes= {'166445405#0': ['s1'], '61734682#3.115':['61734682#3.75', 'e1'], 'n1': ['318881710#0'], '314915850#0': ['314915843', 'w1']}
    lanes= [edgeID+ "_0"]
    route=  traci.vehicle.getRoute(vehID)
    current= route.index(edgeID)
    
    #if edgeID in edge2lane.keys():
        #print edgeID, edge2lane[edgeID]
    # for id in range(edge2lane[edgeID]):
        # laneID= edgeID + '_' + str(0) # pedestrian and bike way are excluded
        # lanes.append(laneID)
    for laneID in lanes:
        num_lane= 0  
        try: 
            veh_lane= traci.lane.getLastStepVehicleNumber(laneID)
            num_lane += 1
            #print laneID, veh_lane
            if veh_lane > veh_number:
                veh_number= veh_lane
                # if traci.lane.getLastStepOccupancy(laneID)> 0.8:
                    # newMax= 0
                    # #check moreLanes and add
                    # if edgeID in moreLanes:
                        # for followLane in moreLanes[edgeID]:
                            # vehs= traci.lane.getLastStepVehicleNumber(followLane)
                            # if vehs > newMax:
                                # newMax= vehs
                        # veh_number += newMax
        except:
            print laneID, 'gibts nicht'
    speed= 13.9
    time_free=  (veh_number * 2) + 5
    max_distance= time_free * speed
    
    #check wheter there is space after the intersection
    nextEdgeID= route[current+1]
    vehEdge=traci.edge.getLastStepVehicleNumber(edgeID)
    vehNextEdge= traci.edge.getLastStepVehicleNumber(nextEdgeID)
    edgeLength= 100#185.6 #should be done automatically
    max_distance2= -1
    if not hasCapacity(vehEdge, vehNextEdge, edgeLength):
        tfree2= (vehEdge +vehNextEdge+1)*2 + 3
        speed2= 13.9
        z= (edgeLength - (vehEdge* 7.5))/speed2# achtung meter hier und zeit gerechnet pruefen
        max_distance2= (tfree2+ z )* speed
        #print "No capacity"    
    # fuer extended approach
    return max_distance, max_distance2
    
    
# generates a map which gives traffic light which has to be passed when the given edge is used.
def initLinkMap(net):
    LSAmap= {}
    #LSAmap the key is an edge from the network, value: a list (Id of the Traffic Light, amount of links of the traffic light, link ids which should be switched to green )
    for tls in net._tlss:
        for connection in tls._connections:
            edge= str(connection[0].getID())
            edge= edge[: len(edge)-2]
            if LSAmap.has_key(edge):
                LSAmap[edge].append(connection[2])
            else:
                linkCount= len(tls._connections)
                LSAmap[edge] = [tls._id, linkCount, connection[2]]
                
    # tls with more than one intersection
    #should be made automatically someday
    LSAmap['51798203']= LSAmap['51798203'][:] + LSAmap['51798202'][2:] 
    LSAmap['51808715']= LSAmap['51808715'][:] + LSAmap['51808699'][2:] 
    LSAmap['51808713']= LSAmap['51808715'][:] + LSAmap['51808699'][2:] 
    #LSAmap['']= LSAmap[''][:] + LSAmap[''][2:] 
    LSAmap['-786367651']= LSAmap['-51812073'][:] + LSAmap['-786367651'][2:] 
    LSAmap['-540638370']= LSAmap['-540638370'][:] + LSAmap['-51810895'][2:] 
    LSAmap['-51810892']= LSAmap['-51810892'][:] + LSAmap['-51810891'][2:] 
    LSAmap['-51810892']= LSAmap['-51810892'][:] + LSAmap['-51810891'][2:] + LSAmap['-51810730'][2:] 
    LSAmap['-783382276']= LSAmap['-783382276'][:] + LSAmap['-554711240'][2:] 
    LSAmap['-51797752.-70']= LSAmap['-51797752.-70'][:] + LSAmap['-51797738'][2:] 
    LSAmap['-67944896']= LSAmap['-67944896'][:] + LSAmap['-51808700'][2:] 
    #LSAmap['-554711240']=  LSAmap['-554711240'][:] +LSAmap['-783382276'][2:]
    LSAmap['51812210']= LSAmap['51812210'][:] + LSAmap['51811264'][2:] 
    LSAmap['-51811230.-75']= LSAmap['-51811230.-75'][:] + LSAmap['-51811226'][2:] + LSAmap['n1'][2:] 
    LSAmap['51808251']= LSAmap['51808251'][:] + LSAmap['51808252'][2:] + LSAmap['51808258'][2:] #+ LSAmap['54533991'][2:] 
    return LSAmap
 
# generates a map with TLIDs and juctions
def J2LSA(net):
    j2tls= {}
    for j in net._nodes:
        tls= j.getTLS()
        if tls:
            j2tls[j]= tls.getID()
               
    # tls with more than one intersection
    #should be made automatically someday
    return j2tls 
    
def initPassedEdges(net):
    tls2outEdge= {}
    for node in net._nodes:
        tls=str(node.getID()) # node.getTLS()
        if tls:
            for e in node.getOutgoing():
                tls2outEdge[e.getID()]= tls
    tls2j= { "a3": "51798026", "f1":"-51932979", "cluster_54535338_54535339": "-51810926", "54536832":"-51805758", "d9": "-51810953", "cluster_54535338_54535339": "-51810926", "54535257": "-51810894", "54534950": "-51811197", "a6": "-540638352", "a2": "-540638369", "a5": "-51813485", "54531459": "-783385978", "54536832": "-51805674", "f3": "51797737", "54532611": "-51808711.10", "d5": "-51811261", "221":"-67944711", "b3a": "51808253", "b4a": "-67944604", "c2": "-67944600", "c1": "-51963722", "221": "51811223", "d3": "-67944815", "e5": "51808251", "cluster_54532353_54532355_54532356_54532359_54532361": "51798029", "54532329": "-51798039", "a1": "51808344"}# "a1": "51808344", "a1": "-51808710",
    for tls in tls2j:
        tls2outEdge[tls2j[tls]]= tls
    return tls2outEdge
    
def clearPath(vehID, tlsLinkMap, usedTLS, j2tls, tlss):
    # for edge in passedroute:
        # if edge in self.tlsLinkMap:
            # tlid= self.tlsLinkMap[edge][0]
            # tlid= str(tlid)
            # programID= 'utopia'
            # traci.trafficlights.setProgram(tlid, programID) 
            
    #Distance to the tls
    # Todo automatically for more tls
    tlid= ""
    edge= traci.vehicle.getRoadID(vehID)
    
    # check um tls wieder auf alten plan zu setzen
    if edge in j2tls.keys():
        passedIntersection= False
        edges= j2tls.keys()
        if edge in edges:
            passedIntersection= True
            #setBackEdge={v: k for k, v in j2tls.items()}
        if j2tls[edge] in usedTLS and passedIntersection:
            #print("Intersection passed",usedTLS, tlid, passedIntersection) 
            #print 'Set back phase', j2tls[edge]
            programID= '0'
            passedIntersection= False
            #if j2tls[edge] in usedTLS:
            usedTLS.remove(j2tls[edge])
            try:
                traci.trafficlight.setProgram(j2tls[edge] , programID)   #j2tls[edge]         
            except:
                print("Junction has no tls", usedTLS)
     
    
    if edge in tlsLinkMap:
        tlid= tlsLinkMap[edge][0]
        tlid= str(tlid)
        #print tlid
        
        #Distance to the tls
        tls2j= {"a1": "54532608", "a3": "54532540", "f1":"54536753", "d9": "54535620", "a2": "54535263", "a5": "54535257", "a6": "54535186", "f3": "54531922", "d5": "54542095", "221": "54534889", "e5": "54533980", "b3a": "54533985", "d3": "54534192", "b4a": "54534970", "c2": "54534963", "c1": "54534984", "a6": "54534945"}#tls2j= {"maschpl" : "3792043772", "celler": "59654713", "rudolfplatz": "1786940099", "kaelberwiese": "635103577", "maienstr": "3323411891", "kreuzstr": "5502963199", "madamenweg": "5502964928", "broitzemer": "5624016221", "Cyriaksring": "59708186"}
        if tlid in tls2j:
            junction= tls2j[tlid]
        else:
            junction= tlid
        position2= traci.junction.getPosition(junction) 
        #position2= traci.junction.getPosition(tlid) 
        position= traci.vehicle.getPosition(vehID)
        distance= (position[0] - position2[0])**2 + (position[1] - position2[1])**2
        distance= distance**(0.5)
        # test for traffic jam at traffic light
        #print edge
        max_distance= 0
        max_distance2= -1
        if not edge==-1:
            max_distance, max_distance2= calculateTrafficJam(vehID, edge, tlss)
            # korrektur da manche lsa mittelpunkte weit weg von haltelinie sind
            max_distance += 30 
            #print max_distance
        if edge in tlsLinkMap:
            state= ''
            #print distance, max_distance
            if tlid not in usedTLS and distance < max_distance:
                # set TLS Phase
                #todo check for conflicts only
                for i in range(tlsLinkMap[edge][1]): 
                    if not tlid in usedTLS:
                        usedTLS.append(tlid)
                    if i in tlsLinkMap[edge][2:]   :
                        state += 'g'
                    else:
                        state+= 'r'
                # bloeder hack todo aendern
                if (len(traci.trafficlight.getRedYellowGreenState(tlid))> len(state)):
                    for i in range(len(traci.trafficlight.getRedYellowGreenState(tlid))- len(state)):
                        state += 'r'
                #list= traci.trafficlight.getIDList() 
                #print traci.trafficlight.getRedYellowGreenState(tlid)
                traci.trafficlight.setRedYellowGreenState(tlid, state)
                print "Emergency TLS preemption"
            
        if (max_distance2 > -1):
            state= ''
            route=  traci.vehicle.getRoute(vehID)
            current= route.index(edge)
            nextEdgeID= route[current+1]
            if nextEdgeID in tlsLinkMap:
                tlid2= tlsLinkMap[nextEdgeID][0]
                if tlid2 in tls2j:
                        junction2= tls2j[tlid2]
                else:
                        junction2= tlid2
                if tlid== "a3":
                    tlid2= "cluster_54532353_54532355_54532356_54532359_54532361"
                    
                #Distance to the tls
                position2= traci.junction.getPosition(junction2)#tlid2) 
                position= traci.vehicle.getPosition(vehID)
                new_distance= (position[0] - position2[0])**2 + (position[1] - position2[1])**2
                new_distance= new_distance**(0.5)
                if new_distance < max_distance2:
                    # set TLS Phase
                    #todo check for conflicts only
                    for i in range(tlsLinkMap[nextEdgeID][1]): 
                        if not tlid2 in usedTLS:
                            usedTLS.append(tlid2)
                        if i in tlsLinkMap[nextEdgeID][2:]   :
                            state += 'g'
                        else:
                            state+= 'r'           
                    traci.trafficlight.setRedYellowGreenState(tlid2, state)
                    print "Emergency TLS preemption for next TLS", tlid2
                
            
def singleRun(run, evRoute):
    net = sumolib.net.readNet("_use_AIM_weekdays_dido\\data\\bs_nt.net.xml") 
    tlsLinkMap= initLinkMap(net)
    #tls2j= LSA2Junction(net)
    tlss= []
    for tls in net.getTrafficLights():
        tlss.append(tls._id)
    #print("TLS:", tlss)
    
    #print tlsLinkMap
    
    j2tls=initPassedEdges(net)
    #print j2tls
    usedTLS= []
    # start simulation and establish connection
    sumoExe = os.environ["SUMO_HOME"] + "\\bin\\sumo-gui"
    print sumoExe
    sumoConfig = "_use_AIM_weekdays_dido\\data\\sim_dido.sumocfg" #braunschweig_FK\\run.sumocfg"
    sumoCmd = [sumoExe, "-c", sumoConfig, "--tripinfo-output",  "walabi_bs\\tripinfos%s_%s.xml" %(run, evRoute),  "--random"]
    traci.start(sumoCmd) 
    #sumoProcess = subprocess.Popen("%s -c %s --no-step-log --no-duration-log --remote-port %s --summary waitingtimes_%s_%s.xml  --random --tripinfo-output tripinfos_%s_%s.xml" % (sumoExe, sumoConfig, PORT+run, run, evRoute, run, evRoute), shell=True, stdout=sys.stdout)
    #traci.init(PORT+run) 
    print "running"
    emergencyIDs= []
    step=0
    counter = 0
    while step < 3600*10: #traci.simulation.getMinExpectedNumber() > 0: 
        traci.simulationStep() 
        step+= 1
        if step in [1800,1800+3600, 1800+(3600*2), 1800+(3600*3),1800+(3600*4),1800+(3600*5),1800+(3600*6),1800+(3600*7),1800+(3600*8),1800+(3600*9)]: #+ (run* 10 ):
            traci.vehicle.addFull("emergency"+ str(counter), evRoute, typeID="e") 
            emergencyIDs.append("emergency" + str(counter))
            counter += 1
            print "insert"
        vehicles= traci.simulation.getDepartedIDList()

        for vehID in emergencyIDs:
            if vehID in traci.simulation.getArrivedIDList():
                    emergencyIDs.remove(vehID)
                    usedTLS=[]
            else:
                clearPath(vehID, tlsLinkMap, usedTLS, j2tls, tlss)
    print('TraCI Closed')    
    traci.close()
    #shutil.copyfile("corridor\\tls_state.xml", "walabi_corridor\\tls_%s.xml" %(run))


def main():
    evRoutes= ['routedist1']#"S_S", "S_N", "S_E", "S_W", "N_S", "N_N", "N_E", "N_W", "E_S", "E_N", "E_E", "E_W", "W_S", "W_N", "W_E", "W_W"]
    for run in RUNS:
        for route in evRoutes:
            singleRun(run, route)


if __name__ == "__main__":
    main()

