#################################################################################
#
# Script File: Sinewave_Generation.py
# 
#     ************************************************************************
#     *** Copyright Tektronix, Inc.                                        ***
#     *** See www.tek.com/sample-license for licensing terms.              ***
#     ************************************************************************
# 
# Description:
#     This script is example code, which creates (and subsequently calls) several
#     functions that can be used with the Model MP5000 Based SMUs to perform a
# 	  current sweeping. The purpose is show that you can make a sine waveform in output
# 	  As written, one channel of SMU is assigned to the high and the other to the low 
# 	  terminal. The script shows fast changing source bias to be enough to make a sine. 
# 	  For the same purpose, SMU support it in run time evironment and in trigger model.
# 	  Upon completion of each test, the data is printed to the TSP Toolkit Console 
# 	  in a format that is suitable for copying and pasting into Microsoft Excel for 
# 	  graphing and analysis.
# 
# Required Equipment: 1 Model MP5000 Mainframe 
# 					  1 channel SMU (MSMU Series)
# 					  1 Resistor
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
    pt.title("Sine Generation")
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

# information of SMU
slot_no 		= 1
smu_channel 	= 1
# AC input parameters
Vrms            = 5
numCycles       = 3
frequency       = 60
limitI          = .100

tm_name 		= "tm_sine"

smu = f"slot[{slot_no}].smu[{smu_channel}]"
inst.write(f"{smu}.reset()")
# Calculate sinewave values
Vpp             = Vrms * math.sqrt(2)
pointsPerCycle  = 7200 / frequency
timeInterval    = 1 / 7200
numDataPoints   = pointsPerCycle * numCycles
sourceValues    = [None] * int(numDataPoints)
# Generate voltage sweep values
inst.write("sourceValues = {}")
for i in range(int(numDataPoints)):
    inst.write(f"sourceValues[{i+1}] = {(Vpp * math.sin((i+1) * 2 * math.pi / pointsPerCycle))}")
# Create reading buffers
numReadings     = 280 * numCycles
inst.write(f"readingBuffer1 = {smu}.makebuffer(5000)")
inst.write(f"readingBuffer2 = {smu}.makebuffer(5000)")

# Configure channel settings
inst.write(f"{smu}.source.func = {smu}.FUNC_DC_VOLTAGE")
inst.write(f"{smu}.source.autorangev = {smu}.OFF")
inst.write(f"{smu}.source.rangev = 20")
inst.write(f"{smu}.source.limiti = {limitI}")
inst.write(f"{smu}.source.levelv = 0")
inst.write(f"{smu}.source.output = 1")
inst.write(f"{smu}.measure.aperture = .0001")
inst.write(f"{smu}.measure.rangei = .100")
inst.write(f"{smu}.measure.rangev = 20")

# Configure sweep voltage list
inst.write(f"{smu}.trigger.source.listv(sourceValues)")
# Set trigger model readings for i/v and store in reading buffers
inst.write(f"{smu}.trigger.measure.iv(readingBuffer1, readingBuffer2)")

# Configure trigger model
triggerModel = f"slot[{slot_no}].trigger.model"
inst.write(f"{triggerModel}.create(\"{tm_name}\")")
# Measure overlapped allows for readings to hapen while triggermodel is executing in parallel
inst.write(f"{triggerModel}.addblock.measureoverlapped(\"{tm_name}\", \"measure3\", {smu_channel}, {numReadings})")
inst.write(f"{triggerModel}.addblock.delay.constant(\"{tm_name}\", \"delay-init\", .002)")
# Advance through voltage sweep
inst.write(f"{triggerModel}.addblock.source.action.step(\"{tm_name}\", \"sweep_step1\", {smu_channel})")
inst.write(f"{triggerModel}.addblock.delay.constant(\"{tm_name}\", \"delay-on2\", {timeInterval}, \"sweep_step1\")")
# Loop through all voltage values
inst.write(f"{triggerModel}.addblock.branch.counter(\"{tm_name}\", \"branch-counter7\", \"sweep_step1\", {numDataPoints})")

# Execute trigger model and delete when finished
inst.write(f"{smu}.source.output = 1")
inst.write(f"{triggerModel}.initiate(\"{tm_name}\")")
inst.write(f"waitcomplete()")
inst.write(f"{smu}.source.output = 0")
inst.write(f"{triggerModel}.delete(\"{tm_name}\")")

# Retrieve buffer data
timestamps = inst.query(f"printbuffer(1, readingBuffer1.n, readingBuffer1.timestamps)").split(", ")
timestamps = [float(x) for x in timestamps]
readingBuffer1 = inst.query(f"printbuffer(1, readingBuffer1.n, readingBuffer1)").split(", ")
readingBuffer1 = [float(x) for x in readingBuffer1]
readingBuffer2 = inst.query(f"printbuffer(1, readingBuffer2.n, readingBuffer2)").split(", ")
readingBuffer2 = [float(x) for x in readingBuffer2]

# Display data
print("Time","V","I",sep="\t\t")
for i in range(len(readingBuffer1)):
    print(f"{timestamps[i]:.5e}",
          f"{readingBuffer2[i]:.5e}",
          f"{readingBuffer1[i]:.5e}",
          sep="\t"
          )

inst.clear()
inst.close()

plotResults(timestamps, readingBuffer2)