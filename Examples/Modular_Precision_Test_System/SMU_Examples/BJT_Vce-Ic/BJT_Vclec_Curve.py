#################################################################################
#
# Script File: BJT_Vclec_Curve.py
# 
#     ************************************************************************
#     *** Copyright Tektronix, Inc.                                        ***
#     *** See www.tek.com/sample-license for licensing terms.              ***
#     ************************************************************************
# 
# Description:
#     This script is example code, which creates (and subsequently calls) several
#     functions that can be used with the Model MP5000 Based SMUs to perform a
# 	  drain family of curve test for MOSFET devices. The purpose is show that 
# 	  you can perform the semiductor device characterization with the SMUs  
#       As written, two channels of SMU are assigned to the base/collector and the two
# 	  LOs from the two channels are tied together to the emitter. There are three different
# 	  scripts for the same test. One is operation in run time environment, the other
# 	  is single trigger model for both channels in the same slot. The third is another trigger
# 	  model example for each channel in different slot or in the same slot in the trigger
# 	  trigger model. 
# 	  Upon completion of each test, the data is printed to the TSP Toolkit Console 
# 	  in a format that is suitable for copying and pasting into Microsoft Excel for 
# 	  graphing and analysis.
# 
# Required Equipment: 1 Model MP5000 Mainframe 
# 					  2 channel SMUs 
# 					  1 BJT transistor
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
    pt.ylabel("Collector Current (A)")
    pt.xlabel("Collector Voltage (V)")
    pt.grid(True)
    pt.title("BJT Family of Curves")

    pt.show()

import pyvisa

# Configure Visa Connection
rm = pyvisa.ResourceManager()
inst = rm.open_resource('TCPIP0::192.168.0.2::5025::SOCKET')
# for using the sockets based implementation
inst.write_termination = "\n"
inst.read_termination = "\n"
inst.send_end = True
inst.timeout = 20000

# information of SMU
base_slot           = 1
collector_slot      = 1
common_slot 	    = 1
base_channel        = 1
collector_channel   = 2
# Collector Channel Settings
startVc		        = 0
stopVc		        = 2
noSwpPoints	        = 41
rangeIc		        = 250e-3
limitIc		        = 250e-3
# Base Channel Settings
startIb		        = 3.0e-3
stopIb		        = 10.0e-3
noStpPoints	        = 5
limitVb		        = 6
# Measure Settings for both channels
nplc			    = 1
mDelay		        = 0

tm_name1 = "tm_vcic"
tm_name2 = "tm_base"
tm_name3 = "tm_collector"

def OutputCurve_VceIc_TriggerInOneSlot():
    baseSMU = f"slot[{common_slot}].smu[{base_channel}]"
    collectorSMU = f"slot[{common_slot}].smu[{collector_channel}]"
    smu_id = [baseSMU, collectorSMU]
    # Configure both channel settings
    for i in range(2):
        inst.write(f"{smu_id[i]}.reset()")
        # Set base to perform current sweep
        if smu_id[i] == baseSMU:
            inst.write(f"{smu_id[i]}.source.func = {smu_id[i]}.FUNC_DC_CURRENT")
            inst.write(f"{smu_id[i]}.source.rangei = {max(abs(startIb), abs(stopIb))}")
            inst.write(f"{smu_id[i]}.source.limitv = {limitVb}")
        # Set collector to perform voltage sweep
        else:
            inst.write(f"{smu_id[i]}.source.func = {smu_id[i]}.FUNC_DC_VOLTAGE")
            inst.write(f"{smu_id[i]}.source.rangev = {max(abs(startVc), abs(stopVc))}")
            inst.write(f"{smu_id[i]}.source.limiti = {limitIc}")
            inst.write(f"{smu_id[i]}.measure.rangei = {rangeIc}")

        inst.write(f"{smu_id[i]}.sense = {smu_id[i]}.SENSE_2WIRE")
        inst.write(f"{smu_id[i]}.measure.nplc = {nplc}")

        inst.write(f"{smu_id[i]}.defbuffer1.clear()")
        inst.write(f"{smu_id[i]}.defbuffer1.appendmode = 1")
        inst.write(f"{smu_id[i]}.defbuffer2.clear()")
        inst.write(f"{smu_id[i]}.defbuffer2.appendmode = 1")
    # Configure voltage and current sweeps
    inst.write(f"{collectorSMU}.trigger.source.linearv({startVc}, {stopVc}, {noSwpPoints})")
    # Configure trigger model measurements to i/v and store in default buffers
    inst.write(f"{collectorSMU}.trigger.measure.iv({collectorSMU}.defbuffer1, {collectorSMU}.defbuffer2)")
    inst.write(f"{baseSMU}.trigger.source.lineari({startIb}, {stopIb}, {noStpPoints})")
    inst.write(f"{baseSMU}.trigger.measure.iv({baseSMU}.defbuffer1, {baseSMU}.defbuffer2)")

