#################################################################################
#
# Script File: Laser_VSCEL.py
# 
#     ************************************************************************
#     *** Copyright Tektronix, Inc.                                        ***
#     *** See www.tek.com/sample-license for licensing terms.              ***
#     ************************************************************************
# 
# Description:
#     This script is example code, which creates (and subsequently calls) several
#     functions that can be used with the Model MP5000 Based SMUs to perform a
#     current sweeping. The purpose is show that you can perform a laser/VCLSE device
#     characterization with the SMUs. As written, one channel of SMU is assigned to 
#     the anode for the high and cathode for the low terminal. the high of the other SMU
#     is assigned to the high of a PD anode and the low is to cathod. One channels performs
#     current sweeping on the laser/or VCSEL measuring voltage and current. The other channel
#     keeps a constanst voltage bias measurement current of the PD device. This test provides
#     three different scripts. One is DC sweep measurement in run time environment. The second
#     is still DC test tested in trigger model. The third is a pulse test in trigger model. 
#     This feature gives a lot of convience and speed in LED sequence test. 
#     Upon completion of each test, the data is printed to the TSP Toolkit Console 
#     in a format that is suitable for copying and pasting into Microsoft Excel for 
#     graphing and analysis.
# 
# Required Equipment: 1 Model MP5000 Mainframe 
# 					  2 channel SMU 
# 					  1 Laser/VSCEL unit
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

def plotResults(x, y1, y2):
    import matplotlib.pyplot as pt

    fig, ax1 = pt.subplots()

    ax1.plot(x, y1, '-', color="tab:blue")
    ax1.set_xlabel("IF (A)")
    ax1.set_ylabel("VF (V)", color="tab:blue")
    ax1.tick_params(axis='y', labelcolor="tab:blue")
    
    ax2 = ax1.twinx()

    ax2.plot(x, y2, '-', color="tab:red")
    ax2.set_ylabel("I_PD (A)", color="tab:red")
    ax2.tick_params(axis='y', labelcolor="tab:red")

    fig.suptitle("L-I_V Test")
    fig.tight_layout()
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
IF_slot 		= 1
IF_channel  	= 1
PD_slot 		= 1
PD_channel 	    = 2

# IF Settings
startIF 		= 0
stopIF 		    = 100e-3
noPoints 		= 60
rangeI 		    = 1000e-3
limitV 		    = 6
measRangeV	    = 6

# PD Source Measure Settings
biasV_PD 		= 0
srcRangeV_PD 	= 6
measRangeI_PD   = 10e-3
# Mesaure Settings
nplc 			= 1
mDelay 		    = 1e-3
remoteSense 	= False

# Pulse Settings
pulsePeriod	    = 5e-3  # pulsePeriod should be longer than pulseWidth + mDelay + apertureTime
pulseWidth	    = 3e-3
apertureTime	= 1e-3

# Trigger model names
tm_name1 = "tm_if"
tm_name2 = "tm_pd"

IF_smu = f"slot[{IF_slot}].smu[{IF_channel}]"
PD_smu = f"slot[{PD_slot}].smu[{PD_channel}]"
smu_id = [IF_smu, PD_smu]

def Pulse_Laser_VCSEL_LIV_inTriggerModel():
    for i in smu_id:
        inst.write(f"{i}.reset()")

        # Buffer clear
        inst.write(f"{i}.defbuffer1.clear()")
        inst.write(f"{i}.defbuffer1.appendmode = 1")
        inst.write(f"{i}.defbuffer2.clear()")
        inst.write(f"{i}.defbuffer2.appendmode = 1")

        if i == IF_smu:
            # Source settings
            inst.write(f"{i}.source.func = {i}.FUNC_DC_CURRENT")
            inst.write(f"{i}.source.rangei = {rangeI}")
            inst.write(f"{i}.source.leveli = 0")
            inst.write(f"{i}.source.limitv = {limitV}")
            # Measure settings
            inst.write(f"{i}.measure.rangev = {measRangeV}")
            inst.write(f"{i}.measure.rangei = {rangeI}")
        else:
            # Source settings
            inst.write(f"{i}.source.func = {i}.FUNC_DC_VOLTAGE")
            inst.write(f"{i}.source.rangev = {srcRangeV_PD}")
            inst.write(f"{i}.source.levelv = {biasV_PD}")
            # Measure settings
            inst.write(f"{i}.measure.rangei = {measRangeI_PD}")
        
        inst.write(f"{i}.measure.aperture = {apertureTime}")

        if remoteSense:
            inst.write(f"{i}.sense = {i}.SENSE_4WIRE")
        else:
            inst.write(f"{i}.sense = {i}.SENSE_2WIRE")
        
