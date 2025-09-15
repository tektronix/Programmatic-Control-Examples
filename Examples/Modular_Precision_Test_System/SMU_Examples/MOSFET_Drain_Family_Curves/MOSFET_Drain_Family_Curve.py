#################################################################################
#
# Script File: MOSFET_Drain_Family_Curve.tsp
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
#################################################################################

def plotResults(x, y, numPoints, numSeries):
    import matplotlib.pyplot as pt

    for i in range(numSeries):
        pt.plot(x[i*numPoints:i*numPoints+numPoints], y[i*numPoints:i*numPoints+numPoints], '-', color="blue")
    pt.ylabel("Drain Current (A)")
    pt.xlabel("Drain Voltage (V)")
    pt.grid(True)
    pt.title("MOSFET Family of Curves")

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
common_slot 	= 1
gate_channel    = 1
drain_channel   = 2
# Drain Channel Settings
startVd		    = 0
stopVd		    = 2
noSwpPoints	    = 41
rangeId		    = 100e-3
limitId		    = 100e-3
# Gate Channel Settings
startVg		    = 1.4
stopVg		    = 1.8
noStpPoints	    = 3
limitIg		    = 0.1
# Measure Settings for both channels
nplc            = 1
mDelay		    = 0

tm_name1 = "tm_vdid"
tm_name2 = "tm_gate"
tm_name3 = "tm_drain"

def DrainFamilyCurve_VdId_TriggerInOneSlot():
    gateSMU = f"slot[{common_slot}].smu[{gate_channel}]"
    drainSMU = f"slot[{common_slot}].smu[{drain_channel}]"
    smu_id = [gateSMU, drainSMU]
    # Configure both channels for a voltage sweep
    for i in smu_id:
        inst.write(f"{i}.reset()")
        inst.write(f"{i}.source.func = {i}.FUNC_DC_VOLTAGE")
        inst.write(f"{i}.sense = {i}.SENSE_2WIRE")

        if i == gateSMU:
            inst.write(f"{i}.source.rangev = {max(abs(startVg), abs(stopVg))}")
            inst.write(f"{i}.source.limiti = {limitIg}")
        else:
            inst.write(f"{i}.source.rangev = {max(abs(startVd), abs(stopVd))}")
            inst.write(f"{i}.source.limiti = {limitId}")
            inst.write(f"{i}.measure.rangei = {rangeId}")

        inst.write(f"{i}.source.levelv = 0")
        inst.write(f"{i}.measure.nplc = {nplc}")
        inst.write(f"{i}.defbuffer1.clear()")
        inst.write(f"{i}.defbuffer1.appendmode = 1")
        inst.write(f"{i}.defbuffer2.clear()")
        inst.write(f"{i}.defbuffer2.appendmode = 1")
    
    # Set both trigger model sources to a linear voltage sweep
    inst.write(f"{drainSMU}.trigger.source.linearv({startVd}, {stopVd}, {noSwpPoints})")
    # Set both trigger model measurements to i/v and store in default buffers
    inst.write(f"{drainSMU}.trigger.measure.iv({drainSMU}.defbuffer1, {drainSMU}.defbuffer2)")
    inst.write(f"{gateSMU}.trigger.source.linearv({startVg}, {stopVg}, {noStpPoints})")
    inst.write(f"{gateSMU}.trigger.measure.iv({gateSMU}.defbuffer1, {gateSMU}.defbuffer2)")

################################################ Trigger model #################################################
################################################################################################################

    triggerModel = f"slot[{common_slot}].trigger.model"
    inst.write(f"{triggerModel}.create(\"{tm_name1}\")")

    # Advance gate voltage to next value                                                                                                ## Loop 2
    inst.write(f"{triggerModel}.addblock.source.action.step(\"{tm_name1}\", \"gateVoltage\", {gate_channel})")                              ##--##
    # Advance drain voltage to next value                                                                                   ## Loop 1       ##--##
    inst.write(f"{triggerModel}.addblock.source.action.step(\"{tm_name1}\", \"drainVoltage\", {drain_channel})")                ##--##      ##--##
    # Measure i/v on both channels                                                                                              ##--##      ##--##
    inst.write(f"{triggerModel}.addblock.measure(\"{tm_name1}\", \"measure\", {gate_channel}, 1)")                              ##--##      ##--##
    inst.write(f"{triggerModel}.addblock.measure(\"{tm_name1}\", \"measure2\", {drain_channel}, 1)")                            ##--##      ##--##
    # Loop back to advance drain voltage                                                                                        ##--##      ##--##
    inst.write(f"{triggerModel}.addblock.branch.counter(\"{tm_name1}\", \"branch-drain\", \"drainVoltage\", {noSwpPoints})") ##--##         ##--##
    # Loop back to advance gate voltage                                                                                                     ##--##
    inst.write(f"{triggerModel}.addblock.branch.counter(\"{tm_name1}\", \"branch-gate\", \"gateVoltage\", {noStpPoints})")               ##--##
    # Set sources to 0
    inst.write(f"{triggerModel}.addblock.source.action.bias(\"{tm_name1}\", \"gatebiaszeo\", {gate_channel})")
    inst.write(f"{triggerModel}.addblock.source.action.bias(\"{tm_name1}\", \"drainbiaszeo\", {drain_channel})")