########################################################## Trigger model ###########################################################
####################################################################################################################################

    triggerModel = f"slot[{common_slot}].trigger.model"
    inst.write(f"{triggerModel}.create(\"{tm_name1}\")")
    # Advance base voltage to next value in sweep                                                                                                       ## Loop 2
    inst.write(f"{triggerModel}.addblock.source.action.step(\"{tm_name1}\", \"baseVoltage\", {base_channel})")                                              ##--##
    # Advance collector current to next value in sweep                                                                                      ## Loop 1       ##--##
    inst.write(f"{triggerModel}.addblock.source.action.step(\"{tm_name1}\", \"collectorVoltage\", {collector_channel})")                        ##--##      ##--##
    # Measure both channels i/v                                                                                                                 ##--##      ##--##
    inst.write(f"{triggerModel}.addblock.measure(\"{tm_name1}\", \"measure\", {base_channel}, 1)")                                              ##--##      ##--##
    inst.write(f"{triggerModel}.addblock.measure(\"{tm_name1}\", \"measure2\", {collector_channel}, 1)")                                        ##--##      ##--##
    # Loop back to advancing collector voltage                                                                                                  ##--##      ##--##
    inst.write(f"{triggerModel}.addblock.branch.counter(\"{tm_name1}\", \"branch-collector\", \"collectorVoltage\", {noSwpPoints})")         ##--##         ##--## 
    # Loop back to advancing base current                                                                                                                   ##--##
    inst.write(f"{triggerModel}.addblock.branch.counter(\"{tm_name1}\", \"branch-base\", \"baseVoltage\", {noStpPoints})")                               ##--##
    # Reset sources to 0
    inst.write(f"{triggerModel}.addblock.source.action.bias(\"{tm_name1}\", \"basebiaszeo\", {base_channel})")
    inst.write(f"{triggerModel}.addblock.source.action.bias(\"{tm_name1}\", \"collectorbiaszeo\", {collector_channel})")

####################################################################################################################################

    # Initiate trigger model, delete when completed
    inst.write(f"{baseSMU}.source.output = 1")
    inst.write(f"{collectorSMU}.source.output = 1")
 
    inst.write(f"{triggerModel}.initiate(\"{tm_name1}\")")
    inst.write("waitcomplete()")
 
    inst.write(f"{baseSMU}.source.output   = 0")
    inst.write(f"{collectorSMU}.source.output  = 0")
    inst.write(f"{triggerModel}.delete(\"{tm_name1}\")")

    # Fetch contents of buffer
    defBuffer1 = inst.query(f"printbuffer(1, {baseSMU}.defbuffer1.n, {baseSMU}.defbuffer1)").split(",")
    defBuffer1 = [float(x) for x in defBuffer1]
    defBuffer2 = inst.query(f"printbuffer(1, {baseSMU}.defbuffer2.n, {baseSMU}.defbuffer2)").split(",")
    defBuffer2 = [float(x) for x in defBuffer2]
    defBuffer3 = inst.query(f"printbuffer(1, {collectorSMU}.defbuffer1.n, {collectorSMU}.defbuffer1)").split(",")
    defBuffer3 = [float(x) for x in defBuffer3]
    defBuffer4 = inst.query(f"printbuffer(1, {collectorSMU}.defbuffer2.n, {collectorSMU}.defbuffer2)").split(",")
    defBuffer4 = [float(x) for x in defBuffer4]

    # Display results
    print("Vb","Ib","Vce","Ic",sep="\t\t")
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