################################################# Source channel trigger model #################################################
################################################################################################################################

    inst.write(f"{IF_smu}.trigger.source.lineari({startIF}, {stopIF}, {noPoints})")
    inst.write(f"{IF_smu}.trigger.measure.iv({IF_smu}.defbuffer1, {IF_smu}.defbuffer2)")
    
    # Configure trigger model
    trigger_IF = f"slot[{IF_slot}].trigger.model"
    inst.write(f"{trigger_IF}.create(\"{tm_name1}\")")

    # Notify PD trigger model to begin
    inst.write(f"{trigger_IF}.addblock.notify(\"{tm_name1}\", \"notifyPDStep\", slot[{IF_slot}].trigger.model.EVENT_NOTIFY1)")

    # Wait for PD channel to advance to next source value
    inst.write(f"{trigger_IF}.addblock.wait(\"{tm_name1}\", \"waitPDStep\", slot[{PD_slot}].trigger.model.EVENT_NOTIFY2)")
    # Advance to next current value in sweep                                                                                # Loop 1
    inst.write(f"{trigger_IF}.addblock.source.action.step(\"{tm_name1}\", \"IF_sweep\", {IF_channel})")                         ##--##
    inst.write(f"{trigger_IF}.addblock.delay.constant(\"{tm_name1}\", \"meaDelay\", {mDelay}, \"IF_sweep\")")                   ##--##
    # Notify PD trigger model that current value has advanced                                                                   ##--##
    inst.write(f"{trigger_IF}.addblock.notify(\"{tm_name1}\", \"notify\", slot[{IF_slot}].trigger.model.EVENT_NOTIFY3)")        ##--##
    # Measure source channel i/v                                                                                                ##--##
    inst.write(f"{trigger_IF}.addblock.measure(\"{tm_name1}\", \"measure\", {IF_channel}, 1)")                                  ##--##
                                                                                                                                ##--##
    # Wait for notification that PD channel has been measured                                                                   ##--##
    inst.write(f"{trigger_IF}.addblock.wait(\"{tm_name1}\", \"wait\", slot[{PD_slot}].trigger.model.EVENT_NOTIFY4)")            ##--##
    inst.write(f"{trigger_IF}.addblock.delay.constant(\"{tm_name1}\", \"pulse_width\", {pulseWidth}, \"IF_sweep\")")            ##--##
    # Set source value back to 0                                                                                                ##--##
    inst.write(f"{trigger_IF}.addblock.source.action.bias(\"{tm_name1}\", \"IF_off\", {IF_channel})")                           ##--##
    inst.write(f"{trigger_IF}.addblock.delay.constant(\"{tm_name1}\", \"pulse_period\", {pulsePeriod}, \"IF_sweep\")")          ##--##
    # Loop back to advance source current                                                                                       ##--##
    inst.write(f"{trigger_IF}.addblock.branch.counter(\"{tm_name1}\", \"IF_branch\", \"IF_sweep\", {noPoints})")             ##--##
    # Notify PD channel that sweep has completed
    inst.write(f"{trigger_IF}.addblock.notify(\"{tm_name1}\", \"notifySweepDone\", slot[{IF_slot}].trigger.model.EVENT_NOTIFY5)")
    inst.write(f"{trigger_IF}.addblock.source.action.bias(\"{tm_name1}\", \"IF_bias\", {IF_channel})")