################################################################################################################

    # Initiate trigger model and delete when completed
    inst.write(f"{gateSMU}.source.output = 1")
    inst.write(f"{drainSMU}.source.output = 1")

    inst.write(f"{triggerModel}.initiate(\"{tm_name1}\")")
    inst.write(f"waitcomplete()")

    inst.write(f"{gateSMU}.source.output = 0")
    inst.write(f"{drainSMU}.source.output = 0")
    inst.write(f"{triggerModel}.delete(\"{tm_name1}\")")

    # Fetch buffer data
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
        
    inst.clear()
    inst.close()

    plotResults(defBuffer4, defBuffer3, noSwpPoints, noStpPoints)

def DrainFamilyCurve_VdId_TwoTriggers():
    gateSMU = f"slot[{gate_slot}].smu[{gate_channel}]"
    drainSMU = f"slot[{drain_slot}].smu[{drain_channel}]"
    smu_id = [gateSMU, drainSMU]
    # Configure both channels for a voltage sweep
    for i in smu_id:
        inst.write(f"{i}.reset()")
        inst.write(f"{i}.source.func = {i}.FUNC_DC_VOLTAGE")
        inst.write(f"{i}.sense = {i}.SENSE_2WIRE")

        if i == gateSMU:
            inst.write(f"{i}.source.rangev = {max(abs(startVg), abs(stopVg))}")
            inst.write(f"{i}.source.limiti = {limitIg}")
        else:
            inst.write(f"{i}.source.rangev = {max(abs(startVd), abs(stopVd))}")
            inst.write(f"{i}.source.limiti = {limitId}")
            inst.write(f"{i}.measure.rangei = {rangeId}")

        inst.write(f"{i}.source.levelv = 0")
        inst.write(f"{i}.measure.nplc = {nplc}")

        inst.write(f"{i}.defbuffer1.clear()")
        inst.write(f"{i}.defbuffer1.appendmode = 1")
        inst.write(f"{i}.defbuffer2.clear()")
        inst.write(f"{i}.defbuffer2.appendmode = 1")

############################################# Drain Trigger model ##############################################
################################################################################################################

    # Configure trigger model for linear voltage sweep
    inst.write(f"{drainSMU}.trigger.source.linearv({startVd}, {stopVd}, {noSwpPoints})")
    # Set trigger model measurements to i/v and store in default buffers
    inst.write(f"{drainSMU}.trigger.measure.iv({drainSMU}.defbuffer1, {drainSMU}.defbuffer2)")

    trigger_drain = f"slot[{drain_slot}].trigger.model"
    inst.write(f"{trigger_drain}.create(\"{tm_name3}\")")

    # Notify gate that sweep has began                                                                                                          ## Loop 2
    inst.write(f"{trigger_drain}.addblock.notify(\"{tm_name3}\",\"notifyStep\",slot[{drain_slot}].trigger.model.EVENT_NOTIFY1)	")                  ##--##
                                                                                                                                                    ##--##
    # Wait for notification from gate that gate voltage has advanced                                                                                ##--##
    inst.write(f"{trigger_drain}.addblock.wait(\"{tm_name3}\",\"waitStep\",slot[{gate_slot}].trigger.model.EVENT_NOTIFY2 )")                        ##--##
    # Advance drain source voltage                                                                                                  ## Loop 1       ##--##
    inst.write(f"{trigger_drain}.addblock.source.action.step(\"{tm_name3}\", \"drainSweep\", {drain_channel})")                         ##--##      ##--##
    # Notify gate that drain voltage has advanced                                                                                       ##--##      ##--##
    inst.write(f"{trigger_drain}.addblock.notify(\"{tm_name3}\",\"notifyMeasure\",slot[{drain_slot}].trigger.model.EVENT_NOTIFY3)")	    ##--##      ##--##
    # Measure drain i/v                                                                                                                 ##--##      ##--##
    inst.write(f"{trigger_drain}.addblock.measure(\"{tm_name3}\", \"measure\", {drain_channel}, 1)")                                    ##--##      ##--##
                                                                                                                                        ##--##      ##--##
    # Wait for notification that gate measurement has been taken                                                                        ##--##      ##--##
    inst.write(f"{trigger_drain}.addblock.wait(\"{tm_name3}\",\"waitMeasure\",slot[{gate_slot}].trigger.model.EVENT_NOTIFY4 )")         ##--##      ##--##
    # Loop back to advancing drain voltage                                                                                              ##--##      ##--##
    inst.write(f"{trigger_drain}.addblock.branch.counter(\"{tm_name3}\", \"branch-sweep\", \"drainSweep\", {noSwpPoints})")          ##--##         ##--##
    # Notify gate that drain voltage sweep has completed                                                                                            ##--##
    inst.write(f"{trigger_drain}.addblock.notify(\"{tm_name3}\",\"notifySweepDone\",slot[{drain_slot}].trigger.model.EVENT_NOTIFY5)")	            ##--##
    # Loop back to notify gate to begin sweep                                                                                                       ##--##
    inst.write(f"{trigger_drain}.addblock.branch.counter(\"{tm_name3}\", \"branch-step\", \"notifyStep\",  {noStpPoints})")                       ##--##
    inst.write(f"{trigger_drain}.addblock.source.action.bias(\"{tm_name3}\", \"drainbiaszeo\", {drain_channel})")

