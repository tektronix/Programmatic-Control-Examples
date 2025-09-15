
#################################################################################
#
# Script File: Sweep_Current_Diode.py
# 
#     ************************************************************************
#     *** Copyright Tektronix, Inc.                                        ***
#     *** See www.tek.com/sample-license for licensing terms.              ***
#     ************************************************************************
# 
# Description:
#     This script is example code, which creates (and subsequently calls) several
#     functions that can be used with the Model MP5000 Based SMUs to perform a
# 	  current sweeping. The purpose is show that you can perform a diode device
# 	  characterization with the SMUs. As written, one channel of SMU is 
# 	  assigned to the anode for the high and cathode for the low terminal.
# 	  Upon completion of each test, the data is printed to the TSP Toolkit Console 
# 	  in a format that is suitable for copying and pasting into Microsoft Excel for 
# 	  graphing and analysis.
# 
# Required Equipment: 1 Model MP5000 Mainframe 
# 					  1 channel SMU (MSMU Series)
# 					  1 Diode
# 
# Note:  The functions do not perform any error checking.  It is the user's 
#        responsibility to specify settings that are compatible with the 
#        instrument model being used, and with its power envelope.
#        
# Note:  It is the user's responsibility to follow all safety guidelines given in 
#        the instrument's Reference Manual.  This is especially critical if 
#        voltages in excess of 42VDC will be present in the test circuits.  Such 
#        voltage levels are hazardous. 
#################################################################################

def plotResults(x, y):
    import matplotlib.pyplot as pt

    pt.plot(x, y, "o-")
    pt.xlabel("Supplied Current (A)")
    pt.ylabel("Measured Voltage (V)")
    pt.title("Diode Current Sweep")

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
IF_channel 	    = 1
# Source Settings
startIF 		= 0
stopIF 		    = 12e-3
noPoints 		= 31
rangeI 		    = 100e-3
limitV 		    = 3
# Measure Settings
measRangeV      = 6
nplc 			= 1
mDelay 		    = 0
remoteSense 	= False
tm_name		    = "TM_Diode"

# Channel assignment
smu = f"slot[{slot_no}].smu[{IF_channel}]"
inst.write(f"{smu}.reset()")

# Source settings
inst.write(f"{smu}.source.func = {smu}.FUNC_DC_CURRENT")
inst.write(f"{smu}.source.rangei = {rangeI}")
inst.write(f"{smu}.source.leveli = 0")
inst.write(f"{smu}.source.limitv = {limitV}")
# Measure settings
inst.write(f"{smu}.measure.rangev = {measRangeV}")
inst.write(f"{smu}.measure.rangei = {rangeI}")
inst.write(f"{smu}.measure.nplc = {nplc}")
inst.write(f"{smu}.measure.autorangei = 1")

if remoteSense:
    inst.write(f"{smu}.sense = {smu}.SENSE_4WIRE")
else:
    inst.write(f"{smu}.sense = {smu}.SENSE_2WIRE")

# Buffer clear
inst.write(f"{smu}.defbuffer1.clear()")
inst.write(f"{smu}.defbuffer1.appendmode = 1")
inst.write(f"{smu}.defbuffer2.clear()")
inst.write(f"{smu}.defbuffer2.appendmode = 1")

# Configure trigger model source for a linear current sweep
inst.write(f"{smu}.trigger.source.lineari({startIF}, {stopIF}, {noPoints})")
# Set trigger model current and voltage measurements to be stored in the default buffers
inst.write(f"{smu}.trigger.measure.iv({smu}.defbuffer1, {smu}.defbuffer2)")

# Configure trigger model
triggerModel = f"slot[{slot_no}].trigger.model"
inst.write(f"{triggerModel}.create(\"{tm_name}\")")
# Set the source level to next value in linear current sweep
inst.write(f"{triggerModel}.addblock.source.action.step(\"{tm_name}\", \"IF_sweep\", {IF_channel})")
# Delay in trigger model is very accurate
inst.write(f"{triggerModel}.addblock.delay.constant(\"{tm_name}\", \"IF_delay\", {mDelay})")
# Measure iv and store in default buffers
inst.write(f"{triggerModel}.addblock.measure(\"{tm_name}\", \"VF_measure\", {IF_channel}, 1)")
# Loop for a set number of iterations
inst.write(f"{triggerModel}.addblock.branch.counter(\"{tm_name}\", \"IF_branch\", \"IF_sweep\", {noPoints})")
# Return source to 0
inst.write(f"{triggerModel}.addblock.source.action.bias(\"{tm_name}\", \"IF_bias\", {IF_channel})")

# Execute sweep
inst.write(f"{smu}.source.output = 1")
# Initiate trigger model, delete when finished
inst.write(f"{triggerModel}.initiate(\"{tm_name}\")")
inst.write(f"waitcomplete()")
inst.write(f"{smu}.source.output = 0")
inst.write(f"{triggerModel}.delete(\"{tm_name}\")")

# Retrieve defbuffers
defbuffer1 = inst.query(f"printbuffer(1, {smu}.defbuffer1.n, {smu}.defbuffer1)").split(",")
defbuffer1 = [float(x) for x in defbuffer1]
defbuffer2 = inst.query(f"printbuffer(1, {smu}.defbuffer2.n, {smu}.defbuffer2)").split(",")
defbuffer2 = [float(x) for x in defbuffer2]

# Display readings to terminal
print("IF","VF",sep="\t\t")
for i in range(len(defbuffer1)):
    print(f"{defbuffer1[i]:.5e}", 
          f"{defbuffer2[i]:.5e}",
          sep="\t"
          )

inst.clear()
inst.close()

plotResults(defbuffer1, defbuffer2)