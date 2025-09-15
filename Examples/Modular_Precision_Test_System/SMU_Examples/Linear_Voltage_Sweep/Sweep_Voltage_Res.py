#################################################################################
#
# Script File: Sweep_Voltage_Res.tsp
# 
#     ************************************************************************
#     *** Copyright Tektronix, Inc.                                        ***
#     *** See www.tek.com/sample-license for licensing terms.              ***
#     ************************************************************************
# 
# Description:
#     This script is example code, which creates (and subsequently calls) several
#     functions that can be used with the Model MP5000 Based SMUs to perform a
# 	  voltage sweeping. The purpose is show that you can perform a resistor 
# 	  device characterization with the SMUs. As written, one channel of SMU is 
# 	  assigned to one terminal for the high and the other for the low terminal.
# 	  For the same purpose, SMU support it in run time evironment and in trigger model.
# 	  Upon completion of each test, the data is printed to the TSP Toolkit Console 
# 	  in a format that is suitable for copying and pasting into Microsoft Excel for 
# 	  graphing and analysis.
# 
# Required Equipment: 1 Model MP5000 Mainframe 
# 					  1 channel SMU (MSMU Series)
# 					  1 Resistive load
# 
# Note:  The functions do not perform any error checking.  It is the user's 
#        responsibility to specify settings that are compatible with the 
#        instrument model being used, and with its power envelope.
#        
# Note:  It is the user's responsibility to follow all safety guidelines given in 
#        the instrument's Reference Manual.  This is especially critical if 
#        voltages in excess of 42VDC will be present in the test circuits.  Such 
#        voltage levels are hazardous. 
#        
# Functions created by this script:
#     * DC_Voltage_Sweep_Resistor_RunTimeEnv({slot_no,smu_channel},,{startV,stopV,noPoints,limitI},{measRangeV, measRangeI, autoRangeI, nplc,mDelay,remoteSense})
#     * DC_Voltage_Sweep_Resistor_inTriggerModel({slot_no,smu_channel},,{startV,stopV,noPoints,limitI},{measRangeV, measRangeI, autoRangeI, nplc,mDelay,remoteSense},tm_name)
# 
# Example Usage:
#     * DC_Voltage_Sweep_Resistor_RunTimeEnv({1,1},-5,5,101,1,6, 1, 1, 1,0)
# 	  * DC_Voltage_Sweep_Resistor_inTriggerModel({1,1},-5,5,101,1,6, 1, 1, 1,0,"TM_sweepV")
#	
#################################################################################

def plotResults(x, y):
    import matplotlib.pyplot as pt
    pt.scatter(x, y, label="R")
    pt.xlabel("Supplied voltage (V)")
    pt.ylabel("Resistance (Ω)")
    pt.title("Resistor Characterization")
    pt.grid(True)
    pt.show()

import pyvisa

# Configure Visa Connection
rm = pyvisa.ResourceManager()
inst = rm.open_resource('TCPIP0::192.168.0.2::5025::SOCKET')
# for using the sockets based implementation
inst.write_termination = "\n"
inst.read_termination = "\n"
inst.send_end = True
inst.timeout = 10000

# information of SMU
slot_no 		= 1
sweepV_channel 	= 1
# Source Settings
startV 		    = -5
stopV 		    = 5
noPoints 		= 100
limitI 		    = 1
# Measure Settings
measRangeV      = 6
measRangeI      = 0.100
autoRangeI      = True 
nplc 			= 1
mDelay 		    = 0
remoteSense 	= False
tm_name		    = "TM_sweepV"

# Channel assignment
smu = f"slot[{slot_no}].smu[{sweepV_channel}]"
inst.write(f"{smu}.reset()")

# Source settings
inst.write(f"{smu}.source.func = {smu}.FUNC_DC_VOLTAGE")
inst.write(f"{smu}.source.rangev = {max(abs(startV), abs(stopV))}")
inst.write(f"{smu}.source.limiti = {limitI}")
inst.write(f"{smu}.source.levelv = 0")
# Measure settings
inst.write(f"{smu}.measure.rangev = {measRangeV}")
inst.write(f"{smu}.measure.nplc = {nplc}")

if autoRangeI:
    inst.write(f"{smu}.measure.autorangei = 1")
else:
    inst.write(f"{smu}.measure.autorangei = 1")
    inst.write(f"{smu}.measure.rangei = {measRangeI}")

if remoteSense:
    inst.write(f"{smu}.sense = {smu}.SENSE_4WIRE")
else:
    inst.write(f"{smu}.sense = {smu}.SENSE_2WIRE")

# Buffer clear
inst.write(f"{smu}.defbuffer1.clear()")
inst.write(f"{smu}.defbuffer1.appendmode = 1")
inst.write(f"{smu}.defbuffer2.clear()")
inst.write(f"{smu}.defbuffer2.appendmode = 1")

# Setup trigger model source levels for linear voltage sweep
inst.write(f"{smu}.trigger.source.linearv({startV}, {stopV}, {noPoints})")
# Set trigger model iv measurements to store in default buffers
inst.write(f"{smu}.trigger.measure.iv({smu}.defbuffer1, {smu}.defbuffer2)")

# Configure trigger model
triggerModel = f"slot[{slot_no}].trigger.model"
inst.write(f"{triggerModel}.create(\"{tm_name}\")")
# Step soruce level to next value in sweep
inst.write(f"{triggerModel}.addblock.source.action.step(\"{tm_name}\", \"sweepV_IV\", {sweepV_channel})")
# Constant delay in trigger model is very accurate
inst.write(f"{triggerModel}.addblock.delay.constant(\"{tm_name}\", \"IV_delay\", {mDelay})")
# Measure iv and store in buffers
inst.write(f"{triggerModel}.addblock.measure(\"{tm_name}\", \"measure_IV\", {sweepV_channel}, 1)")
# Loop for each value in sweep
inst.write(f"{triggerModel}.addblock.branch.counter(\"{tm_name}\", \"branch-counter\", \"sweepV_IV\", {noPoints})")

# Execute sweep, delete trigger model when finished
inst.write(f"{smu}.source.output = 1")
inst.write(f"{triggerModel}.initiate(\"{tm_name}\")")
inst.write(f"waitcomplete()")
inst.write(f"{smu}.source.output = 0")
inst.write(f"{triggerModel}.delete(\"{tm_name}\")")

# Retrieve defbuffers
defbuffer1 = inst.query(f"printbuffer(1, {smu}.defbuffer1.n, {smu}.defbuffer1)").split(",")
defbuffer1 = [float(x) for x in defbuffer1]
defbuffer2 = inst.query(f"printbuffer(1, {smu}.defbuffer2.n, {smu}.defbuffer2)").split(",")
defbuffer2 = [float(x) for x in defbuffer2]
resists = [x/y for x,y in zip(defbuffer2, defbuffer1)]

# Display readings to terminal
print("V","I","R",sep="\t\t")
for i in range(len(defbuffer1)):
    print(f"{defbuffer2[i]:.5e}",
          f"{defbuffer1[i]:.5e}",
          f"{resists[i]:.5e}",
          sep="\t"
          )

inst.clear()
inst.close()

plotResults(defbuffer2, resists)