############################################## Gate Trigger model ##############################################
################################################################################################################

    inst.write(f"{gateSMU}.trigger.source.linearv({startVg}, {stopVg}, {noStpPoints})")
    inst.write(f"{gateSMU}.trigger.measure.iv({gateSMU}.defbuffer1, {gateSMU}.defbuffer2)")

    trigger_gate = f"slot[{gate_slot}].trigger.model"
    inst.write(f"{trigger_gate}.create(\"{tm_name2}\")")

    # Wait for notification from drain to begin                                                                                             ## Loop 2
    inst.write(f"{trigger_gate}.addblock.wait(\"{tm_name2}\",\"waitStep\",slot[{drain_slot}].trigger.model.EVENT_NOTIFY1 )")                    ##--##
    # Advance gate source voltage                                                                                                               ##--##
    inst.write(f"{trigger_gate}.addblock.source.action.step(\"{tm_name2}\", \"gateVoltage\", {gate_channel})")                                  ##--##
    # Notify drain that gate voltage has advanced                                                                                               ##--##
    inst.write(f"{trigger_gate}.addblock.notify(\"{tm_name2}\",\"notify\",slot[{gate_slot}].trigger.model.EVENT_NOTIFY2)")                      ##--##
                                                                                                                                                ##--##
    # Wait for notification that drain source voltage has advanced                                                              ## Loop 1       ##--##
    inst.write(f"{trigger_gate}.addblock.wait(\"{tm_name2}\",\"waitMeasure\",slot[{drain_slot}].trigger.model.EVENT_NOTIFY3 )")     ##--##      ##--##
    # Measure gate i/v                                                                                                              ##--##      ##--##
    inst.write(f"{trigger_gate}.addblock.measure(\"{tm_name2}\",\"measure\",{gate_channel}, 1)")                                    ##--##      ##--##
    # Notify drain that measurement has been taken                                                                                  ##--##      ##--##
    inst.write(f"{trigger_gate}.addblock.notify(\"{tm_name2}\",\"notify\",slot[{gate_slot}].trigger.model.EVENT_NOTIFY4)")          ##--##      ##--##
    # Loop back to wait for drain voltage to advance                                                                                ##--##      ##--##
    inst.write(f"{trigger_gate}.addblock.branch.counter(\"{tm_name2}\", \"branch-Measure\", \"waitMeasure\", {noSwpPoints})")    ##--##         ##--##  
                                                                                                                                                ##--##
    # Wait for notification that drain voltage sweep has completed                                                                              ##--##
    inst.write(f"{trigger_gate}.addblock.wait(\"{tm_name2}\",\"waitSweepDone\",slot[{drain_slot}].trigger.model.EVENT_NOTIFY5 )")               ##--##
    # Loop back to wait for drain to begin                                                                                                      ##--##
    inst.write(f"{trigger_gate}.addblock.branch.counter(\"{tm_name2}\", \"branch-Step\", \"waitStep\",  {noStpPoints})")                     ##--##
    inst.write(f"{trigger_gate}.addblock.source.action.bias(\"{tm_name2}\", \"gatebiaszero\", {gate_channel})")

################################################################################################################

    # Initiate trigger models and delete when completed
    inst.write(f"{gateSMU}.source.output = 1")
    inst.write(f"{drainSMU}.source.output = 1")
    inst.write(f"{trigger_gate}.initiate(\"{tm_name2}\")")
    inst.write(f"{trigger_drain}.initiate(\"{tm_name3}\")")

    inst.write("waitcomplete()")

    # Fetch buffer data
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
    
    inst.write(f"{trigger_drain}.delete(\"{tm_name3}\")")
    inst.write(f"{trigger_gate}.delete(\"{tm_name2}\")")

    inst.clear()
    inst.close()

    plotResults(defBuffer4, defBuffer3, noSwpPoints, noStpPoints)

DrainFamilyCurve_VdId_TriggerInOneSlot()
#DrainFamilyCurve_VdId_TwoTriggers()