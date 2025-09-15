################################################################################
# 
# Script File: MOSFET_Transfer_Curve.tsp
# 
#     ************************************************************************
#     *** Copyright Tektronix, Inc.                                        ***
#     *** See www.tek.com/sample-license for licensing terms.              ***
#     ************************************************************************
# 
# Description:
#     This script is example code, which creates (and subsequently calls) several
#     functions that can be used with the Model MP5000 Based SMUs to perform a
# 	  drain famility of curve test for MOSFET devices. The purpose is show that 
# 	  you can perform the semiductor device characterization with the SMUs  
#     As written, two channels of SMU are assigned to the gate, drain, and the two
# 	  LOs from the two channels are tied together to source.
# 	  Upon completion of each test, the data is printed to the TSP Toolkit Console 
# 	  in a format that is suitable for copying and pasting into Microsoft Excel for 
# 	  graphing and analysis.
# 
# Required Equipment: 1 Model MP5000 Mainframe 
# 					  2 channel SMUs 
# 					  1 MOSFET
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
################################################################################

def plotResults(x, y):
    import matplotlib.pyplot as pt

    pt.plot(x, y, '-', color="blue")
    pt.ylabel("Drain Current (A)")
    pt.xlabel("Gate Voltage (V)")
    pt.grid(True)
    pt.title("MOSFET Transfer Curve")

    pt.tight_layout()
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
gate_slot       = 1
drain_slot      = 1
common_slot     = 1
gate_channel    = 1
drain_channel   = 2
# Drain Channel Settings
Vd			    = 1
limitId		    = 0.1
# Gate Channel Settings
startVg		    = 0
stopVg		    = 2.2
noSwpPoints	    = 45
limitIg		    = 0.1
# Measure Settings for both channels
nplc			= 1
mDelay		    = 0

tm_name1 = "tm_vgid"
tm_name2 = "tm_gate"
tm_name3 = "tm_drain"

def TransferCurve_VgId_TriggerInOneSlot():
    gateSMU = f"slot[{common_slot}].smu[{gate_channel}]"
    drainSMU = f"slot[{common_slot}].smu[{drain_channel}]"
    smu_id = [gateSMU, drainSMU]
    # Configure both channels for a voltage output
    for i in smu_id:
        inst.write(f"{i}.reset()")
        inst.write(f"{i}.source.func = {i}.FUNC_DC_VOLTAGE")
        inst.write(f"{i}.sense = {i}.SENSE_2WIRE")
        if i == gateSMU:
            inst.write(f"{i}.source.rangev = {max(abs(startVg), abs(stopVg))}")
            inst.write(f"{i}.source.limiti = {limitIg}")
        else:
            inst.write(f"{i}.source.rangev = {Vd}")
            inst.write(f"{i}.measure.rangev = {Vd}")
            inst.write(f"{i}.source.limiti = {limitId}")

        inst.write(f"{i}.source.levelv = 0")
        inst.write(f"{i}.measure.nplc = {nplc}")
        inst.write(f"{i}.measure.autorangei = 1")

        inst.write(f"{i}.defbuffer1.clear()")
        inst.write(f"{i}.defbuffer1.appendmode = 1")
        inst.write(f"{i}.defbuffer2.clear()")
        inst.write(f"{i}.defbuffer2.appendmode = 1")

    # Set both trigger model sources to a linear voltage sweep
    inst.write(f"{drainSMU}.trigger.source.linearv({Vd}, {Vd}, 2)")
    # Set both trigger model measurements to i/v and store in default buffers
    inst.write(f"{gateSMU}.trigger.source.linearv({startVg}, {stopVg}, {noSwpPoints})")
    inst.write(f"{gateSMU}.trigger.measure.iv({gateSMU}.defbuffer1, {gateSMU}.defbuffer2)")
    inst.write(f"{drainSMU}.trigger.measure.iv({drainSMU}.defbuffer1, {drainSMU}.defbuffer2)")

