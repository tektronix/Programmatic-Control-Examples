#################################################################################
#
# Script File: Res_Volt_Pulse_Sweep.py
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
# 	  This pulse test should be excuted in trigger model. the first script shows
# 	  how much accurate the delay constance with reference makes pulse. 
# 	  The second script shows how to make pulse with trigger timer object. 
# 	  Upon completion of each test, the data is printed to the TSP Toolkit Console 
# 	  in a format that is suitable for copying and pasting into Microsoft Excel for 
# 	  graphing and analysis.
# 
# Required Equipment: 1 Model MP5000 Mainframe 
# 					  1 channel SMU 
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
# Functions created by this script:
#     * DC_Voltage_Sweep_Resistor_RunTimeEnv({slot_no,smu_channel},,{startV,stopV,noPoints,limitI},{measRangeV, measRangeI, autoRangeI, nplc,mDelay,remoteSense},tm_name)
#     * DC_Voltage_Sweep_Resistor_inTriggerModel({slot_no,smu_channel},,{startV,stopV,noPoints,limitI},{measRangeV, measRangeI, autoRangeI, nplc,mDelay,remoteSense},tm_name)
#
#################################################################################

def plotResults(x, y):
    import matplotlib.pyplot as pt
    pt.plot(x, y, 'o')
    pt.ylim(-30000, 70000)
    pt.xlabel("Supplied Voltage (V)")
    pt.ylabel("Measured Resistance (Ω)")
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
noPoints 		= 101
limitI 		    = 1
# Measure Settings
measRangeV  	= 6
measRangeI      = 1
remoteSense 	= False
# Pulse Settings
pulsePeriod	    = 5e-3  # pulsePeriod should be longer than pulseWidth + mDelay + apertureTime
pulseWidth	    = 3e-3
mDelay 		    = 1e-3
apertureTime	= 1e-3

tm_name 		= "TM_sweepV_pulse"

smu = f"slot[{slot_no}].smu[{sweepV_channel}]"
inst.write(f"{smu}.reset()")

def Pulse_Voltage_Sweep_Resistor_inDelayConstant():
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

    inst.write(f"{smu}.trigger.source.linearv({startV}, {stopV}, {noPoints})")
    inst.write(f"{smu}.trigger.measure.iv({smu}.defbuffer1, {smu}.defbuffer2)")

    # Configure trigger model
    triggerModel = f"slot[{slot_no}].trigger.model"
    inst.write(f"{triggerModel}.create(\"{tm_name}\")")
    inst.write(f"{triggerModel}.addblock.source.action.step(\"{tm_name}\", \"sweepV_IV\", {sweepV_channel})")
    inst.write(f"{triggerModel}.addblock.delay.constant(\"{tm_name}\", \"meas_delay\", {mDelay})")
    inst.write(f"{triggerModel}.addblock.measure(\"{tm_name}\", \"measure_IV\", {sweepV_channel}, 1)")
    inst.write(f"{triggerModel}.addblock.delay.constant(\"{tm_name}\", \"meas_pulse_width\", {pulseWidth}, \"sweepV_IV\")")
    inst.write(f"{triggerModel}.addblock.source.action.bias(\"{tm_name}\", \"pulse_bias\", {sweepV_channel})")
    inst.write(f"{triggerModel}.addblock.delay.constant(\"{tm_name}\", \"meas_pulse_period\", {pulsePeriod}, \"sweepV_IV\")")
    inst.write(f"{triggerModel}.addblock.branch.counter(\"{tm_name}\", \"branch-counter\", \"sweepV_IV\", {noPoints})")

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
    resists = [x/y for x, y in zip(defbuffer2, defbuffer1)]

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

