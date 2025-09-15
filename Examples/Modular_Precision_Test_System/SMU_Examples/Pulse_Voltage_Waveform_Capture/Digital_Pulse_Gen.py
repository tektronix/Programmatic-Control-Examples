#################################################################################
# 
# Script File: Pulse_Waveform_Capture_MSMU_MP5000.py
# 
#     ************************************************************************
#     *** Copyright Tektronix, Inc.                                        ***
#     *** See www.tek.com/sample-license for licensing terms.              ***
#     ************************************************************************
# 
# Description:
#     This script is example code, which creates (and subsequently calls) several
#     functions that can be used with the Model MP5000 Based SMUs to perform a
# 	  voltage sweeping. The purpose is show that you can make digitiazer for pulse train
# 	  As written, one channel of SMU is assigned to the high and the other to the low 
# 	  terminal. The script generates voltage pulses measuring voltage and current with
# 	  digitizers at a same time. 
# 	  For the same purpose, SMU support is in run time evironment and in trigger model.
# 	  Upon completion of each test, the data is printed to the TSP Toolkit Console 
# 	  in a format that is suitable for copying and pasting into Microsoft Excel for 
# 	  graphing and analysis.
# 
# Required Equipment: 1 Model MP5000 Mainframe 
# 					  1 channel SMU 
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
#################################################################################

def plotResults(x, y):
    import matplotlib.pyplot as pt
    pt.plot(x, y, 'o-')
    pt.xlabel("Time (s)")
    pt.ylabel("Measured Voltage (V)")
    pt.title("Digital Pulse Generation")
    pt.grid(True)
    pt.show()

import pyvisa
import math

# Configure Visa Connection
rm = pyvisa.ResourceManager()
inst = rm.open_resource('TCPIP0::192.168.0.2::5025::SOCKET')
# for using the sockets based implementation
inst.write_termination = "\n"
inst.read_termination = "\n"
inst.send_end = True
inst.timeout = 10000

# SMU channel Settings
slot_no 		= 1
sweepV_channel	= 1
# Source Settings
startV 		    = 1
stopV 		    = 10
noPoints 	    = 10
limitI 		    = 1
# Measure Settings
measRangeV    	= 10
measRangeI    	= 1
remoteSense 	= False

# Pulse Settings
pulsePeriod	  	= 5e-3  # pulsePeriod should be longer than pulseWidth + mDelay + apertureTime
pulseWidth	  	= 3e-3
mDelay 		    = 1e-3
apertureTime	= 100e-6

tm_name			= "TM_pulse_digitizer"

smu = f"slot[{slot_no}].smu[{sweepV_channel}]"
inst.write(f"{smu}.reset()")

# Source settings
inst.write(f"{smu}.source.func = {smu}.FUNC_DC_VOLTAGE")
inst.write(f"{smu}.source.rangev = {max(abs(startV), abs(stopV))}")
inst.write(f"{smu}.source.limiti = {limitI}")
inst.write(f"{smu}.source.levelv = 0")
# Measure settings
inst.write(f"{smu}.measure.rangev = {measRangeV}")
inst.write(f"{smu}.measure.rangei = {measRangeI}")
inst.write(f"{smu}.measure.aperture = {apertureTime}")
inst.write(f"{smu}.measure.autorangei = 0")

if remoteSense:
    inst.write(f"{smu}.sense = {smu}.SENSE_4WIRE")
else:
    inst.write(f"{smu}.sense = {smu}.SENSE_2WIRE")

# Buffer clear
inst.write(f"{smu}.defbuffer1.clear()")
inst.write(f"{smu}.defbuffer1.appendmode = 1")
inst.write(f"{smu}.defbuffer2.clear()")
inst.write(f"{smu}.defbuffer2.appendmode = 1")
# Calculate number of points
nPoints = math.ceil(((pulsePeriod * noPoints) + pulsePeriod) / apertureTime)

# Configure trigger model source for linear voltage sweep
inst.write(f"{smu}.trigger.source.linearv({startV}, {stopV}, {noPoints})")
# Set trigger model to measure i/v and store in default buffers
inst.write(f"{smu}.trigger.measure.iv({smu}.defbuffer1, {smu}.defbuffer2)")

# Configure trigger model
triggerModel = f"slot[{slot_no}].trigger.model"
inst.write(f"{triggerModel}.create(\"{tm_name}\")")
# Measureoverlapped allows measurements to be taken while triggermodel is running in parallel
inst.write(f"{triggerModel}.addblock.measureoverlapped(\"{tm_name}\", \"measure_IV\", {sweepV_channel}, {nPoints})")
inst.write(f"{triggerModel}.addblock.delay.constant(\"{tm_name}\", \"prepulse_delay\", {pulsePeriod/2})")
# Advance to next voltage value in voltage sweep
inst.write(f"{triggerModel}.addblock.source.action.step(\"{tm_name}\", \"sweepV_IV\", {sweepV_channel})")
inst.write(f"{triggerModel}.addblock.delay.constant(\"{tm_name}\", \"meas_pulse_width\", {pulseWidth}, \"sweepV_IV\")")
# Set source level to 0
inst.write(f"{triggerModel}.addblock.source.action.bias(\"{tm_name}\", \"pulse_bias\", {sweepV_channel})")
inst.write(f"{triggerModel}.addblock.delay.constant(\"{tm_name}\", \"mean_pulse_period\", {pulsePeriod}, \"sweepV_IV\")")
# Loop through all voltage sweep values
inst.write(f"{triggerModel}.addblock.branch.counter(\"{tm_name}\", \"branch-counter\", \"sweepV_IV\", {noPoints})")
inst.write(f"{triggerModel}.addblock.delay.constant(\"{tm_name}\", \"postpulse_delay\", {pulsePeriod})")

# Initiate trigger model and delete when finished
inst.write(f"{smu}.source.output = 1")
inst.write(f"{triggerModel}.initiate(\"{tm_name}\")")
inst.write(f"waitcomplete()")
inst.write(f"{smu}.source.output = 0")
inst.write(f"{triggerModel}.delete(\"{tm_name}\")")

# Retrieve buffer data
timestamps = inst.query(f"printbuffer(1, {smu}.defbuffer1.n, {smu}.defbuffer1.timestamps)").split(",")
timestamps = [float(x) for x in timestamps]
defbuffer1 = inst.query(f"printbuffer(1, {smu}.defbuffer1.n, {smu}.defbuffer1)").split(",")
defbuffer1 = [float(x) for x in defbuffer1]
defbuffer2 = inst.query(f"printbuffer(1, {smu}.defbuffer2.n, {smu}.defbuffer2)").split(",")
defbuffer2 = [float(x) for x in defbuffer2]

# Display buffer data
print("Time","V","I",sep="\t\t")
for i in range(len(defbuffer1)):
    print(f"{timestamps[i]:.5e}",
          f"{defbuffer2[i]:.5e}",
          f"{defbuffer1[i]:.5e}",
          sep="\t"
          )

inst.clear()
inst.close()

plotResults(timestamps, defbuffer2)