################################################ Trigger model #################################################
################################################################################################################

    triggerModel = f"slot[{common_slot}].trigger.model"
    inst.write(f"{triggerModel}.create(\"{tm_name1}\")")

    # Advance drain voltage to next value                                                                                       ## Loop 1
    inst.write(f"{triggerModel}.addblock.source.action.step(\"{tm_name1}\", \"drainVoltage\", {drain_channel})")                    ##--##
    # Advance gate voltage to next value                                                                                            ##--##
    inst.write(f"{triggerModel}.addblock.source.action.step(\"{tm_name1}\", \"gateVoltage\", {gate_channel})")                      ##--##
    inst.write(f"{triggerModel}.addblock.delay.constant(\"{tm_name1}\",\"meaDelay\", {mDelay})")                                    ##--##
    # Measure i/v on both channels                                                                                                  ##--##
    inst.write(f"{triggerModel}.addblock.measure(\"{tm_name1}\", \"measure\", {gate_channel}, 1)")                                  ##--##
    inst.write(f"{triggerModel}.addblock.measure(\"{tm_name1}\", \"measure2\", {drain_channel}, 1)")                                ##--##
    # Loop through all sweep values                                                                                                 ##--##
    inst.write(f"{triggerModel}.addblock.branch.counter(\"{tm_name1}\", \"branch-counter\", \"gateVoltage\", {noSwpPoints})")    ##--##

################################################################################################################

    # Initiate trigger model, delete when finished
    inst.write(f"{gateSMU}.source.output = 1")
    inst.write(f"{drainSMU}.source.output = 1")

    inst.write(f"{triggerModel}.initiate(\"{tm_name1}\")")
    inst.write(f"waitcomplete()")

    # Retrieve buffer data
    defBuffer1 = inst.query(f"printbuffer(1, {gateSMU}.defbuffer1.n, {gateSMU}.defbuffer1)").split(",")
    defBuffer1 = [float(x) for x in defBuffer1]
    defBuffer2 = inst.query(f"printbuffer(1, {gateSMU}.defbuffer2.n, {gateSMU}.defbuffer2)").split(",")
    defBuffer2 = [float(x) for x in defBuffer2]
    defBuffer3 = inst.query(f"printbuffer(1, {drainSMU}.defbuffer1.n, {drainSMU}.defbuffer1)").split(",")
    defBuffer3 = [float(x) for x in defBuffer3]
    defBuffer4 = inst.query(f"printbuffer(1, {drainSMU}.defbuffer2.n, {drainSMU}.defbuffer2)").split(",")
    defBuffer4 = [float(x) for x in defBuffer4]

    # Display results
    print("Vg","Ig","Vd","Id", sep="\t\t")
    for i in range(len(defBuffer1)):
        print(f"{defBuffer2[i]:.5e}",
              f"{defBuffer1[i]:.5e}",
              f"{defBuffer4[i]:.5e}",
              f"{defBuffer3[i]:.5e}",
              sep="\t"
              )

    inst.write(f"{gateSMU}.source.output = 0")
    inst.write(f"{drainSMU}.source.output = 0")

    inst.write(f"{triggerModel}.delete(\"{tm_name1}\")")

    inst.clear()
    inst.close()

    plotResults(defBuffer2, defBuffer3)

def TransferCurve_VgId_TwoTriggers():
    gateSMU = f"slot[{gate_slot}].smu[{gate_channel}]"
    drainSMU = f"slot[{drain_slot}].smu[{drain_channel}]"
    smu_id = [gateSMU, drainSMU]

    for i in smu_id:
        inst.write(f"{i}.reset()")
        inst.write(f"{i}.source.func = {i}.FUNC_DC_VOLTAGE")
        inst.write(f"{i}.sense = {i}.SENSE_2WIRE")
        # Configure both channels for voltage output
        if i == gateSMU:
            inst.write(f"{i}.source.rangev = {max(abs(startVg), abs(stopVg))}")
            inst.write(f"{i}.source.limiti = {limitIg}")
        else:
            inst.write(f"{i}.source.rangev = {Vd}")
            inst.write(f"{i}.source.limiti = {limitId}")
        inst.write(f"{i}.source.levelv = 0")
        inst.write(f"{i}.measure.nplc = {nplc}")
        inst.write(f"{i}.measure.autorangei = 1")
        inst.write(f"{i}.defbuffer1.clear()")
        inst.write(f"{i}.defbuffer1.appendmode = 1")
        inst.write(f"{i}.defbuffer2.clear()")
        inst.write(f"{i}.defbuffer2.appendmode = 1")

