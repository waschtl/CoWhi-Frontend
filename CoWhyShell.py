# -*- coding: utf-8 -*-
#!/usr/bin/python2.6
# main.py

"""
    Skript um den Roboter direkt über die  Shell anzusteuern. Wird eigentlich nur 
    für testzwecke gebraucht, und sollte automatisch mit den neuen Funktionen des
    `robot_interface` mitwachsen...
    
    26.10.2012    erstellen des Grundgerüsts und ersten brauchbaren Prototypen
    
    TODO:
        robot_interface.py einbinden und laufenden Workerthread erstellen
"""

import os
import Queue
import sys
import time
     
import robot_interface
from debug import debug

"""
    #mögliche Jobs für das Interface
jobs = {1:  'send_string',
        2:  'read_skid_pos',
        3:  'skid_goto',
        4:  'do_order',
        5:  'do_pourer',
        99: 'delay'}
"""        

debug.DEBUG = True

    
def main():
    """
        TDOD die globalen q und robbi evtl mal loswerden?
             --> alternative überlegen
    """ 
    q = Queue.Queue()
    robbi = robot_interface.RobotInterface(q, 'ttyUSB', 9600)
    
    print len(sys.argv)
    
    if len(sys.argv) == 4:
        
        job = sys.argv[1]
        jobParam1 = str(sys.argv[2])
        jobParam2 = int(sys.argv[3])
        
            #dieser spezielle Teil ist erst mal nur zum Dosierer betätigen
        if int(job) <> 5:
            exit 
        print 'starte Dosierer:'
        print jobParam1
        print jobParam2
        #robbi.start()  
        #q.put((int(job), jobParam1, jobParam2))
        time.sleep(1)
        robbi.do_pourer(jobParam1, jobParam2)
        while robbi.busy:
            print robbi.jobdiscr
            time.sleep(0.1)
            #Thread für RoboterInterface töten
        robbi.stop_thread = True
        
    elif len(sys.argv) == 3:    
        robbi.start()  
        job = sys.argv[1]
        jobParam = sys.argv[2]
  
        q.put((int(job), jobParam))
        time.sleep(1)
        while robbi.busy:
            print robbi.jobdiscr
            time.sleep(0.1)

            #Thread für RoboterInterface töten
        robbi.stop_thread = True
    
    else:
        print "Unpassende Parameter"
        for item in robot_interface.jobs:
            print item , ' - ' , robot_interface.jobs[item]
    
if __name__ == "__main__":
    main()
    
    
    
    