################################################### PD channel trigger model ###################################################
################################################################################################################################

    inst.write(f"{PD_smu}.trigger.source.linearv({biasV_PD}, {biasV_PD}, 1)")
    inst.write(f"{PD_smu}.trigger.measure.iv({PD_smu}.defbuffer1, {PD_smu}.defbuffer2)")

    trigger_PD = f"slot[{PD_slot}].trigger.model"
    inst.write(f"{trigger_PD}.create(\"{tm_name2}\")")

    # Wait for source trigger model to begin
    inst.write(f"{trigger_PD}.addblock.wait(\"{tm_name2}\", \"waitStep\", slot[{IF_slot}].trigger.model.EVENT_NOTIFY1)")
    # Advance to next source value in sweep
    inst.write(f"{trigger_PD}.addblock.source.action.step(\"{tm_name2}\", \"bias_PD\", {PD_channel})")
    # Notify source that voltage value has been advanced
    inst.write(f"{trigger_PD}.addblock.notify(\"{tm_name2}\", \"notifyStep\", slot[{PD_slot}].trigger.model.EVENT_NOTIFY2)")

    # Wait for source trigger model to advance source current                                                               # Loop 1
    inst.write(f"{trigger_PD}.addblock.wait(\"{tm_name2}\", \"waitMeas\", slot[{IF_slot}].trigger.model.EVENT_NOTIFY3)")        ##--##
    # Measure i/v on PD channel                                                                                                 ##--##
    inst.write(f"{trigger_PD}.addblock.measure(\"{tm_name2}\", \"measure\", {PD_channel}, 1)")                                  ##--##
    # Notify source trigger model that measurement has been completed                                                           ##--##
    inst.write(f"{trigger_PD}.addblock.notify(\"{tm_name2}\", \"notify\", slot[{PD_slot}].trigger.model.EVENT_NOTIFY4)")        ##--##
    # Loop back to wait for notification from source trigger model                                                              ##--##
    inst.write(f"{trigger_PD}.addblock.branch.counter(\"{tm_name2}\", \"branch-PD\", \"waitMeas\", {noPoints})")             ##--##
                                                                                                                                
    # Wait for nootification from source that the sweep has been completed
    inst.write(f"{trigger_PD}.addblock.wait(\"{tm_name2}\", \"waitPDDone\", slot[{IF_slot}].trigger.model.EVENT_NOTIFY5)")
    inst.write(f"{trigger_PD}.addblock.source.action.bias(\"{tm_name2}\", \"PDzero\", {PD_channel})")
    
################################################################################################################################

    # Initiate trigger models, delete when completed
    inst.write(f"{IF_smu}.source.output = 1")
    inst.write(f"{PD_smu}.source.output = 1")
    inst.write(f"{PD_smu}.source.levelv = {biasV_PD}")

    inst.write(f"{trigger_PD}.initiate(\"{tm_name2}\")")
    inst.write(f"{trigger_IF}.initiate(\"{tm_name1}\")")

    inst.write("waitcomplete()")

    inst.write(f"{IF_smu}.source.output = 0")
    inst.write(f"{PD_smu}.source.output = 0")

    inst.write(f"{trigger_PD}.delete(\"{tm_name1}\")")
    inst.write(f"{trigger_IF}.delete(\"{tm_name2}\")")

    # Retrieve buffer data
    defBuffer1 = inst.query(f"printbuffer(1, {IF_smu}.defbuffer1.n, {IF_smu}.defbuffer1)").split(",")
    defBuffer1 = [float(x) for x in defBuffer1]
    defBuffer2 = inst.query(f"printbuffer(1, {IF_smu}.defbuffer2.n, {IF_smu}.defbuffer2)").split(",")
    defBuffer2 = [float(x) for x in defBuffer2]
    defBuffer3 = inst.query(f"printbuffer(1, {PD_smu}.defbuffer1.n, {PD_smu}.defbuffer1)").split(",")
    defBuffer3 = [float(x) for x in defBuffer3]
    defBuffer4 = inst.query(f"printbuffer(1, {PD_smu}.defbuffer2.n, {PD_smu}.defbuffer2)").split(",")
    defBuffer4 = [float(x) for x in defBuffer4]

    # Display results
    print("IF","VF","I_PD","V_PD",sep="\t\t")
    for i in range(len(defBuffer1)):
        print(f"{defBuffer1[i]:.5e}", 
              f"{defBuffer2[i]:.5e}", 
              f"{defBuffer3[i]:.5e}", 
              f"{defBuffer4[i]:.5e}", 
              sep="\t"
            )
    inst.clear()
    inst.close()
    plotResults(defBuffer1, defBuffer2, [-1 * x for x in defBuffer3])
    
    
Pulse_Laser_VCSEL_LIV_inTriggerModel()