############################################## Gate Trigger model ##############################################
################################################################################################################

    # Configure gate source for linear voltage sweep
    inst.write(f"{gateSMU}.trigger.source.linearv({startVg}, {stopVg}, {noSwpPoints})")
    # Set trigger model to measure i/v and store in default buffer
    inst.write(f"{gateSMU}.trigger.measure.iv({gateSMU}.defbuffer1, {gateSMU}.defbuffer2)")

    trigger_gate = f"slot[{gate_slot}].trigger.model"
    inst.write(f"{trigger_gate}.create(\"{tm_name2}\")")

    # Notify drain that sweep has began
    inst.write(f"{trigger_gate}.addblock.notify(\"{tm_name2}\",\"notifyDrainStep\",slot[{gate_slot}].trigger.model.EVENT_NOTIFY1)")

    # Wait for notification that drain source voltage has advanced
    inst.write(f"{trigger_gate}.addblock.wait(\"{tm_name2}\",\"waitDrainStep\",slot[{drain_slot}].trigger.model.EVENT_NOTIFY2)")
    # Advance gate voltage source level                                                                                     ## Loop 1
    inst.write(f"{trigger_gate}.addblock.source.action.step(\"{tm_name2}\",\"gateVoltage\",{gate_channel})")                    ##--##
    # Notify drain that source voltage has advanced                                                                             ##--##
    inst.write(f"{trigger_gate}.addblock.notify(\"{tm_name2}\",\"notify\",slot[{gate_slot}].trigger.model.EVENT_NOTIFY3)")      ##--##
    # Measure drain i/v                                                                                                         ##--##
    inst.write(f"{trigger_gate}.addblock.measure(\"{tm_name2}\",\"measure\",{gate_channel},1)")                                 ##--##
                                                                                                                                ##--##
    # Wait for measurement completed notification from drain                                                                    ##--##
    inst.write(f"{trigger_gate}.addblock.wait(\"{tm_name2}\",\"wait\",slot[{drain_slot}].trigger.model.EVENT_NOTIFY4)")         ##--##
    # Loop back to advance source voltage                                                                                       ##--##
    inst.write(f"{trigger_gate}.addblock.branch.counter(\"{tm_name2}\",\"branch-gate\",\"gateVoltage\",{noSwpPoints})")      ##--##
    # Notify drain that sweep has completed
    inst.write(f"{trigger_gate}.addblock.notify(\"{tm_name2}\",\"notifySweepDone\",slot[{gate_slot}].trigger.model.EVENT_NOTIFY5)")
    inst.write(f"{trigger_gate}.addblock.source.action.bias(\"{tm_name2}\",\"gatezero\",{gate_channel})")

