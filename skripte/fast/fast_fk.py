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
    max_distance= 200
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
            # set extend green or reduce red phase
            state= traci.trafficlight.getRedYellowGreenState(tlid)
            isgreen= False
            index= 0
            for i in range(tlsLinkMap[edge][1]): 
                usedTLS.append(tlid)
                if i in tlsLinkMap[edge][2:] and state[index].lower()== 'g': #upper cases
                    isgreen= True
                    print "Green phase" , i               
                index += 1
            if isgreen:
                nextswitch= traci.trafficlight.getNextSwitch(tlid) - traci.simulation.getTime()
                if nextswitch < 25:
                    print("Extend green: " + str(25-nextswitch))
                    traci.trafficlight.setPhaseDuration(tlid, 25-nextswitch)
                else:
                    print("Time table fits. Green duration: " +str(nextswitch))
            else:
                #reduce red
                traci.trafficlight.setPhaseDuration(tlid, 1)
                print("Reduce red phase")
    return usedTLS

def singleRun(run, evRoute):
    net = sumolib.net.readNet("braunschweig_FK\\net\\net.net.xml") #sumonet.NetReader()
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
    sumoConfig = "braunschweig_FK\\run.sumocfg"
	#--step-length 0.1
    sumoCmd = [sumoExe, "-c", sumoConfig, "--tripinfo-output",  "fast_fk_results\\tripinfos_%s_%s.xml" %(run, evRoute),  "--random"]
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
            elif(len(usedTLS)<1):
                usedTLS=clearPath(vehID, tlsLinkMap, usedTLS)
    print('TraCI Closed')    
    traci.close()
    shutil.copyfile("braunschweig_FK\\tls_state.xml", "fast_fk_results\\tls_%s.xml" %(run))

def main():
    evRoutes= ['routedist1']#"S_S", "S_N", "S_E", "S_W", "N_S", "N_N", "N_E", "N_W", "E_S", "E_N", "E_E", "E_W", "W_S", "W_N", "W_E", "W_W"]
    for run in RUNS:
        for route in evRoutes:
            singleRun(run, route)


if __name__ == "__main__":
    main()

