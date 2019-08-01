## Setting Output AFG3k
# AFG 3252 Firmware Version 3.2.3
# Python 3.4.3 Shell
# pyvisa        1.8             (http://pyvisa.sourceforge.net/)
# numpy         1.9.2           (http://numpy.scipy.org/)
# MatPlotLib    1.4.3           (http://matplotlib.sourceforge.net/)
# Author: SimonR
############################################################

import visa
import time
import numpy as np
from struct import unpack
import pylab
import csv

#############################################################
# Globals - Initialize and open connection
#############################################################

rm = visa.ResourceManager()
rm.list_resources()
scope = rm.open_resource('TCPIP0::IP_Address::inst0::INSTR')
print(scope.query("*IDN?"))                                                     #Who are you?
print("ESR says: ", scope.ask("*ESR?"))                                         #Event status register? 
scope.write("*CLS")                                                             #clears the ESR

#############################################################
#run(1)
#############################################################


def SetUp():                                                                        #This function writes all presets to AFG
    scope.write('*RST')                                                         #defaults the instrument
    scope.timeout = 10000                                                   #set standard timeout to 10sec
    r=scope.query("*OPC?")                                                          #Waits for the scope to send a 1 back once default setup is complete
    scope.timeout = 2000

    #settings channel1
    scope.write("source1:function:shape pulse")
    scope.write("source1:frequency 1kHz")
    scope.write("source1:pulse:delay 1us")
    scope.write("source1:voltage:level:immediate:high 2V")
    scope.write("source1:voltage:level:immediate:low 0V")
    scope.write("source1:burst:state on")
    scope.write("source1:burst:ncycles inf")
    scope.write("source1:burst:mode triggered")

    #settings channel2
    scope.write("source2:function:shape pulse")
    scope.write("source2:frequency 1kHz")
    scope.write("source2:pulse:delay 1us")
    scope.write("source2:voltage:level:immediate:high 2V")
    scope.write("source2:voltage:level:immediate:low 0V")
    scope.write("source2:burst:state on")
    scope.write("source2:burst:ncycles inf")
    scope.write("source2:burst:mode triggered")

    #trigger settings and output
    scope.write("trigger:sequence:source external")
    scope.write("output1:state on")
    scope.write("output2:state on")
    return(0)

def Fire():
    #scope.write("trigger:sequence:immediate")                                  #Sends a force trigger to start outputs simultaneously

    return(0)

def close():                                                                         #closes connection 
    rm.close()
    return(0)



#############################################################
#Main (like C++)
#############################################################

if __name__ == "__main__":
    SetUp()
    Fire()
    close()
