#################################################################################
#
# Script File: LED_Sequence.tsp
# 
#     ************************************************************************
#     *** Copyright Tektronix, Inc.                                        ***
#     *** See www.tek.com/sample-license for licensing terms.              ***
#     ************************************************************************
# 
# Description:
#     This script is example code, which creates (and subsequently calls) several
#     functions that can be used with the Model MP5000 Based SMUs to perform a
# 	  current sweeping. The purpose is show that you can perform a LED device
# 	  with the SMU. As written, one channel of SMU is assigned to the anode for 
# 	  the high and cathode for the low terminal. This script shows the benefit of
# 	  configlist feature. All the attributes of source and measurement are configured
# 	  in configlist prior to the trigger. Then trigger recalls the configlist and run.
# 	  This feature gives a lot of convience and speed in LED sequence test. 
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

import pyvisa

# Configure Visa Connection
rm = pyvisa.ResourceManager()
inst = rm.open_resource('TCPIP0::192.168.0.2::5025::SOCKET')
# for using the sockets based implementation
inst.write_termination = "\n"
inst.read_termination = "\n"
inst.send_end = True
inst.timeout = 10000

IF_slot = 1
IF_Channel = 1
smu = f"slot[{IF_slot}].smu[{IF_Channel}]"
triggerModel = f"slot[{IF_slot}].trigger.model"

triggerName = "tm_led"
configName = "cl_led"

# test_items stores the various settings to create a config list
test_items = [
# Mode,  srcBias,   srcRng,   mDelay,    mTime,     Limit,     mRng
    [0, 0.000001,  0.00001,     0.01,    0.001, 	    1,        6],
    [0,  0.00001,   0.0001,    0.005,    0.001,   		3,        6],
    [0,  	0.35,        1,    0.001,    0.001,	        5,        6],
    [1,   	  -7,       20,    0.005,    0.001,   0.00005,    0.001],
    [0, 0.000001,  0.00001,    0.003,    0.001, 	    1,        6],
    [0,    0.350,        1,    0.003,    0.001,        10,       20],
    [0, 0.000001,  0.00001,    0.003,    0.001, 	    1,        6],
    [1, 	 -40,       60,     0.01,   0.0001,    0.0005,     0.01],
    [1, 	 -20,       20,     0.01,   0.0001,    0.0005,     0.01],
    [0,  0.00001,   0.0001,    0.003,    0.001, 	    3,        6],
    [0,    0.030,        1,    0.003,    0.001,   	   10,       20],
    [0,  0.00001,   0.0001,    0.003,    0.001, 	    3,        6],
    [1,      -24,       60,    0.005,   0.0001,     0.005,    0.001],
    [1,       -7,       20,    0.005,   0.0001,     0.005,    0.001],
    [0, 0.000001,  0.00001,     0.01,    0.001, 	    1,        6],
    [0,  0.00001,   0.0001,    0.005,    0.001,   		3,        6],
    [0,   	0.35,        1,    0.001,    0.001,	        5,        6],
    [1,        7,       20,    0.005,   0.0001,     0.005,    0.001]
]

# Initialize SMU
def initSMU():
    inst.write(f"{smu}.reset()")
    inst.write(f"{smu}.source.func = {smu}.OUTPUT_DCVOLTS")
    inst.write(f"{smu}.source.rangev = 20")
    inst.write(f"{smu}.source.levelv = 0")
    inst.write(f"{smu}.source.limiti = 1e-6")

    inst.write(f"{smu}.measure.rangei = 1e-6")
    inst.write(f"{smu}.measure.rangev = 20")
    inst.write(f"{smu}.measure.aperture = 5e-3")
    inst.write(f"{smu}.defbuffer1.clear()")
    inst.write(f"{smu}.defbuffer2.clear()")

# Create a configlist from the table
def setConfigList():
    # Create configlist
    inst.write(f"{smu}.configlist.create(\"{configName}\")")
    for i in range(len(test_items)):
        seqTable = test_items[i]
        # Setup SMU with settings from table
        if seqTable[0] == 0:
            inst.write(f"{smu}.source.func = {smu}.FUNC_DC_CURRENT")
            inst.write(f"{smu}.source.rangei = {seqTable[2]}")
            inst.write(f"{smu}.source.leveli = {seqTable[1]}")
            inst.write(f"{smu}.source.limitv = {seqTable[5]}")

            inst.write(f"{smu}.measure.rangev = {seqTable[6]}")
            inst.write(f"{smu}.measure.rangei = {seqTable[2]}")
            inst.write(f"{smu}.measure.delay = {seqTable[3]}")
            inst.write(f"{smu}.measure.aperture = {seqTable[4]}")
        elif seqTable[0] == 1:
            inst.write(f"{smu}.source.func = {smu}.OUTPUT_DCVOLTS")
            inst.write(f"{smu}.source.rangev = {seqTable[2]}")
            inst.write(f"{smu}.source.levelv = {seqTable[1]}")
            inst.write(f"{smu}.source.limiti = {seqTable[5]}")

            inst.write(f"{smu}.measure.rangev = {seqTable[2]}")
            inst.write(f"{smu}.measure.rangei = {seqTable[6]}")
            inst.write(f"{smu}.measure.delay = {seqTable[3]}")
            inst.write(f"{smu}.measure.aperture = {seqTable[4]}")
        # Store the current settings in configlist at index i
        inst.write(f"{smu}.configlist.store(\"{configName}\", {i+1})")

# Create and initialize trigger model
def setTriggerModel():
    inst.write(f"{smu}.trigger.measure.iv({smu}.defbuffer1, {smu}.defbuffer2)")
    inst.write(f"{triggerModel}.create(\"{triggerName}\")")
    # Set SMU settings to next item in configlist
    inst.write(f"{triggerModel}.addblock.configlist.next(\"{triggerName}\", \"recallBlockName\", {IF_Channel}, \"{configName}\")")
    # Take i/v measurements
    inst.write(f"{triggerModel}.addblock.measure(\"{triggerName}\", \"measBlockname\", {IF_Channel}, 1)")
    # Loop through all items in configlist
    inst.write(f"{triggerModel}.addblock.branch.counter(\"{triggerName}\", \"branch-counter\", \"recallBlockName\", {len(test_items)})")

# Execute test
setConfigList()
setTriggerModel()
initSMU()

inst.write(f"{smu}.source.levelv = 0")
inst.write(f"{smu}.source.output = 1")

inst.write(f"{triggerModel}.initiate(\"{triggerName}\")")
inst.write(f"waitcomplete()")

print("Test Done")
inst.write(f"{smu}.source.output = 0")

inst.write(f"{triggerModel}.delete(\"{triggerName}\")")
inst.write(f"{smu}.configlist.delete(\"{configName}\")")

# Restieve buffer data
defBuffer1 = inst.query(f"printbuffer(1, {smu}.defbuffer1.n, {smu}.defbuffer1)")
defBuffer1 = defBuffer1.split(",")
defBuffer2 = inst.query(f"printbuffer(1, {smu}.defbuffer2.n, {smu}.defbuffer2)")
defBuffer2 = defBuffer2.split(",")

# Display results
print("Current","Voltage",sep="\t")
for i in range(len(defBuffer1)):
    print(defBuffer1[i].lstrip(),
          defBuffer2[i].lstrip(),
          sep="\t"
          )

inst.clear()
inst.close()