def OutputCurve_VceIc_TwoTriggers():
    baseSMU = f"slot[{base_slot}].smu[{base_channel}]"
    collectorSMU = f"slot[{collector_slot}].smu[{collector_channel}]"
    smu_id = [baseSMU, collectorSMU]
    # Configure channel settings
    for i in range(2):
        inst.write(f"{smu_id[i]}.reset()")
        # Set base channel to perform current sweep
        if smu_id[i] == baseSMU:
            inst.write(f"{smu_id[i]}.source.func = {smu_id[i]}.FUNC_DC_CURRENT")
            inst.write(f"{smu_id[i]}.source.rangei = {max(abs(startIb), abs(stopIb))}")
            inst.write(f"{smu_id[i]}.source.limitv = {limitVb}")
        # Set collector channel to perform voltage sweep
        else:
            inst.write(f"{smu_id[i]}.source.func = {smu_id[i]}.FUNC_DC_VOLTAGE")
            inst.write(f"{smu_id[i]}.source.rangev = {max(abs(startVc), abs(stopVc))}")
            inst.write(f"{smu_id[i]}.source.limiti = {limitIc}")
            inst.write(f"{smu_id[i]}.measure.rangei = {rangeIc}")

        inst.write(f"{smu_id[i]}.sense = {smu_id[i]}.SENSE_2WIRE")
        inst.write(f"{smu_id[i]}.measure.nplc = {nplc}")

        inst.write(f"{smu_id[i]}.defbuffer1.clear()")
        inst.write(f"{smu_id[i]}.defbuffer1.appendmode = 1")
        inst.write(f"{smu_id[i]}.defbuffer2.clear()")
        inst.write(f"{smu_id[i]}.defbuffer2.appendmode = 1")
    
##################################################### Collector trigger model ######################################################
####################################################################################################################################

    # Configure trigger model for a linear voltage sweep
    inst.write(f"{collectorSMU}.trigger.source.linearv({startVc}, {stopVc}, {noSwpPoints})")
    # Set trigger model measurements to i/v and store in default buffers
    inst.write(f"{collectorSMU}.trigger.measure.iv({collectorSMU}.defbuffer1, {collectorSMU}.defbuffer2)")

    trigger_collector = f"slot[{collector_slot}].trigger.model"
    inst.write(f"{trigger_collector}.create(\"{tm_name3}\") ")

    # Notify base model that collector model has begun                                                                                                  ## Loop 2
    inst.write(f"{trigger_collector}.addblock.notify(\"{tm_name3}\",\"notifyStep\",slot[{collector_slot}].trigger.model.EVENT_NOTIFY1)")                    ##--##
                                                                                                                                                            ##--##
    # Wait for notification that base current has been advanced                                                                                             ##--##
    inst.write(f"{trigger_collector}.addblock.wait(\"{tm_name3}\",\"waitStep\",slot[{base_slot}].trigger.model.EVENT_NOTIFY2 )")                            ##--##
    # Advance voltage source value                                                                                                          ## Loop 1       ##--##
    inst.write(f"{trigger_collector}.addblock.source.action.step(\"{tm_name3}\",\"collectorSweep\",{collector_channel})")                       ##--##      ##--##
    # Notify vase that voltage sweep has been advanced                                                                                          ##--##      ##--##
    inst.write(f"{trigger_collector}.addblock.notify(\"{tm_name3}\",\"notifyMeasure\",slot[{collector_slot}].trigger.model.EVENT_NOTIFY3)")     ##--##      ##--##
    # Measure collector channel i/v                                                                                                             ##--##      ##--##
    inst.write(f"{trigger_collector}.addblock.measure(\"{tm_name3}\",\"measure\",{collector_channel}, 1)")                                      ##--##      ##--##
                                                                                                                                                ##--##      ##--##
    # Wait for notification from vase that measurement has been taken                                                                           ##--##      ##--##
    inst.write(f"{trigger_collector}.addblock.wait(\"{tm_name3}\",\"waitMeasure\",slot[{base_slot}].trigger.model.EVENT_NOTIFY4 )")             ##--##      ##--##
    # Loop back to advance voltage value                                                                                                        ##--##      ##--##
    inst.write(f"{trigger_collector}.addblock.branch.counter(\"{tm_name3}\",\"branch-sweep\",\"collectorSweep\",{noSwpPoints})")             ##--##         ##--##
    # Notify base that voltage sweep has completed                                                                                                          ##--##
    inst.write(f"{trigger_collector}.addblock.notify(\"{tm_name3}\",\"notifySweepDone\",slot[{collector_slot}].trigger.model.EVENT_NOTIFY5)")   	        ##--##
    # Loop back to notify base that sweep has begun                                                                                                         ##--##
    inst.write(f"{trigger_collector}.addblock.branch.counter(\"{tm_name3}\",\"branch-step\",\"notifyStep\",{noStpPoints})")                              ##--##
    inst.write(f"{trigger_collector}.addblock.source.action.bias(\"{tm_name3}\",\"collectorbiaszeo\",{collector_channel})")