############################################# Drain Trigger model ##############################################
################################################################################################################

    # Configure drain source to maintain constant voltage
    inst.write(f"{drainSMU}.trigger.source.linearv({Vd}, {Vd}, 1)")
    # Set trigger model to measure i/v and store in default buffers
    inst.write(f"{drainSMU}.trigger.measure.iv({drainSMU}.defbuffer1,{drainSMU}.defbuffer2)")

    trigger_drain = f"slot[{drain_slot}].trigger.model"
    inst.write(f"{trigger_drain}.create(\"{tm_name3}\")")

    # Wait for notification that sweep has begun
    inst.write(f"{trigger_drain}.addblock.wait(\"{tm_name3}\",\"waitStep\",slot[{gate_slot}].trigger.model.EVENT_NOTIFY1)")
    # Advance source voltage level
    inst.write(f"{trigger_drain}.addblock.source.action.step(\"{tm_name3}\",\"drainVoltage\",{drain_channel})")
    # Notify gate that source voltage has advanced
    inst.write(f"{trigger_drain}.addblock.notify(\"{tm_name3}\",\"notifyStep\",slot[{drain_slot}].trigger.model.EVENT_NOTIFY2)")
    
    # Wait for notificaiton that gate voltage source has advanced                                                               ## Loop 1
    inst.write(f"{trigger_drain}.addblock.wait(\"{tm_name3}\",\"waitMeas\",slot[{gate_slot}].trigger.model.EVENT_NOTIFY3)")         ##--##
    inst.write(f"{trigger_drain}.addblock.delay.constant(\"{tm_name3}\",\"meaDelay\",{mDelay})")                                    ##--##
    # Measure drain i/v                                                                                                             ##--##
    inst.write(f"{trigger_drain}.addblock.measure(\"{tm_name3}\",\"measure\",{drain_channel},1)")                                   ##--##
    # Notify gate that measurement has been taken                                                                                   ##--##
    inst.write(f"{trigger_drain}.addblock.notify(\"{tm_name3}\",\"notify\",slot[{drain_slot}].trigger.model.EVENT_NOTIFY4)")        ##--##
    # Loop back to wait block                                                                                                       ##--##
    inst.write(f"{trigger_drain}.addblock.branch.counter(\"{tm_name3}\",\"branch-drain\",\"waitMeas\",{noSwpPoints})")           ##--##
    
    # Wait for notificaiton that sweep has completed
    inst.write(f"{trigger_drain}.addblock.wait(\"{tm_name3}\",\"waitSweepDone\",slot[{gate_slot}].trigger.model.EVENT_NOTIFY5)")
    inst.write(f"{trigger_drain}.addblock.source.action.bias(\"{tm_name3}\",\"drainzero\",{drain_channel})")

################################################################################################################

    # Initiate trigger models, delete when completed
    inst.write(f"{gateSMU}.source.output = 1")
    inst.write(f"{drainSMU}.source.output = 1")

    inst.write(f"{trigger_drain}.initiate(\"{tm_name3}\")")
    inst.write(f"{trigger_gate}.initiate(\"{tm_name2}\")")
    inst.write("waitcomplete()")

    # Retrieve buffer data
    defBuffer1 = inst.query(f"printbuffer(1, {gateSMU}.defbuffer1.n, {gateSMU}.defbuffer1)").split(",")
    defBuffer1 = [float(x) for x in defBuffer1]
    defBuffer2 = inst.query(f"printbuffer(1, {gateSMU}.defbuffer2.n, {gateSMU}.defbuffer2)").split(",")
    defBuffer2 = [float(x) for x in defBuffer2]
    defBuffer3 = inst.query(f"printbuffer(1, {drainSMU}.defbuffer1.n, {drainSMU}.defbuffer1)").split(",")
    defBuffer3 = [float(x) for x in defBuffer3]
    defBuffer4 = inst.query(f"printbuffer(1, {drainSMU}.defbuffer2.n, {drainSMU}.defbuffer2)").split(",")
    defBuffer4 = [float(x) for x in defBuffer4]

    # Display results
    print("Vg","Ig","Vd","Id", sep="\t\t")
    for i in range(len(defBuffer1)):
        print(f"{defBuffer2[i]:.5e}",
              f"{defBuffer1[i]:.5e}",
              f"{defBuffer4[i]:.5e}",
              f"{defBuffer3[i]:.5e}",
              sep="\t"
              )

    inst.write(f"{gateSMU}.source.output = 0")
    inst.write(f"{drainSMU}.source.output = 0")

    inst.write(f"{trigger_gate}.delete(\"{tm_name2}\")")
    inst.write(f"{trigger_drain}.delete(\"{tm_name3}\")")

    inst.clear()
    inst.close()

    plotResults(defBuffer2, defBuffer3)

#TransferCurve_VgId_TriggerInOneSlot()
TransferCurve_VgId_TwoTriggers()