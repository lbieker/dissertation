from time import clock
import random, sys
import traci
import subprocess, sys, socket, time, struct, random
from xml.sax import saxutils, make_parser, handler
import sumolib
import shutil
import os

PORT= 8350
RUNS= range(50)

def calculateTrafficJam(edgeID):
    veh_number= 0
    #todo automatically
    edge2lane= {'166445405#0': 5, 'e1': 2, 's1': 2, '61734682#3.75': 3, '61734682#3.115': 5, '318881710#0': 3, 'n1': 2, '314915850#0': 5, '314915843': 4, 'w1': 3}
    moreLanes= {'166445405#0': ['s1'], '61734682#3.115':['61734682#3.75', 'e1'], 'n1': ['318881710#0'], '314915850#0': ['314915843', 'w1']}
    lanes= []
    
    if edgeID in edge2lane.keys():
        #print edgeID, edge2lane[edgeID]
        for id in range(edge2lane[edgeID]):
            laneID= edgeID + '_' + str(id+2) # pedestrian and bike way are excluded
            lanes.append(laneID)
        for laneID in lanes:
            num_lane= 0  
            try: 
                veh_lane= traci.lane.getLastStepVehicleNumber(laneID)
                num_lane += 1
                #print laneID, veh_lane
                if veh_lane > veh_number:
                    veh_number= veh_lane
                    if traci.lane.getLastStepOccupancy(laneID)> 0.8:
                        newMax= 0
                        #check moreLanes and add
                        if edgeID in moreLanes:
                            for followLane in moreLanes[edgeID]:
                                vehs= traci.lane.getLastStepVehicleNumber(followLane)
                                if vehs > newMax:
                                    newMax= vehs
                            veh_number += newMax
            except:
                print laneID, 'gibts nicht'
    time_free=  (veh_number * 2) + 5
    max_distance= time_free * 13.9
    return max_distance
    
    
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
    return LSAmap
    
    
def clearPath(vehID, tlsLinkMap, usedTLS):
    # for edge in passedroute:
        # if edge in self.tlsLinkMap:
            # tlid= self.tlsLinkMap[edge][0]
            # tlid= str(tlid)
            # programID= 'utopia'
            # traci.trafficlights.setProgram(tlid, programID) 
            
    #Distance to the tls
    # Todo automatically for more tls
    position2= traci.junction.getPosition("C") 
    position= traci.vehicle.getPosition(vehID)
    edge= traci.vehicle.getRoadID(vehID)
    distance= (position[0] - position2[0])**2 + (position[1] - position2[1])**2
    distance= distance**(0.5)
    # test for traffic jam at traffic light
    #print edge
    max_distance= 100
    #if not edge==-1:
    #    max_distance= calculateTrafficJam(edge)
    #    #print max_distance
    tlid= "gneJ0"
    passedIntersection= False
    edges= ["s2", "447787390#1", "n2", "e2"]
    if edge in edges:
        passedIntersection= True
    if tlid in usedTLS and passedIntersection:
        #print 'Set back phase', tlid
        programID= '0'
        traci.trafficlight.setProgram(tlid, programID) 
    elif edge in tlsLinkMap:
        state= ''
        #print distance, max_distance
        if tlid not in usedTLS and distance < max_distance:
            # set TLS Phase
            print("Change TLS")
            #todo check for conflicts only
            for i in range(tlsLinkMap[edge][1]): 
                usedTLS.append(tlid)
                if i in tlsLinkMap[edge][2:]   :
                    state += 'g'
                else:
                    state+= 'r'
            # bloeder hack todo aendern
            for i in range(8):
                state += 'r'
            #list= traci.trafficlight.getIDList() 
            #print traci.trafficlight.getRedYellowGreenState(tlid)
            traci.trafficlight.setRedYellowGreenState(tlid, state)
            #print "Emergency TLS preemption"

def singleRun(run, evRoute):
    net = sumolib.net.readNet("SUMO_Sirene\\sirene.net.xml") #sumonet.NetReader()
    tlsLinkMap= initLinkMap(net)
    #print tlsLinkMap
    usedTLS= []
    tlsLinkMap["n1"]= tlsLinkMap["318881710#0"]
    tlsLinkMap['s1'] = tlsLinkMap['166445405#0']
    tlsLinkMap['61734682#3.75'] = tlsLinkMap['61734682#3.115']
    tlsLinkMap['e1'] = tlsLinkMap['61734682#3.115']
    tlsLinkMap['314915843']= tlsLinkMap['314915850#0']
    tlsLinkMap['w1']= tlsLinkMap['314915850#0']
    # start simulation and establish connection
    sumoExe = os.environ["SUMO_HOME"] + "\\bin\\sumo"
    print sumoExe
    sumoConfig = "SUMO_Sirene\\sirene.sumocfg"
	#--step-length 0.1
    sumoCmd = [sumoExe, "-c", sumoConfig, "--tripinfo-output",  "stream_results_fk\\tripinfos_%s_%s.xml" %(run, evRoute),"--random"]
    traci.start(sumoCmd) 
    #sumoProcess = subprocess.Popen("%s -c %s --no-step-log --no-duration-log --remote-port %s --summary waitingtimes_%s_%s.xml  --random --tripinfo-output tripinfos_%s_%s.xml" % (sumoExe, sumoConfig, PORT+run, run, evRoute, run, evRoute), shell=True, stdout=sys.stdout)
    #traci.init(PORT+run) 
    print "running"
    emergencyIDs= []
    step=0
    while step < 3600: #traci.simulation.getMinExpectedNumber() > 0: 
        traci.simulationStep() 
        step+= 1
        if step == 900 + (run* 10 ):
            traci.vehicle.addFull("emergency", evRoute, typeID="e") #"S_E", "S_W", "E_S" evRoute 
            emergencyIDs.append("emergency")
            print "insert"
        vehicles= traci.simulation.getDepartedIDList()

        for vehID in emergencyIDs:
            if vehID in traci.simulation.getArrivedIDList():
                    emergencyIDs.remove(vehID)
                    usedTLS=[]
            else:
                clearPath(vehID, tlsLinkMap, usedTLS)
    print('TraCI Closed')    
    traci.close()
    shutil.copyfile("SUMO_Sirene\\tls_state.xml", "stream_results_sirene\\tls_%s.xml" %(run))

def main():
    evRoutes= ['routedist1']#"S_S", "S_N", "S_E", "S_W", "N_S", "N_N", "N_E", "N_W", "E_S", "E_N", "E_E", "E_W", "W_S", "W_N", "W_E", "W_W"]
    for run in RUNS:
        for route in evRoutes:
            singleRun(run, route)


if __name__ == "__main__":
    main()

