#-------------------------------------------------------------------------------
# Name:  DPO MSO 2000 Series Search and Mark on CH1 get Value on CH2
# Purpose:  This example demonstrates how to use the Search and Marks feature of
# the DPO/MSO 2000(B) Series instruments to find an event of interest on one
# channel, but then read back the value at that same point in time on another
# channel.
#
# Created:  2016-09-27
#
# Development Environment: Python 3.4, PyVisa 1.8, NI-VISA 2016, Windows 8.1
#
# Compatible Instruments: DPO/MSO 2000(B) Series Oscilloscopes
#
# Compatible Interfaces:  USB, Ethernet
#
# Tektronix provides the following example "AS IS" with no support or warranty.
#
#-------------------------------------------------------------------------------

import visa # pyvisa.org
import time # std library

visaResourceAddr = "MSO2024"

rm = visa.ResourceManager()
scope = rm.open_resource(visaResourceAddr)

print(scope.query('*IDN?'))

scope.write("*RST")
time.sleep(2.5)

scope.write("SELect:CH2 1")
scope.write("SELect:CH1 1")
scope.write("AUTOSet EXECute")
time.sleep(5)

# Setup Search and Marks
scope.write("SEARCH:SEARCH1:TRIGger:A:EDGE:SOUrce CH1")
scope.write("SEARCH:SEARCH1:TRIGger:A:TYPe EDGe")
scope.write("SEARCH:SEARCH1:TRIGger:A:EDGE:SLOpe FALL")
scope.write("SEARCH:SEARCH1:TRIGger:A:LEVel:CH1 2.5")
scope.write("SEARCH:SEARCH1:STATE ON")

# Give the search and marks time to search and mark
time.sleep(1)

# Use FPAnel:PRESS NEXt and FPAnel:PRESS PREv as many times as necessary to select the correct mark
scope.write("FPAnel:PRESS PREv")

# MARK:SELected:STARt? and MARK:SELected:END? return where the mark starts and ends.  Even for an edge event the start and end are different because the scope uses hysteresis to detect edge transitions, otherwise the edge detection would be affected by noise.  For this reason you'll want to retrieve the start and end and average the two to get the position that is right in the middle.
start = scope.query("MARK:SELected:STARt?")
end = scope.query("MARK:SELected:END?")
position_in_percent = (float(end) + float(start))/float(2)


scope.write("CURSor:FUNCtion VBArs")
# The cursors will require some initial setup so the marker position in percent can be directly applied to cursor position in percent.
scope.write("CURSor:VBArs:UNIts PERcent")
scope.write("CURSor:VBArs:POSITION1 -50")
scope.write("CURSor:VBArs:POSITION2 150")
scope.write("CURSor:VBArs:USE CURrent")
time.sleep(0.25)
# Cursor positioning is now setup so the marker percent can be directly applied

scope.write("CURSor:VBArs:POSITION1 {0}".format(position_in_percent))
scope.write("SELect:CH2 1")

time.sleep(1)

value = scope.query("CURSor:VBArs:HPOS1?")
print("Value on CH2 at Marked Position is {0}".format(value))

scope.close()

