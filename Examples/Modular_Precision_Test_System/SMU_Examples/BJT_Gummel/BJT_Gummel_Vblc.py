#################################################################################
#
# Script File: BJT_Gummel_Vblc.py
# 
#     ************************************************************************
#     *** Copyright Tektronix, Inc.                                        ***
#     *** See www.tek.com/sample-license for licensing terms.              ***
#     ************************************************************************
# 
# Description:
#     This script is example code, which creates (and subsequently calls) several
#     functions that can be used with the Model MP5000 Based SMUs to perform a
# 	  gummel curve test for n-type bipolar junction transitor devices. 
# 	  The purpose is show that you can perform the semiductor device gummel characterization 
# 	  with the SMUs As written, two channels of SMU are assigned to the collector/base. 
# 	  LOs from the two channels are tied together to emitter. There are three different
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
# 					  1 BJT Transistor
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

    pt.plot(x, y1, color="blue")
    pt.plot(x, y2, color="orange")

    pt.ylabel("Current (A)")
    pt.xlabel("Base Voltage (V)")
    pt.xlim(.05, max(x))

    pt.grid(True)
    pt.title("BJT Gummel Plot")
    pt.yscale('log')

    pt.show()

import pyvisa

# Configure Visa Connection
rm = pyvisa.ResourceManager()
inst = rm.open_resource('TCPIP0::192.168.0.2::5025::SOCKET')
# For using the sockets based implementation
inst.write_termination = "\n"
inst.read_termination = "\n"
inst.send_end = True
inst.timeout = 10000

# Information of SMU
base_slot           = 1
collector_slot       = 1
common_slot 	    = 1
base_channel        = 1
collector_channel   = 2

# Base & Collector Channel Settings
startVbVc		    = 0
stopVbVc		    = 1
noSwpPoints	        = 41
limitIbIc		    = 500e-3
# Measure Settings for both channels
nplc			    = 1
mDelay		        = 0

tm_name1 = "tm_vbic"
tm_name2 = "tm_base"
tm_name3 = "tm_collector"

def Gummel_VbIc_TriggerInOneSlot():
    baseSMU = f"slot[{common_slot}].smu[{base_channel}]"
    collectorSMU = f"slot[{common_slot}].smu[{collector_channel}]"
    smu_id = [baseSMU, collectorSMU]
    # Configure both channels for a voltage sweep
    for i in smu_id:
        inst.write(f"{i}.reset()")
        inst.write(f"{i}.source.func = {i}.FUNC_DC_VOLTAGE")
        inst.write(f"{i}.sense = {i}.SENSE_2WIRE")
        inst.write(f"{i}.source.rangev = {max(abs(startVbVc), abs(stopVbVc))}")
        inst.write(f"{i}.source.limiti = {limitIbIc}")
        inst.write(f"{i}.source.levelv = 0")
        inst.write(f"{i}.measure.nplc = {nplc}")
        inst.write(f"{i}.measure.autorangei = 1")
        inst.write(f"{i}.defbuffer1.clear()")
        inst.write(f"{i}.defbuffer1.appendmode = 1")
        inst.write(f"{i}.defbuffer2.clear()")
        inst.write(f"{i}.defbuffer2.appendmode = 1")

    # Setup linear voltage sweep for both channels
    inst.write(f"{collectorSMU}.trigger.source.linearv({startVbVc}, {stopVbVc}, {noSwpPoints})")
    inst.write(f"{baseSMU}.trigger.source.linearv({startVbVc}, {stopVbVc}, {noSwpPoints})")
    # Set trigger models to measure i/v and store in default buffers
    inst.write(f"{baseSMU}.trigger.measure.iv({baseSMU}.defbuffer1, {baseSMU}.defbuffer2)")
    inst.write(f"{collectorSMU}.trigger.measure.iv({collectorSMU}.defbuffer1, {collectorSMU}.defbuffer2)")
    