def Pulse_Voltage_Sweep_Resistor_inTriggerTimer():
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

    # Pulse period timer settings
    pulse_period = "trigger.timer[1]"
    inst.write(f"{pulse_period}.delay = {pulsePeriod}")
    # Passthrough allows for script to continue running
    inst.write(f"{pulse_period}.passthrough = true")
    inst.write(f"{pulse_period}.count = {noPoints}")
    inst.write(f"{pulse_period}.stimulus= trigger.generator[1].EVENT_ID")
    # Measure delay timer settings
    mdelay_on_pulse = "trigger.timer[2]"
    inst.write(f"{mdelay_on_pulse}.delay = {mDelay}")
    inst.write(f"{mdelay_on_pulse}.passthrough = false")
    inst.write(f"{mdelay_on_pulse}.count = 1")
    inst.write(f"{mdelay_on_pulse}.stimulus = {pulse_period}.EVENT_ID")
    # Pulse width timer settings
    pulse_width = "trigger.timer[3]"
    inst.write(f"{pulse_width}.delay = {pulseWidth}")
    inst.write(f"{pulse_width}.passthrough = false")
    inst.write(f"{pulse_width}.count = 1")
    inst.write(f"{pulse_width}.stimulus = {pulse_period}.EVENT_ID")

    # Setup trigger model source for linear voltage sweep
    inst.write(f"{smu}.trigger.source.linearv({startV}, {stopV}, {noPoints})")
    # Setup measurements to store in default buffers and measure current/voltage
    inst.write(f"{smu}.trigger.measure.iv({smu}.defbuffer1, {smu}.defbuffer2)")

    # Configure trigger model 
    triggerModel = f"slot[{slot_no}].trigger.model"
    inst.write(f"{triggerModel}.create(\"{tm_name}\")") 
    # Wait for event from pulse period timer
    inst.write(f"{triggerModel}.addblock.wait(\"{tm_name}\", \"wait_period\", {pulse_period}.EVENT_ID)")
    # Advance to next source level in sweep
    inst.write(f"{triggerModel}.addblock.source.action.step(\"{tm_name}\", \"sweepV_IV\", {sweepV_channel})")
    # Wait for event from mdelay
    inst.write(f"{triggerModel}.addblock.wait(\"{tm_name}\", \"wait_mdelay\", {mdelay_on_pulse}.EVENT_ID)")
    # Measure current/voltage
    inst.write(f"{triggerModel}.addblock.measure(\"{tm_name}\", \"measure_IV\", {sweepV_channel}, 1)")
    # Wait for event from pulse_width
    inst.write(f"{triggerModel}.addblock.wait(\"{tm_name}\", \"wait_width\", {pulse_width}.EVENT_ID)")
    inst.write(f"{triggerModel}.addblock.source.action.bias(\"{tm_name}\", \"pulse_bias\", {sweepV_channel})")
    # Loop through all voltage values in sweep
    inst.write(f"{triggerModel}.addblock.branch.counter(\"{tm_name}\", \"branch-counter\", \"sweepV_IV\", {noPoints})")

    # Initiate trigger model, delete when completed
    inst.write(f"{smu}.source.output = 1")
    inst.write(f"{triggerModel}.initiate(\"{tm_name}\")")
    inst.write(f"trigger.generator[1].assert()")
    inst.write(f"waitcomplete()")
    inst.write(f"{smu}.source.output = 0")
    inst.write(f"{triggerModel}.delete(\"{tm_name}\")")

    # Retrieve defbuffers
    defbuffer1 = inst.query(f"printbuffer(1, {smu}.defbuffer1.n, {smu}.defbuffer1)").split(",")
    defbuffer1 = [float(x) for x in defbuffer1]
    defbuffer2 = inst.query(f"printbuffer(1, {smu}.defbuffer2.n, {smu}.defbuffer2)").split(",")
    defbuffer2 = [float(x) for x in defbuffer2]
    resists = [x/y for x, y in zip(defbuffer2, defbuffer1)]

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

#Pulse_Voltage_Sweep_Resistor_inDelayConstant()
Pulse_Voltage_Sweep_Resistor_inTriggerTimer()