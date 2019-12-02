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
 
# generates a map mit TLIDs and juctions
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
        #print edge
        tlid= tlsLinkMap[edge][0]
        tlid= str(tlid)
        #print tlid
        
        #Distance to the tls
        tls2j= {"a1": "54532608", "a3": "54532540", "f1":"54536753", "d9": "54535620", "a2": "54535263", "a5": "54535257", "a6": "54535186", "f3": "54531922", "d5": "54542095", "221": "54534889", "e5": "54533980", "b3a": "54533985", "d3": "54534192", "b4a": "54534970", "c2": "54534963", "c1": "54534984", "a6": "54534945"}#{"maschpl" : "3792043772", "celler": "59654713", "rudolfplatz": "1786940099", "kaelberwiese": "635103577", "maienstr": "3323411891", "kreuzstr": "5502963199", "madamenweg": "5502964928", "broitzemer": "5624016221", "broitzemer": "5749804898", "Cyriaksring": "59708186"}
        if tlid in tls2j:
            junction= tls2j[tlid]
        else:
            junction= tlid
        position2= traci.junction.getPosition(junction) 
        position= traci.vehicle.getPosition(vehID)
        distance= (position[0] - position2[0])**2 + (position[1] - position2[1])**2
        distance= distance**(0.5)
        # test for traffic jam at traffic light
        #print edge
        max_distance= 200
       
        if edge in tlsLinkMap:
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
    net = sumolib.net.readNet("_use_AIM_weekdays_dido\\data\\bs_nt.net.xml")    #braunschweig_FK\\net\\net.net.xml") #sumonet.NetReader()
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
    sumoExe = os.environ["SUMO_HOME"] + "\\bin\\sumo"
    print sumoExe
    sumoConfig = "_use_AIM_weekdays_dido\\data\\sim_dido.sumocfg" #braunschweig_FK\\run.sumocfg"
    sumoCmd = [sumoExe, "-c", sumoConfig, "--tripinfo-output",  "fast_bs\\tripinfos%s_%s.xml" %(run, evRoute),  "--random"]
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
    #shutil.copyfile("SUMO_Sirene\\tls_state.xml", "fast_sirene\\tls_%s.xml" %(run))

def main():
    evRoutes= ['routedist1']#"S_S", "S_N", "S_E", "S_W", "N_S", "N_N", "N_E", "N_W", "E_S", "E_N", "E_E", "E_W", "W_S", "W_N", "W_E", "W_W"]
    for run in RUNS:
        for route in evRoutes:
            singleRun(run, route)


if __name__ == "__main__":
    main()