########################################################### Trigger model ############################################################
######################################################################################################################################

    triggerModel = f"slot[{common_slot}].trigger.model"
    inst.write(f"{triggerModel}.create(\"{tm_name1}\")")

    # Advance both channels to the next volatge value                                                                               ## Loop 1
    inst.write(f"{triggerModel}.addblock.source.action.step(\"{tm_name1}\", \"collectorVoltage\", {collector_channel})")                ##--##
    inst.write(f"{triggerModel}.addblock.source.action.step(\"{tm_name1}\", \"baseVoltage\", {base_channel})")                          ##--##
    inst.write(f"{triggerModel}.addblock.delay.constant(\"{tm_name1}\", \"meaDelay\", {mDelay})")                                       ##--##
    # Measure i/v                                                                                                                       ##--##
    inst.write(f"{triggerModel}.addblock.measure(\"{tm_name1}\", \"measure\",  {base_channel}, 1)")                                     ##--##
    inst.write(f"{triggerModel}.addblock.measure(\"{tm_name1}\", \"measure2\", {collector_channel}, 1)")                                ##--##
    # Loop for every value in volgate sweeps                                                                                            ##--##
    inst.write(f"{triggerModel}.addblock.branch.counter(\"{tm_name1}\", \"branch-counter\", \"collectorVoltage\", {noSwpPoints})")   ##--##

######################################################################################################################################
    
    # Initate trigger model, delete when finished
    inst.write(f"{baseSMU}.source.output = 1")
    inst.write(f"{collectorSMU}.source.output = 1")
    inst.write(f"{triggerModel}.initiate(\"{tm_name1}\")")
    inst.write("waitcomplete()")
    inst.write(f"{baseSMU}.source.output = 0")
    inst.write(f"{collectorSMU}.source.output = 0")
    inst.write(f"{triggerModel}.delete(\"{tm_name1}\")")
    
    # Fetch data from buffers
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

    plotResults(defBuffer2, defBuffer1, defBuffer3)
    
def Gummel_VbIc_TwoTriggers():
    baseSMU = f"slot[{base_slot}].smu[{base_channel}]"
    collectorSMU = f"slot[{collector_slot}].smu[{collector_channel}]"
    smu_id = [baseSMU, collectorSMU]
    # Configure both channels for a voltage sweep
    for i in smu_id:
        inst.write(f"{i}.reset()")
        inst.write(f"{i}.source.func = {i}.FUNC_DC_VOLTAGE")
        inst.write(f"{i}.sense = {i}.SENSE_2WIRE")
        inst.write(f"{i}.source.rangev = {max(abs(startVbVc), abs(stopVbVc))}")
        inst.write(f"{i}.source.limiti = {limitIbIc}")
        inst.write(f"{i}.source.levelv = 0")
        inst.write(f"{i}.measure.nplc = {nplc}")
        inst.write(f"{i}.measure.autorangei = 1")
        inst.write(f"{i}.defbuffer1.clear()")
        inst.write(f"{i}.defbuffer1.appendmode = 1")
        inst.write(f"{i}.defbuffer2.clear()")
        inst.write(f"{i}.defbuffer2.appendmode = 1")

######################################################### Base trigger model #########################################################
######################################################################################################################################

    # Set source values for linear voltage sweep
    inst.write(f"{baseSMU}.trigger.source.linearv({startVbVc}, {stopVbVc}, {noSwpPoints})")
    # Set trigger model measurements to i/v and store in default buffers
    inst.write(f"{baseSMU}.trigger.measure.iv({baseSMU}.defbuffer1, {baseSMU}.defbuffer2)")

    trigger_base = f"slot[{base_slot}].trigger.model"
    inst.write(f"{trigger_base}.create(\"{tm_name2}\")")

    # Notify collector model that sweep has begun                                                                                       ## Loop 1
    inst.write(f"{trigger_base}.addblock.notify(\"{tm_name2}\",\"notifyCollectorStep\",slot[{base_slot}].trigger.model.EVENT_NOTIFY1)")     ##--##
    # Advance source to next voltage value                                                                                                  ##--##
    inst.write(f"{trigger_base}.addblock.source.action.step(\"{tm_name2}\",\"baseVoltage\",{base_channel})")                                ##--##
    inst.write(f"{trigger_base}.addblock.delay.constant(\"{tm_name2}\",\"meaDelay\",{mDelay})")                                             ##--##
    # Measure i/v on base                                                                                                                   ##--##
    inst.write(f"{trigger_base}.addblock.measure(\"{tm_name2}\",\"measure\",{base_channel},1)")                                             ##--##
                                                                                                                                            ##--##
    # Wait for notification that collector model finished measurement                                                                       ##--##
    inst.write(f"{trigger_base}.addblock.wait(\"{tm_name2}\",\"waitCollectorStep\",slot[{collector_slot}].trigger.model.EVENT_NOTIFY2)")    ##--##
    # Loop to notify collecto model of next iteration                                                                                       ##--##
    inst.write(f"{trigger_base}.addblock.branch.counter(\"{tm_name2}\",\"branch-gate\",\"notifyCollectorStep\",{noSwpPoints})")          ##--##
    # Notify collector model that voltage sweep has completed
    inst.write(f"{trigger_base}.addblock.notify(\"{tm_name2}\",\"notifySweepDone\",slot[{base_slot}].trigger.model.EVENT_NOTIFY3)")
    inst.write(f"{trigger_base}.addblock.source.action.bias(\"{tm_name2}\",\"basezero\",{base_channel})")