####################################################### Base trigger model #########################################################
####################################################################################################################################

    # Configure trigger model for a linear current sweep
    inst.write(f"{baseSMU}.trigger.source.lineari({startIb}, {stopIb}, {noStpPoints})")
    # Set trigger model measurements i/v and store in default buffers
    inst.write(f"{baseSMU}.trigger.measure.iv({baseSMU}.defbuffer1,{baseSMU}.defbuffer2)")  

    
    trigger_base = f"slot[{base_slot}].trigger.model"
    inst.write(f"{trigger_base}.create(\"{tm_name2}\")") 

    # Wait for notification that collector model has started                                                                                         ## Loop 2
    inst.write(f"{trigger_base}.addblock.wait(\"{tm_name2}\",\"waitStep\",slot[{collector_slot}].trigger.model.EVENT_NOTIFY1 )")                         ##--##
    # Advance current source value                                                                                                                       ##--##
    inst.write(f"{trigger_base}.addblock.source.action.step(\"{tm_name2}\",\"baseVoltage\",{base_channel})")                                             ##--##
    # Notify collector that current has been advanced                                                                                                    ##--##
    inst.write(f"{trigger_base}.addblock.notify(\"{tm_name2}\",\"notify\",slot[{base_slot}].trigger.model.EVENT_NOTIFY2)")                               ##--##
                                                                                                                                                         ##--##
    # Wait for notification from collector that measurement has been taken                                                               ## Loop 1       ##--##
    inst.write(f"{trigger_base}.addblock.wait(\"{tm_name2}\",\"waitMeasure\",slot[{collector_slot}].trigger.model.EVENT_NOTIFY3 )")          ##--##      ##--##
    # Measure base channel i/v                                                                                                               ##--##      ##--##
    inst.write(f"{trigger_base}.addblock.measure(\"{tm_name2}\",\"measure\",{base_channel},1)")                                              ##--##      ##--##
    # Notify collector that measurement has been taken                                                                                       ##--##      ##--##
    inst.write(f"{trigger_base}.addblock.notify(\"{tm_name2}\",\"notify\",slot[{base_slot}].trigger.model.EVENT_NOTIFY4)")                   ##--##      ##--##
    # Loop back to wait for notification from collector                                                                                      ##--##      ##--##
    inst.write(f"{trigger_base}.addblock.branch.counter(\"{tm_name2}\",\"branch-Measure\",\"waitMeasure\",{noSwpPoints})")                ##--##         ##--##
                                                                                                                                                         ##--##
    # Wait for notification that collector voltage sweep has been completed                                                                              ##--##
    inst.write(f"{trigger_base}.addblock.wait(\"{tm_name2}\",\"waitSweepDone\",slot[{collector_slot}].trigger.model.EVENT_NOTIFY5 )")                    ##--##
    # Loop back to wait for notification from collector and advance current                                                                              ##--##
    inst.write(f"{trigger_base}.addblock.branch.counter(\"{tm_name2}\",\"branch-Step\",\"waitStep\",{noStpPoints})")                                  ##--##
    inst.write(f"{trigger_base}.addblock.source.action.bias(\"{tm_name2}\",\"gatebiaszero\",{base_channel})")

####################################################################################################################################

    # Initiate trigger models, delete when finished
    inst.write(f"{baseSMU}.source.output = 1")
    inst.write(f"{collectorSMU}.source.output = 1")
    inst.write(f"{trigger_base}.initiate(\"{tm_name2}\")")
    inst.write(f"{trigger_collector}.initiate(\"{tm_name3}\")")

    inst.write(f"waitcomplete()")

    inst.write(f"{baseSMU}.source.output = 0")
    inst.write(f"{collectorSMU}.source.output = 0")

    inst.write(f"{trigger_base}.delete(\"{tm_name2}\")")
    inst.write(f"{trigger_collector}.delete(\"{tm_name3}\")")

    # Fetch contents of buffer
    defBuffer1 = inst.query(f"printbuffer(1, {baseSMU}.defbuffer1.n, {baseSMU}.defbuffer1)").split(",")
    defBuffer1 = [float(x) for x in defBuffer1]
    defBuffer2 = inst.query(f"printbuffer(1, {baseSMU}.defbuffer2.n, {baseSMU}.defbuffer2)").split(",")
    defBuffer2 = [float(x) for x in defBuffer2]
    defBuffer3 = inst.query(f"printbuffer(1, {collectorSMU}.defbuffer1.n, {collectorSMU}.defbuffer1)").split(",")
    defBuffer3 = [float(x) for x in defBuffer3]
    defBuffer4 = inst.query(f"printbuffer(1, {collectorSMU}.defbuffer2.n, {collectorSMU}.defbuffer2)").split(",")
    defBuffer4 = [float(x) for x in defBuffer4]

    # Display results
    print("Vb","Ib","Vce","Ic",sep="\t\t")
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

OutputCurve_VceIc_TriggerInOneSlot()
#OutputCurve_VceIc_TwoTriggers()