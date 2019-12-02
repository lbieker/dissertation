from time import clock
import random, sys
import traci
import subprocess, sys, socket, time, struct, random
from xml.sax import saxutils, make_parser, handler
import sumolib
import shutil
import os

PORT= 8880
RUNS= range(50)
    
                
def singleRun(run, evRoute):
    net = sumolib.net.readNet("braunschweig_FK\\net\\net.net.xml")    #braunschweig_FK\\net\\net.net.xml") #sumonet.NetReader()
    #print tlsLinkMap
    usedTLS= []
    # tlsLinkMap["n1"]= tlsLinkMap["318881710#0"]
    # tlsLinkMap['s1'] = tlsLinkMap['166445405#0']
    # tlsLinkMap['61734682#3.75'] = tlsLinkMap['61734682#3.115']
    # tlsLinkMap['e1'] = tlsLinkMap['61734682#3.115']
    # tlsLinkMap['314915843']= tlsLinkMap['314915850#0']
    # tlsLinkMap['w1']= tlsLinkMap['314915850#0']
    # start simulation and establish connection
    sumoExe = os.environ["SUMO_HOME"] + "\\bin\\sumo"
    print sumoExe
    sumoConfig = "braunschweig_FK\\run.sumocfg" #braunschweig_FK\\run.sumocfg"
	#--step-length 0.1
    sumoCmd = [sumoExe, "-c", sumoConfig, "--tripinfo-output",  "without_results_fk\\tripinfos_%s_%s.xml" %(run, evRoute), "--random"]
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
            traci.vehicle.addFull("emergency", evRoute, typeID="e") 
            emergencyIDs.append("emergency")
            print "insert"
    print('TraCI Closed')    
    traci.close()
    shutil.copyfile("braunschweig_FK\\tls_state.xml", "without_results_fk\\tls_%s.xml" %(run))


def main():
    evRoutes= ['routedist1']
    for run in RUNS:
        for route in evRoutes:
            singleRun(run, route)


if __name__ == "__main__":
    main()