####################################################### Collector trigger model ######################################################
######################################################################################################################################

    # Set source values for linear voltage sweep
    inst.write(f"{collectorSMU}.trigger.source.linearv({startVbVc}, {stopVbVc}, {noSwpPoints})")
    # Set trigger model measurements to i/v and store in default buffers
    inst.write(f"{collectorSMU}.trigger.measure.iv({collectorSMU}.defbuffer1, {collectorSMU}.defbuffer2)")

    trigger_collector = f"slot[{collector_slot}].trigger.model"
    inst.write(f"{trigger_collector}.create(\"{tm_name3}\")")

    # Wait for notification from base to begin sweep                                                                                    ## Loop 1
    inst.write(f"{trigger_collector}.addblock.wait(\"{tm_name3}\",\"waitStep\",slot[{base_slot}].trigger.model.EVENT_NOTIFY1)")             ##--##
    # Advance source to next voltage value                                                                                                  ##--##
    inst.write(f"{trigger_collector}.addblock.source.action.step(\"{tm_name3}\",\"collectorVoltage\",{collector_channel})")                 ##--##
    inst.write(f"{trigger_collector}.addblock.delay.constant(\"{tm_name3}\",\"meaDelay\",{mDelay})")                                        ##--##
    # Measure i/v on collector                                                                                                              ##--##
    inst.write(f"{trigger_collector}.addblock.measure(\"{tm_name3}\",\"measure\",{collector_channel},1)")                                   ##--##
    # Notify vase model that measurement has been completed                                                                                 ##--##
    inst.write(f"{trigger_collector}.addblock.notify(\"{tm_name3}\",\"notifyStep\",slot[{collector_slot}].trigger.model.EVENT_NOTIFY2)")    ##--##
    # Loop to wait for base notification                                                                                                    ##--##
    inst.write(f"{trigger_collector}.addblock.branch.counter(\"{tm_name3}\",\"branch-drain\",\"waitStep\",{noSwpPoints})")               ##--##
    
    # Wait for notification that sweep has been completed
    inst.write(f"{trigger_collector}.addblock.wait(\"{tm_name3}\",\"waitSweepDone\",slot[{base_slot}].trigger.model.EVENT_NOTIFY3)")
    inst.write(f"{trigger_collector}.addblock.source.action.bias(\"{tm_name3}\",\"collectorzero\",{collector_channel})")

######################################################################################################################################

    # Initiate trigger models, delete when completed
    inst.write(f"{baseSMU}.source.output = 1")
    inst.write(f"{collectorSMU}.source.output = 1")
    inst.write(f"{trigger_collector}.initiate(\"{tm_name3}\")")
    inst.write(f"{trigger_base}.initiate(\"{tm_name2}\")")
    inst.write("waitcomplete()")
    inst.write(f"{baseSMU}.source.output = 0")
    inst.write(f"{collectorSMU}.source.output = 0")
    inst.write(f"{trigger_base}.delete(\"{tm_name2}\")")
    inst.write(f"{trigger_collector}.delete(\"{tm_name3}\")")

    # Fetch data from buffers
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

    plotResults(defBuffer2, defBuffer1, defBuffer3)

Gummel_VbIc_TriggerInOneSlot()
#Gummel_VbIc_TwoTriggers()

