#################################################################################
# 
# Script File: Parallel_SMU_Combo.py
# 
#     ************************************************************************
#     *** Copyright Tektronix, Inc.                                        ***
#     *** See www.tek.com/sample-license for licensing terms.              ***
#     ************************************************************************
# 
# Description:
#     This script is example code, which creates (and subsequently calls) several
#     functions that can be used with the Model MP5000 Based SMUs to perform a
# 	  voltage sweeping. The purpose is show that you can perform voltage sweeping
#     with two channel SMU combination in parallel to increase current. Each SMU
# 	  assigned to one terminal for the high and the other for the low terminal.	
# 	  Upon completion of each test, the data is printed to the TSP Toolkit Console 
# 	  in a format that is suitable for copying and pasting into Microsoft Excel for 
# 	  graphing and analysis.
# 
# Required Equipment: 1 Model MP5000 Mainframe 
# 					  2 channel SMU (MSMU Series)
#                     1 Resistive load
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

    pt.plot(x, y, 'o-', color="blue")
    
    pt.ylabel("Measured Current (A)")
    pt.xlabel("Supplied Voltage (V)")
    pt.grid(True)
    pt.title("Parallel Voltage Sweep")

    pt.tight_layout()
    pt.show()

import pyvisa
import time

# Configure Visa Connection
rm = pyvisa.ResourceManager()
inst = rm.open_resource('TCPIP0::192.168.0.2::5025::SOCKET')
# for using the sockets based implementation
inst.write_termination = "\n"
inst.read_termination = "\n"
inst.send_end = True
inst.timeout = 10000

# Source Settings
startV 		= 0
stopV 		= 10
noPoints    = 6
limitI 		= 0.2       # total current for all channels
# Measure Settings
measRangeV 	= 12     
measRangeI	= 100e-3  # same range setting for each range
autoRangeI 	= True
nplc 		= 1
mDelay 		= 0
remoteSense = False

# No more than two channels should be combined
infoSMU = [
    f"slot[1].smu[1]",
    f"slot[1].smu[2]"
]

for i in infoSMU:
    # Reset each channel
    inst.write(f"{i}.reset()")
    inst.write(f"{i}.defbuffer1.clear()")
    inst.write(f"{i}.defbuffer1.appendmode = 1")
    inst.write(f"{i}.defbuffer2.clear()")
    inst.write(f"{i}.defbuffer2.appendmode = 1")
    # Source Settings
    inst.write(f"{i}.source.func = {i}.FUNC_DC_VOLTAGE")
    inst.write(f"{i}.source.rangev = {max(abs(startV), abs(stopV))}")
    inst.write(f"{i}.source.limiti = {limitI / len(infoSMU)}")       # Divide current limit among channels
    inst.write(f"{i}.source.levelv = 0")
    # Measure Settings
    inst.write(f"{i}.measure.rangev = {measRangeV}")
    inst.write(f"{i}.measure.nplc = {nplc}")
    if autoRangeI:
        inst.write(f"{i}.measure.autorangei = 1")
    else:
        inst.write(f"{i}.measure.autorangei = 0")
        inst.write(f"{i}.measure.rangei = {measRangeI}")
    if remoteSense:
        inst.write(f"{i}.sense = {i}.SENSE_4WIRE")
    else:
        inst.write(f"{i}.sense = {i}.SENSE_2WIRE")
    inst.write(f"{i}.source.output = 1")

print("I_total","V",sep="\t\t")
# Calculate change in voltage for each iteration
deltaV = (stopV - startV) / (noPoints - 1)

for j in range(noPoints):
    # Set source voltage for each channel
    for i in infoSMU:
        inst.write(f"{i}.source.levelv = {startV + (j * deltaV)}")   
    time.sleep(mDelay)
    # Measire i/v on each channel and store in default buffers
    for i in infoSMU:
        inst.write(f"{i}.measure.iv({i}.defbuffer1, {i}.defbuffer2)")

currentReadings = [0.0] * noPoints
voltageReadings = [0.0] * noPoints

# Retrieve data from buffers
for i in infoSMU:
    inst.write(f"{i}.source.output = 0")
    defBuffer1 = inst.query(f"printbuffer(1, {i}.defbuffer1.n, {i}.defbuffer1)").split(",")
    defBuffer2 = inst.query(f"printbuffer(1, {i}.defbuffer2.n, {i}.defbuffer2)").split(",")
    # Sum currents and voltages
    currentReadings = [x + float(y) for x, y in zip(currentReadings, defBuffer1)]
    voltageReadings = [x + float(y) for x, y in zip(voltageReadings, defBuffer2)]
# Divide voltage among currents
voltageReadings = [i/len(infoSMU) for i in voltageReadings]
# Display results
for i in range(noPoints):
    print(f"{currentReadings[i]:.5e}",
          f"{voltageReadings[i]:.5e}",
          sep="\t")

inst.clear()
inst.close()

plotResults(voltageReadings, currentReadings)