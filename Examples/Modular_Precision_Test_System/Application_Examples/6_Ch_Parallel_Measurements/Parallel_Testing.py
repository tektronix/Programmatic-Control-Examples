# Used to connect to the instrument
import pyvisa as visa
# Used for arrays
import numpy as np
# Used for frontend
import tkinter as tk 
from tkinter import *
from tkinter import ttk 
# Used for simple delays
from time import sleep
# Used for plotting/displaying results
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk) 

rm = visa.ResourceManager() 

#########################################################################################
#   Function:   check_SMU()
#   Purpose:    This function allows the user to check their instrument connection. A
#               resource string is entered by the user and queried to ensure a working
#               working connection.
#########################################################################################
def check_SMU():
    # Empty displayed text
    string_idn.config(text = ' ')
    # Retrieve resource string
    resource_string = ip_entry.get()
    # Attempt to open the instrument, query the idn, and display the results
    try:
        myMP5000 = rm.open_resource(resource_string, read_termination = '\n')
        myMP5000.timeout = 20000
        myMP5000.write("*IDN?")
        read = myMP5000.read()
        print(read)
        remove_term = read.replace('\n','')
        string_idn.config(text = remove_term)
        myMP5000.write("localnode.prompts = 0 \n")
        myMP5000.close()
    # If error occurs notify the user
    except:
        string_idn.config(text = "Error in opening instrument, check resource string")

    # Clear all figures and draw to screen
    fig1.clf()
    fig2.clf()
    fig3.clf()
    fig4.clf()
    canvas1.draw() 
    canvas2.draw() 
    canvas3.draw() 
    canvas4.draw() 

#########################################################################################
#   Function:   load_script()
#   Purpose:    This function loads multiple functions to execute the various tests for
#               each channel. These tests can be configured and run by the user from the
#               screen.
#########################################################################################
def load_script():
    # Open the instrument
    string_idn.config(text = ' ')
    resource_string = ip_entry.get()
    myMP5000 = rm.open_resource(resource_string, read_termination = '\n')
    myMP5000.timeout = 20000
    # Create a command buffer to later write to the instrument
    tsp_command  = ["loadscript CombinedTestScripts", 
                    ####################################################################################################################
                    #   Function:   configure_DrainFamilyCurve_VdId_TwoTriggers(infoSMU,dSMUsettings, gSMUsettings, meaSettings,tmName)
                    #   Parameters: infoSMU         A list containing the SMU slot/module locations
                    #                               {gate_slot, drain_slot, gate_channel, drain_channel}
                    #               dSMUsettings    A list containing the drain configuration settings
                    #                               {startVd, stopVd, noSwpPoints, rangeId, limitId}
                    #               gSMUsettings    A list containing the gate configuration settings
                    #                               {startVg, stopVg, noStpPoints, limitIg}
                    #               meaSettings     A list containing the measure configuration settings
                    #                               {nplc, mDelay}
                    #               tmName          A string to name the trigger model
                    #
                    #   Purpose:    This function performs VdId characterization on a MOSFET. It returns the results to be graphed to 
                    #               the screen.
                    ####################################################################################################################
                    "function configure_DrainFamilyCurve_VdId_TwoTriggers(infoSMU,dSMUsettings, gSMUsettings, meaSettings,tmName)",
                    #   SMU channel assignment
                    "	local gateSMU      							= slot[infoSMU[1]].smu[infoSMU[2]]",
                    "	local drainSMU     							= slot[infoSMU[3]].smu[infoSMU[4]]",
                    "	local smu_id								= {gateSMU,drainSMU}",
                    #   Configure both channels for a voltage sweep
                    "	for i = 1, 2 do	",
                    "		smu_id[i].reset()",
                    "		smu_id[i].source.func					= smu_id[i].FUNC_DC_VOLTAGE",
                    "		smu_id[i].sense							= smu_id[i].SENSE_2WIRE	",
                    "		if smu_id[i] == gateSMU then",
                    "			smu_id[i].source.rangev				= math.max(math.abs(gSMUsettings[1]), math.abs(gSMUsettings[2]))",
                    "			smu_id[i].source.limiti				= gSMUsettings[4]",
                    "			smu_id[i].measure.rangei			= 1e-3",
                    "		else",
                    "			smu_id[i].source.rangev				= math.max(math.abs(dSMUsettings[1]), math.abs(dSMUsettings[2]))",
                    "			smu_id[i].source.limiti				= dSMUsettings[5]",
                    "			smu_id[i].measure.rangei			= dSMUsettings[4]",
                    "		end	",
                    "		smu_id[i].source.levelv 				= 0",
                    "		smu_id[i].measure.nplc					= meaSettings[1]",

                    "		smu_id[i].defbuffer1.clear()",
                    "		smu_id[i].defbuffer1.appendmode			= 1",
                    "		smu_id[i].defbuffer2.clear()",
                    "		smu_id[i].defbuffer2.appendmode			= 1",
                    "	end",

                    ############################################# Drain Trigger Model ##############################################
                    ################################################################################################################
                    
                    #   Configure trigger model source for linear voltage sweep
                    "	drainSMU.trigger.source.linearv(dSMUsettings[1], dSMUsettings[2], dSMUsettings[3])",
                    #   Set trigger model measurements to i/v and store in default buffers
                    "	drainSMU.trigger.measure.iv(drainSMU.defbuffer1,drainSMU.defbuffer2)",

                    "	local trigger_drain = slot[infoSMU[3]].trigger.model",
                    "	trigger_drain.create(tmName[2])",

                    #   Wait for notification to begin test
                    "	trigger_drain.addblock.wait(tmName[2],\"Wait1\",trigger.generator[1].EVENT_ID)",
                    
                    #   Notify gate that sweep has began
                    "	trigger_drain.addblock.notify(tmName[2],\"notifyStep\",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY1)",

                    #   Wait for notification from gate  that fate voltage has advanced
                    "	trigger_drain.addblock.wait(tmName[2],\"waitStep\",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY2 )",
                    #   Advance drain source voltage
                    "	trigger_drain.addblock.source.action.step(tmName[2], \"drainSweep\", infoSMU[4])",
                    #   Notify gate that drain voltage has advanced
                    "	trigger_drain.addblock.notify(tmName[2],\"notifyMeasure\",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY3)",
                    #   Measure drain i/v
                    "	trigger_drain.addblock.measure(tmName[2], \"measure\", infoSMU[4], 1)",

                    #   Wait for notification that gate measurement has been taken
                    "	trigger_drain.addblock.wait(tmName[2],\"waitMeasure\",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY4 )",
                    #   Loop back to advancing drain voltage
                    "	trigger_drain.addblock.branch.counter(tmName[2], \"branch-sweep\", \"drainSweep\", dSMUsettings[3])",
                    #   Notify gate that drain voltage sweep has completed
                    "	trigger_drain.addblock.notify(tmName[2],\"notifySweepDone\",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY5)",
                    #   Loop back to notify gate to begin sweep
                    "	trigger_drain.addblock.branch.counter(tmName[2], \"branch-step\", \"notifyStep\",  gSMUsettings[3])",
                    "	trigger_drain.addblock.source.action.bias(tmName[2], \"drainbiaszeo\", infoSMU[4])",

                    ############################################## Gate Trigger Model ##############################################
                    ################################################################################################################

                    #   Configure trigger model source for linear voltage sweep
                    "	gateSMU.trigger.source.linearv(gSMUsettings[1], gSMUsettings[2], gSMUsettings[3])",
                    #   Set trigger model measurements to i/v and store in default buffers
                    "	gateSMU.trigger.measure.iv(gateSMU.defbuffer1,gateSMU.defbuffer2)",

                    "	local trigger_gate = slot[infoSMU[1]].trigger.model",
                    "	trigger_gate.create(tmName[1]) ",

                    #   Wait for notification from drain to begin
                    "	trigger_gate.addblock.wait(tmName[1],\"Wait1\",trigger.generator[1].EVENT_ID) ",
                    #   Advance gate source voltage
                    "	trigger_gate.addblock.wait(tmName[1],\"waitStep\",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY1 )",
                    #   Notify drain that gate voltage has advanced
                    "	trigger_gate.addblock.source.action.step(tmName[1], \"gateVoltage\", infoSMU[2])",

                    #   Wait for notification that drain source voltage has advanced
                    "	trigger_gate.addblock.notify(tmName[1],\"notify\",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY2)",
                    #   Measure gate i/v
                    "	trigger_gate.addblock.wait(tmName[1],\"waitMeasure\",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY3 )",
                    #   Notify drain that measurement has been taken
                    "	trigger_gate.addblock.measure(tmName[1],\"measure\",infoSMU[2],1)",
                    #   Loop back to wait for drain voltage to advance
                    "	trigger_gate.addblock.notify(tmName[1],\"notify\",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY4)",

                    #   Wait for notification that drain voltage sweep has completed
                    "	trigger_gate.addblock.branch.counter(tmName[1], \"branch-Measure\", \"waitMeasure\", dSMUsettings[3])",
                    #   Loop back to wait for drain to begin
                    "	trigger_gate.addblock.wait(tmName[1],\"waitSweepDone\",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY5 )",
                    "	trigger_gate.addblock.branch.counter(tmName[1], \"branch-Step\", \"waitStep\",  gSMUsettings[3])",
                    "	trigger_gate.addblock.source.action.bias(tmName[1], \"gatebiaszero\", infoSMU[2])",
                    "end",
                    ####################################################################################################################
                    #   Function:   Pulse_Waveform_Capture_MSMU_MP5000(infoSMU,srcSettings,meaSettings,pulseSettings,triggerName)
                    #   Parameters: infoSMU         A list containing the SMU slot/module locations
                    #                               {slot_no, sweepV_channel}
                    #               srcSettings     A list containing the source configuration settings
                    #                               {startV, stopV, noPoints, limitI}
                    #               meaSettings     A list containing the measure configuration settings
                    #                               {measRangeV, measRangeI, remoteSense}
                    #               pulseSettings   A list containing the pulse parameters
                    #                               {pulsePeriod, pulseWidth, mDelay, apertureTime}
                    #               triggerName     A string to name the trigger model
                    #
                    #   Purpose:    This function configures a channel to generate a voltage source pulsed waveform. The function 
                    #               records current and voltage to display to the user.
                    ####################################################################################################################
                    "function Pulse_Waveform_Capture_MSMU_MP5000(infoSMU,srcSettings,meaSettings,pulseSettings,triggerName)",
                    #   SMU channel assignment
                    "	local sweepV_SMU 						    = slot[infoSMU[1]].smu[infoSMU[2]]",
                    "	sweepV_SMU.reset()",
                    #   Source Settings
                    "	sweepV_SMU.source.func					    = sweepV_SMU.FUNC_DC_VOLTAGE",
                    "	sweepV_SMU.source.rangev				    = math.max(math.abs(srcSettings[1]), math.abs(srcSettings[2]))",
                    "	sweepV_SMU.source.limiti				    = srcSettings[4]",
                    "	sweepV_SMU.source.levelv 				    = 0",
                    #   Measure Settings
                    "	sweepV_SMU.measure.rangev				    = meaSettings[1]",
                    "	sweepV_SMU.measure.rangei				    = meaSettings[2]",
                    "	sweepV_SMU.measure.aperture			    	= pulseSettings[4]",
                    "	sweepV_SMU.sense						    = sweepV_SMU.SENSE_2WIRE",
                    "	sweepV_SMU.measure.autorangei		    	= 0",

                    "	if meaSettings[3] == true then",
                    "		sweepV_SMU.sense					    = sweepV_SMU.SENSE_4WIRE",
                    "	else",
                    "		sweepV_SMU.sense					    = sweepV_SMU.SENSE_2WIRE",
                    "	end	",
                    #   Buffer clear
                    "	sweepV_SMU.defbuffer1.clear()",
                    "	sweepV_SMU.defbuffer1.appendmode    		= 1",
                    "	sweepV_SMU.defbuffer2.clear()",
                    "	sweepV_SMU.defbuffer2.appendmode			= 1",
                    #   Calculate number of points
                    "  	local nPoints = math.ceil(((pulseSettings[1] * srcSettings[3]) + pulseSettings[1]) / pulseSettings[4])",

                    #   Configure trigger model source for linear voltage sweep
                    "	sweepV_SMU.trigger.source.linearv(srcSettings[1], srcSettings[2], srcSettings[3])",
                    #   Set trigger model to measure i/v and store in default buffers
                    "	sweepV_SMU.trigger.measure.iv(sweepV_SMU.defbuffer1,sweepV_SMU.defbuffer2)",

                    #   Configure trigger model
                    "	local triggerModel = slot[infoSMU[1]].trigger.model",
                    "	triggerModel.create(triggerName) ",
                    #   Wait for notification to begin
                    "	triggerModel.addblock.wait(triggerName,\"Wait1_pulse\",trigger.generator[1].EVENT_ID)",
                    #   Measureoverlapped allows measurements to be taken while trigger model is running in parallel
                    "	triggerModel.addblock.measureoverlapped(triggerName, \"measure_IV\", infoSMU[2], nPoints)",
                    "  	triggerModel.addblock.delay.constant(triggerName, \"prepulse_delay\", pulseSettings[1]/2)",
                    #   Advance to next voltage value in voltage sweep
                    "	triggerModel.addblock.source.action.step(triggerName, \"sweepV_IV\", infoSMU[2])",
                    "	triggerModel.addblock.delay.constant(triggerName, \"meas_pulse_width\", pulseSettings[2],\"sweepV_IV\")",
                    #   Set source level to 0
                    "	triggerModel.addblock.source.action.bias(triggerName, \"pulse_bias\", infoSMU[2])",
                    "	triggerModel.addblock.delay.constant(triggerName, \"meas_pulse_period\", pulseSettings[1],\"sweepV_IV\")",
                    #   Loop through all voltage sweep values
                    "	triggerModel.addblock.branch.counter(triggerName, \"branch-counter\", \"sweepV_IV\", srcSettings[3])",
                    "  	triggerModel.addblock.delay.constant(triggerName, \"postpulse_delay\", pulseSettings[1]) ",
                    "end ",
                    ####################################################################################################################
                    #   Function:   configure_DC_Laser_VCSEL_LIV_inTriggerModel(infoSMU,IF_Settings,PD_Settings, meaSettings,tmName)
                    #   Parameters: infoSMU         A list containing the SMU slot/module locations
                    #                               {IF_slot, IF_channel, PD_slot, PD_channel}
                    #               IF_Settings     A list containing the configuration settings for the IF channel
                    #                               {startIF, stopIF, noPoints, rangeI, limitV, measRangeV}
                    #               PD_Settings     A list containing the configuration settings for the PD channel
                    #                               {biasV_PD, srcRangeV_PD, measRangeI_PD}
                    #               meaSettings     A list containing the measure configuration settings
                    #                               {nplc, mDelay, remodeSense}
                    #               tmName          A list containing names for both trigger models
                    #                               {tm_name1, tm_name2}
                    #
                    #   Purpose:    This function configures two channels for an LIV test for a laser VCSEL. 
                    ####################################################################################################################
                    "function configure_DC_Laser_VCSEL_LIV_inTriggerModel(infoSMU,IF_Settings,PD_Settings, meaSettings,tmName)",
                    #   SMU channel assignment
                    "	local IF_SMU 							= slot[infoSMU[1]].smu[infoSMU[2]]",
                    "	local PD_SMU 							= slot[infoSMU[3]].smu[infoSMU[4]]",
                    "	local smu_id 							= {IF_SMU, PD_SMU}",

                    #   Configure all channels
                    "	for i = 1, 2 do",
                    "		smu_id[i].reset()",
                    #       Buffer clear
                    "		smu_id[i].defbuffer1.clear()",
                    "		smu_id[i].defbuffer1.appendmode		= 1",
                    "		smu_id[i].defbuffer2.clear()",
                    "		smu_id[i].defbuffer2.appendmode		= 1",
                    "		if smu_id[i] == IF_SMU then",
                    #           Source Settings
                    "			smu_id[i].source.func			= smu_id[i].FUNC_DC_CURRENT",
                    "			smu_id[i].source.rangei			= IF_Settings[4]",
                    "			smu_id[i].source.leveli			= 0",
                    "			smu_id[i].source.limitv			= IF_Settings[5]",
                    #           Measure Settings
                    "			smu_id[i].measure.rangev		= IF_Settings[6]",
                    "			smu_id[i].measure.rangei		= IF_Settings[4]",
                    "		else",
                    #           Source Settings
                    "			smu_id[i].source.func			= smu_id[i].FUNC_DC_VOLTAGE",
                    "			smu_id[i].source.rangev			= PD_Settings[2]",
                    "			smu_id[i].source.levelv			= PD_Settings[1]",
                    #           Measure Settings
                    "			smu_id[i].measure.rangei		= PD_Settings[3]",
                    "		end",

                    "		smu_id[i].measure.nplc				= meaSettings[1]",
                    "		if meaSettings[3] == true then",
                    "			smu_id[i].sense					= smu_id[i].SENSE_4WIRE",
                    "		else",
                    "			smu_id[i].sense					= smu_id[i].SENSE_2WIRE",
                    "		end",
                    "	end",

                    ########################################### IF Channel Trigger Model ###########################################
                    ################################################################################################################

                    #   Setup trigger model source for linear current sweep
                    "	IF_SMU.trigger.source.lineari(IF_Settings[1], IF_Settings[2], IF_Settings[3])",
                    #   Set trigger model to measure i/v and store in default buffers
                    "	IF_SMU.trigger.measure.iv(IF_SMU.defbuffer1,IF_SMU.defbuffer2)",

                    "	local trigger_IF = slot[infoSMU[1]].trigger.model",
                    "	trigger_IF.create(tmName[1]) ",

                    #   Wait for notification to begin
                    "	trigger_IF.addblock.wait(tmName[1],\"Wait1_if\",trigger.generator[1].EVENT_ID) ",

                    #   Notify PD trigger model to begin
                    "	trigger_IF.addblock.notify(tmName[1],\"notifyPDStep\",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY1)",

                    #   Wait for response from PD trigger model
                    "	trigger_IF.addblock.wait(tmName[1],\"waitPDStep\",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY2 )",
                    #   Advance to next source value
                    "	trigger_IF.addblock.source.action.step(tmName[1], \"IF_sweep\", infoSMU[2])",
                    "	trigger_IF.addblock.delay.constant(tmName[1],\"meaDelay\",meaSettings[2],\"IF_sweep\")",
                    #   Notify PD trigger model that step and wait are complete
                    "	trigger_IF.addblock.notify(tmName[1],\"notify\",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY3)",
                    #   Measure i/v on source terminals
                    "	trigger_IF.addblock.measure(tmName[1], \"measure\", infoSMU[2], 1)",

                    #   Wait for measurement completed notification
                    "	trigger_IF.addblock.wait(tmName[1],\"wait\",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY4 )",
                    #   Loop back to advancing source current
                    "	trigger_IF.addblock.branch.counter(tmName[1], \"IF_branch\", \"IF_sweep\", IF_Settings[3])",
                    #   Notify PD trigger model that current sweep is completed
                    "	trigger_IF.addblock.notify(tmName[1],\"notifySweepDone\",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY5)	",
                    "	trigger_IF.addblock.source.action.bias(tmName[1], \"IF_bias\", infoSMU[2])",

                    ########################################### PD Channel Trigger Model ###########################################
                    ################################################################################################################

                    #   Setup trigger model source for linear voltage sweep 
	                #   (voltage sweep is only one value so will stay constant through test)
                    "	PD_SMU.trigger.source.linearv(PD_Settings[1], PD_Settings[1], 1)",
                    #   Set trigger model to measure i/v and store in default buffers
                    "	PD_SMU.trigger.measure.iv(PD_SMU.defbuffer1,PD_SMU.defbuffer2)",

                    "	local trigger_PD = slot[infoSMU[3]].trigger.model",
                    "	trigger_PD.create(tmName[2])",

                    #   Wait for notification to begin
                    "	trigger_PD.addblock.wait(tmName[2],\"Wait1\",trigger.generator[1].EVENT_ID) ",

                    #   Wait for initiation from source trigger model
                    "	trigger_PD.addblock.wait(tmName[2],\"waitStep\",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY1 )",
                    #   Advance to next source value
                    "	trigger_PD.addblock.source.action.step(tmName[2], \"bias_PD\", infoSMU[4])",
                    #   Notify source trigger model that source has been stepped
                    "	trigger_PD.addblock.notify(tmName[2],\"notifyStep\",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY2)",

                    #   Wait for notification of completion from source trigger model
                    "	trigger_PD.addblock.wait(tmName[2],\"waitMeas\",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY3 )",
                    "	trigger_PD.addblock.delay.constant(tmName[2],\"meaDelay\",meaSettings[2])",
                    #   Measure i/v on PD terminals
                    "	trigger_PD.addblock.measure(tmName[2], \"measure\", infoSMU[4], 1)",
                    #   Notify source trigger model that measurement is completed
                    "	trigger_PD.addblock.notify(tmName[2],\"notify\",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY4)",
                    #   Loop back aand wait for notification from source trigger model
                    "	trigger_PD.addblock.branch.counter(tmName[2], \"branch-PD\", \"waitMeas\", IF_Settings[3])",

                    #   Wait for notification that source trigger model is completed
                    "	trigger_PD.addblock.wait(tmName[2],\"waitPDDone\",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY5 )",
                    #   Set source to 0
                    "	trigger_PD.addblock.source.action.bias(tmName[2], \"PDzero\", infoSMU[4])",
                    "end ",
                    ####################################################################################################################
                    #   Function:   configure_Sine_Waveform_Generate_MSMU_MP5000(noSlot, noCh, Vrms, numCycles, frequency, limitI,tm_Name)
                    #   Parameters: noSlot      Slot number of the module
                    #               noCh        Channel number to be used
                    #               Vrms        Vrms of generated sine wave
                    #               numCycles   Number of cycles to generate
                    #               frequency   Frequency of generated wave
                    #               limitI      Current limit for source
                    #               tm_name     Name for the trigger model
                    #
                    #   Purpose:    This function configures a channel to generate a sine wave according to user specifications.
                    ####################################################################################################################
                    "function configure_Sine_Waveform_Generate_MSMU_MP5000(settings, tm_Name)",
                    #   SMU alais
                    "   local noSlot    = settings[1]",
                    "   local noCh      = settings[2]",
                    "   local Vrms      = settings[3]",
                    "   local numCycles = settings[4]",
                    "   local frequency = settings[5]",
                    "   local limitI    = settings[6]",
                    "	local smu_ID    = slot[noSlot].smu[noCh]",
                    #   Calculate sinewave values
                    "	local Vpp				= Vrms * math.sqrt(2)",
                    "	local sourceValues		= {} ",
                    "	local pointsPerCycle	= 7200 / frequency",
                    "    local timeInterval      = 1/7200",
                    "	local numDataPoints		= pointsPerCycle * numCycles",
                    "	local numReadings",
                    #   Generate voltage sweep values
                    "	for i=1, numDataPoints do",
                    "		sourceValues[i]		= (Vpp * math.sin(i * 2 * math.pi / pointsPerCycle))",
                    "	end",
                    #   Create reading buffers
                    "	numReadings = 280 * numCycles",
                    "	smu_ID.reset()",
                    "	readingBuffer1 = smu_ID.makebuffer(5000)",
                    "	readingBuffer2 = smu_ID.makebuffer(5000)",

                    #   Configure channel settings
                    "	smu_ID.source.func = smu_ID.FUNC_DC_VOLTAGE",
                    "	smu_ID.source.autorangev = smu_ID.OFF",
                    "	smu_ID.source.rangev = 20",
                    "	smu_ID.source.limiti = limitI",
                    "	smu_ID.source.levelv = 0",
                    "	smu_ID.source.output = 1",
                    "	smu_ID.measure.aperture = 0.0001",
                    "	smu_ID.measure.rangei = 100e-3",
                    "	smu_ID.measure.rangev = 20",

                    #   Configure sweep voltage list
                    "	smu_ID.trigger.source.listv(sourceValues)",
                    #   Set trigger model readings for i/v and store in reading buffers
                    " 	smu_ID.trigger.measure.iv(readingBuffer1,readingBuffer2)", 

                    #   Configure trigger model
                    " 	local triggermodel = slot[noSlot].trigger.model",
                    " 	triggermodel.create(tm_Name)", 
                    #   Wait for notification to begin
                    " 	triggermodel.addblock.wait(tm_Name,\"Wait1\",trigger.generator[1].EVENT_ID)",
                    #   Measure overlapped allows for readings to be taken while triggermodel is executing in parallel
                    " 	triggermodel.addblock.measureoverlapped(tm_Name, \"measure3\", noCh, numReadings)",
                    " 	triggermodel.addblock.delay.constant(tm_Name, \"delay-init\", 2e-3)",
                    #   Advance through voltage sweep
                    " 	triggermodel.addblock.source.action.step(tm_Name, \"sweep_step1\",noCh)",
                    " 	triggermodel.addblock.delay.constant(tm_Name, \"delay-on2\", timeInterval,\"sweep_step1\")",
                    #   Loop through all voltage values
                    " 	triggermodel.addblock.branch.counter(tm_Name, \"branch-counter7\", \"sweep_step1\", numDataPoints)",
                    "end",
                    "endscript",
                    "CombinedTestScripts.run()"]
    # Write all commands to the instrument
    for cmd in tsp_command:
        myMP5000.write(cmd + "\n")
    myMP5000.close()
    # Confirm to user that script is loaded
    string_idn.config(text = "Test Script is loaded")
    print("Test Script is loaded")    

#########################################################################################
#   Function:   run_test_drain_family()
#   Purpose:    This function runs the drain family test that was loaded previously. This
#               handles retrieving user input, retrieving buffer data, and displaying 
#               result to the user.
#########################################################################################
def run_test_drain_family():
    # Clear figure
    fig1.clf()
    # Open instrument resource
    resource_string = ip_entry.get()
    myMP5000 = rm.open_resource(resource_string, read_termination = '\n')
    myMP5000.timeout = 20000

    # Retrieve location data from user
    location_assignments = task1_assign_input.get()[1:-1].split(",")
    slot_ga = int(location_assignments[0])
    ch_ga   = int(location_assignments[1])
    slot_dr = int(location_assignments[2])
    ch_dr   = int(location_assignments[3])
    # Retrieve Drain sweep parameters from user
    drain_parameters = task1_drain_input.get()[1:-1].split(",")
    startV  = float(drain_parameters[0])
    stopV   = float(drain_parameters[1])
    noPts   = int(drain_parameters[2])
    # Retrieve Gate sweep parameters from user
    gate_parameters = task1_gate_input.get()[1:-1].split(",")
    noGaPts = int(gate_parameters[2])
    # Initiate and complete the test
    tsp_command = [
        "configure_DrainFamilyCurve_VdId_TwoTriggers("+task1_assign_input.get()+","+task1_drain_input.get()+","+task1_gate_input.get()+",{0.05,0},{\"tm_gate\",\"tm_drain\"})\n",
        f"slot[{slot_ga}].smu[{ch_ga}].source.output = 1 \n",
        f"slot[{slot_dr}].smu[{ch_dr}].source.output = 1 \n",
        "slot[1].trigger.model.initiate(\"tm_gate\")\n",
        "slot[1].trigger.model.initiate(\"tm_drain\")\n",
        "trigger.generator[1].assert()\n",
        "waitcomplete()\n",
        f"slot[{slot_ga}].smu[{ch_ga}].source.output = 0 \n",
        f"slot[{slot_dr}].smu[{ch_dr}].source.output = 0 \n",
        "slot[1].trigger.model.delete(\"tm_gate\")\n",
        "slot[1].trigger.model.delete(\"tm_drain\")\n"
    ]
    for cmd in tsp_command:
        myMP5000.write(cmd)

    # Retrieve drain voltage data
    x_buffer = []
    for i in range(0,noPts):
        x_buffer.append(float(i*((stopV-startV)/(noPts-1)))) 
    x_array = np.array(x_buffer)
    
    # Retrieve drain current data
    y_buffer = []
    data = f"printbuffer(1,slot[{slot_dr}].smu[{ch_dr}].defbuffer1.n,slot[{slot_dr}].smu[{ch_dr}].defbuffer1)\n"
    readBuffer = myMP5000.query(data)
    readBuffer = readBuffer.strip().split(",")
    myMP5000.close()    

    print("\n######## VdId Test ########")
    print("Vd\t\tId")

    # Create plot for displaying data
    plot1 = fig1.add_subplot()
    plot1.grid()
    plot1.set_title("Drain Family Curve Test",fontsize=14)
    # Create plots for each sweep
    for k in range (0, noGaPts):
        for i in range((noPts*k),noPts*(k+1)):
            y_buffer.append(float(readBuffer[i]))
        y_array = np.array(y_buffer)
        for i in range(0,noPts):
            print(f"{"{:.5e}".format(x_array[i])}\t{y_array[i]}")
        plot1.plot(x_array,y_array,'-o', color='blue')
        y_buffer.clear()
        canvas1.draw() 
    print("VdId test done")
    print("###########################\n")

#########################################################################################
#   Function:   liv_test()
#   Purpose:    This function runs the liv test that was loaded previously. This
#               handles retrieving user input, retrieving buffer data, and displaying 
#               result to the user.
#########################################################################################
def liv_test():
    # Clear figure
    fig2.clf()
    # Open instrument connection
    resource_string = ip_entry.get()
    myMP5000 = rm.open_resource(resource_string, read_termination = '\n')
    myMP5000.timeout = 20000

    # Retrieve location data from user
    location_assignments = task2_assign_input.get()[1:-1].split(",")
    slot_ld = int(location_assignments[0])
    ch_ld   = int(location_assignments[1])
    slot_pd = int(location_assignments[2])
    ch_pd   = int(location_assignments[3])
    
    # Initiate and complete the liv test
    tsp_command = [
        "configure_DC_Laser_VCSEL_LIV_inTriggerModel("+task2_assign_input.get()+","+task2_ld_input.get()+","+task2_pd_input.get()+",{0.05,1e-3,false},{\"tm_laser\",\"tm_pd\"})\n",
        f"slot[{slot_ld}].smu[{ch_ld}].source.output = 1\n",
        f"slot[{slot_pd}].smu[{ch_pd}].source.output = 1\n",
        f"slot[{slot_pd}].trigger.model.initiate(\"tm_pd\")\n",
        f"slot[{slot_ld}].trigger.model.initiate(\"tm_laser\")\n",
        "trigger.generator[1].assert()\n",
        "waitcomplete()\n",
        f"slot[{slot_ld}].smu[{ch_ld}].source.output = 0\n",
        f"slot[{slot_pd}].smu[{ch_pd}].source.output = 0\n",
        f"slot[{slot_pd}].trigger.model.delete(\"tm_pd\")\n",
        f"slot[{slot_ld}].trigger.model.delete(\"tm_laser\")\n",
    ]
    for cmd in tsp_command:
        myMP5000.write(cmd)
    
    print("\n################ LIV Test #################")
    print("I_F\t\tV_F\t\tI_D")

    # Retrieve ld current data
    x_buffer = []
    data = f"printbuffer(1,slot[{slot_ld}].smu[{ch_ld}].defbuffer1.n, slot[{slot_ld}].smu[{ch_ld}].defbuffer1)"
    readBuffer = myMP5000.query(data)
    readBuffer = readBuffer.strip().split(",")
    x_buffer = [float(i) for i in readBuffer]
    x_array = np.array(x_buffer)
    # Retrieve ld voltage data
    y_buffer = []
    data = f"printbuffer(1,slot[{slot_ld}].smu[{ch_ld}].defbuffer2.n,slot[{slot_ld}].smu[{ch_ld}].defbuffer2)\n"
    readBuffer = myMP5000.query(data)
    readBuffer = readBuffer.strip().split(",")
    y_buffer =[float(i) for i in readBuffer]
    y_array = np.array(y_buffer)
    # Retrieve pd current data
    y2_buffer = []
    data = f"printbuffer(1,slot[{slot_pd}].smu[{ch_pd}].defbuffer1.n,slot[{slot_pd}].smu[{ch_pd}].defbuffer1)\n"
    readBuffer = myMP5000.query(data)
    readBuffer = readBuffer.strip().split(",")
    myMP5000.close() 
    y2_buffer =[float(i) for i in readBuffer]
    y2_array = np.array(y2_buffer)
    # Plot results
    plot2 = fig2.add_subplot()
    plot2.grid()
    plot2.set_title("Laser/VCSEL L-I-V Test",fontsize=14)
    plot2.plot(x_array,y_array,'-o',color='blue')    

    plot22 = plot2.twinx()
    plot22.plot(x_array,y2_array,'-o',color='red')    

    canvas2.draw() 

    for i in range(len(x_buffer)):
        print("{:.5e}".format(x_buffer[i]), "{:.5e}".format(y_buffer[i]), "{:.5e}".format(y2_buffer[i]), sep="\t")
    print("LIV test done")
    print("###########################################\n")

#########################################################################################
#   Function:   pulse_test()
#   Purpose:    This function runs the pulse test that was loaded previously. This
#               handles retrieving user input, retrieving buffer data, and displaying 
#               result to the user.
#########################################################################################
def pulse_test():
    # Clear figure
    fig3.clf()
    # Open instrument connection
    resource_string = ip_entry.get()
    myMP5000 = rm.open_resource(resource_string, read_termination = '\n')
    myMP5000.timeout = 20000

    # Fetch module location data from user
    location_assignments = task3_assign_input.get()[1:-1].split(",")
    slot_no = int(location_assignments[0])
    chan_no = int(location_assignments[1])

    # Initiate and complete pulse test
    tsp_command = [
        "Pulse_Waveform_Capture_MSMU_MP5000("+task3_assign_input.get()+","+task3_src_input.get()+",{6, 0.1, false}, "+task3_pulse_input.get()+",\"TM_sweepV_pulse\")\n",
        f"slot[{slot_no}].smu[{chan_no}].source.output = 1 \n",
        f"slot[{slot_no}].trigger.model.initiate(\"TM_sweepV_pulse\")\n",
        "delay(100e-3)",
        "trigger.generator[1].assert()\n",
        "waitcomplete()\n",
        f"slot[{slot_no}].smu[{chan_no}].source.output = 0 \n",
        f"slot[{slot_no}].trigger.model.delete(\"TM_sweepV_pulse\")\n"
    ]
    for cmd in tsp_command:
        myMP5000.write(cmd)

    print("\n######## Pulse Test ########")
    print("Time\t\tV")

    # Retrieve timestamp data
    x_buffer = []
    data = f"printbuffer(1,slot[{slot_no}].smu[{chan_no}].defbuffer2.n,slot[{slot_no}].smu[{chan_no}].defbuffer2.timestamps)\n"
    readBuffer = myMP5000.query(data)
    readBuffer = readBuffer.strip().split(",")
    x_buffer = [float(i) for i in readBuffer]
    # Retrieve voltage data
    y_buffer = []
    data = f"printbuffer(1,slot[{slot_no}].smu[{chan_no}].defbuffer2.n,slot[{slot_no}].smu[{chan_no}].defbuffer2)\n"
    readBuffer = myMP5000.query(data)
    readBuffer = readBuffer.strip().split(",")
    y_buffer = [float(i) for i in readBuffer]

    # Plot data
    plot3 = fig3.add_subplot()
    plot3.grid()
    plot3.set_title("Voltage Pulse Sweep",fontsize=14)
    plot3.plot(x_buffer,y_buffer,linewidth = 3,color='magenta')    
    canvas3.draw() 
    
    for i in range(len(x_buffer)):
        print("{:.5e}".format(x_buffer[i]), "{:.5e}".format(y_buffer[i]), sep="\t")
    myMP5000.close() 
    print("Pulse test done")
    print("############################\n")

#########################################################################################
#   Function:   sine_test()
#   Purpose:    This function runs the sine generation test that was loaded previously. 
#               This handles retrieving user input, retrieving buffer data, and
#               displaying result to the user.
#########################################################################################
def sine_test():
    # Clear figure
    fig4.clf()
    # Open instrument connection
    resource_string = ip_entry.get()
    myMP5000 = rm.open_resource(resource_string, read_termination = '\n')
    myMP5000.timeout = 20000

    settings = task4_src_input.get()[1:-1].split(",")
    slot_no = settings[0]
    chan_no = settings[1]

    # Initiate and complete sine generation
    tsp_command = [
        "configure_Sine_Waveform_Generate_MSMU_MP5000("+task4_src_input.get()+", \"TM_sine\")\n",
        f"slot[{slot_no}].smu[{chan_no}].source.output = 1 \n",
        f"slot[{slot_no}].trigger.model.initiate(\"TM_sine\")\n",
        "delay(100e-3)",
        "trigger.generator[1].assert()\n",
        "waitcomplete()\n",
        f"slot[{slot_no}].smu[{chan_no}].source.output = 0 \n",
        f"slot[{slot_no}].trigger.model.delete(\"TM_sine\")\n"
    ]
    for cmd in tsp_command:
        myMP5000.write(cmd)

    print("\n######## Sine Test #########")
    print("Time\t\tV")
    
    # Retrieve timestamp data
    x_buffer = []
    data = "printbuffer(1,readingBuffer2.n,readingBuffer2.timestamps)\n"
    readBuffer = myMP5000.query(data)
    readBuffer = readBuffer.strip().split(",")
    x_buffer = [float(i) for i in readBuffer]
    # Retrieve voltage data
    y_buffer = []
    data = "printbuffer(1,readingBuffer2.n,readingBuffer2)\n"
    readBuffer = myMP5000.query(data)
    readBuffer = readBuffer.strip().split(",")
    y_buffer = [float(i) for i in readBuffer]
    # Plot results
    plot4 = fig4.add_subplot()
    plot4.grid()
    plot4.set_title("Sine Generation",fontsize=14)
    plot4.plot(x_buffer,y_buffer,linewidth = 3, color='darkblue')    
    canvas4.draw() 
    
    for i in range(len(x_buffer)):
        print("{:.5e}".format(x_buffer[i]), "{:.5e}".format(y_buffer[i]), sep="\t")
    myMP5000.close() 
    print("Sine test done")
    print("############################\n")

#########################################################################################
#   Function:   plot()
#   Purpose:    This function runs and plots the results from all tests.
#########################################################################################
def plot(): 
    # Clear all figures
    fig1.clf()
    fig2.clf()
    fig3.clf()
    fig4.clf()

    # Open instrument connection
    resource_string = ip_entry.get()
    myMP5000 = rm.open_resource(resource_string, read_termination = '\n')
    myMP5000.timeout = 20000

    # Retrieve location data from user
    task1_location_assignments = task1_assign_input.get()[1:-1].split(",")
    slot_ga = int(task1_location_assignments[0])
    ch_ga   = int(task1_location_assignments[1])
    slot_dr = int(task1_location_assignments[2])
    ch_dr   = int(task1_location_assignments[3])
    # Retrieve Drain sweep parameters from user
    drain_parameters = task1_drain_input.get()[1:-1].split(",")
    startV  = float(drain_parameters[0])
    stopV   = float(drain_parameters[1])
    noPts   = int(drain_parameters[2])
    # Retrieve Gate sweep parameters from user
    gate_parameters = task1_gate_input.get()[1:-1].split(",")
    noGaPts = int(gate_parameters[2])
    # Retrieve location data from user
    task2_location_assignments = task2_assign_input.get()[1:-1].split(",")
    slot_ld = int(task2_location_assignments[0])
    ch_ld   = int(task2_location_assignments[1])
    slot_pd = int(task2_location_assignments[2])
    ch_pd   = int(task2_location_assignments[3])
    # Fetch module location data from user
    task3_location_assignments = task3_assign_input.get()[1:-1].split(",")
    slot_no_3 = int(task3_location_assignments[0])
    chan_no_3 = int(task3_location_assignments[1])
    # Retrieve location data from user
    task4_location_assignments = task4_src_input.get()[1:-1].split(",")
    slot_no_4 = task4_location_assignments[0]
    chan_no_4 = task4_location_assignments[1]


    tsp_command = [
        "configure_DrainFamilyCurve_VdId_TwoTriggers("+task1_assign_input.get()+","+task1_drain_input.get()+","+task1_gate_input.get()+",{0.05,0},{\"tm_gate\",\"tm_drain\"})\n",
        f"slot[{slot_ga}].smu[{ch_ga}].source.output = 1 \n",
        f"slot[{slot_dr}].smu[{ch_dr}].source.output = 1 \n",
        f"slot[{slot_ga}].trigger.model.initiate(\"tm_gate\")\n",
        f"slot[{slot_dr}].trigger.model.initiate(\"tm_drain\")\n",
        "configure_DC_Laser_VCSEL_LIV_inTriggerModel("+task2_assign_input.get()+","+task2_ld_input.get()+","+task2_pd_input.get()+",{0.05,1e-3,false},{\"tm_laser\",\"tm_pd\"})\n",
        f"slot[{slot_ld}].smu[{ch_ld}].source.output = 1 \n",
        f"slot[{slot_pd}].smu[{ch_pd}].source.output = 1 \n",
        f"slot[{slot_pd}].trigger.model.initiate(\"tm_pd\")\n",
        f"slot[{slot_ld}].trigger.model.initiate(\"tm_laser\")\n",
        "Pulse_Waveform_Capture_MSMU_MP5000("+task3_assign_input.get()+","+task3_src_input.get()+",{6, 0.1, false},"+task3_pulse_input.get()+",\"TM_sweepV_pulse\")\n",
        f"slot[{slot_no_3}].smu[{chan_no_3}].source.output = 1 \n",
        f"slot[{slot_no_3}].trigger.model.initiate(\"TM_sweepV_pulse\")\n",
        "configure_Sine_Waveform_Generate_MSMU_MP5000("+task4_src_input.get()+",\"TM_sine\")\n",
        f"slot[{slot_no_4}].smu[{chan_no_4}].source.output = 1 \n",
        f"slot[{slot_no_4}].trigger.model.initiate(\"TM_sine\")\n",
        "trigger.generator[1].assert()\n",
        "waitcomplete()\n",
        f"slot[{slot_ga}].smu[{ch_ga}].source.output = 0 \n",
        f"slot[{slot_dr}].smu[{ch_dr}].source.output = 0 \n",
        f"slot[{slot_ga}].trigger.model.delete(\"tm_gate\")\n",
        f"slot[{slot_dr}].trigger.model.delete(\"tm_drain\")\n"
    ]
    for cmd in tsp_command:
        myMP5000.write(cmd)
    print("Tests complete")

################################################## VdId Test ###################################################
################################################################################################################

    # Retrieve drain voltage data
    x_buffer = []
    for i in range(0,noPts):
        x_buffer.append(float(i*((stopV-startV)/(noPts-1)))) 
    x_array = np.array(x_buffer)
    
    # Retrieve drain current data
    y_buffer = []
    data = f"printbuffer(1,slot[{slot_dr}].smu[{ch_dr}].defbuffer1.n,slot[{slot_dr}].smu[{ch_dr}].defbuffer1)\n"
    readBuffer = myMP5000.query(data)
    readBuffer = readBuffer.strip().split(",")

    print("\n######## VdId Test ########")
    print("Vd\t\tId")

    # Create plot for displaying data
    plot1 = fig1.add_subplot()
    plot1.grid()
    plot1.set_title("Drain Family Curve Test",fontsize=14)
    # Create plots for each sweep
    for k in range (0, noGaPts):
        for i in range((noPts*k),noPts*(k+1)):
            y_buffer.append(float(readBuffer[i]))
        y_array = np.array(y_buffer)
        for i in range(0,noPts):
            print(f"{"{:.5e}".format(x_array[i])}\t{y_array[i]}")
        plot1.plot(x_array,y_array,'-o', color='blue')
        y_buffer.clear()
        canvas1.draw() 
    print("VdId test done")
    print("###########################\n")

################################################## LIV Test ###################################################
################################################################################################################

    tsp_command = [
        f"slot[{slot_ld}].smu[{ch_ld}].source.output = 0 \n",
        f"slot[{slot_pd}].smu[{ch_pd}].source.output = 0 \n",
        f"slot[{slot_ld}].trigger.model.delete(\"tm_laser\")\n",
        f"slot[{slot_pd}].trigger.model.delete(\"tm_pd\")\n"
    ]
    for cmd in tsp_command:
        myMP5000.write(cmd)

    print("\n################ LIV Test #################")
    print("I_F\t\tV_F\t\tI_D")

    # Retrieve ld current data
    x_buffer = []
    data = f"printbuffer(1,slot[{slot_ld}].smu[{ch_ld}].defbuffer1.n, slot[{slot_ld}].smu[{ch_ld}].defbuffer1)"
    readBuffer = myMP5000.query(data)
    readBuffer = readBuffer.strip().split(",")
    x_buffer = [float(i) for i in readBuffer]
    x_array = np.array(x_buffer)
    # Retrieve ld voltage data
    y_buffer = []
    data = f"printbuffer(1,slot[{slot_ld}].smu[{ch_ld}].defbuffer2.n,slot[{slot_ld}].smu[{ch_ld}].defbuffer2)\n"
    readBuffer = myMP5000.query(data)
    readBuffer = readBuffer.strip().split(",")
    y_buffer =[float(i) for i in readBuffer]
    y_array = np.array(y_buffer)
    # Retrieve pd current data
    y2_buffer = []
    data = f"printbuffer(1,slot[{slot_pd}].smu[{ch_pd}].defbuffer1.n,slot[{slot_pd}].smu[{ch_pd}].defbuffer1)\n"
    readBuffer = myMP5000.query(data)
    readBuffer = readBuffer.strip().split(",")
    y2_buffer =[float(i) for i in readBuffer]
    y2_array = np.array(y2_buffer)
    # Plot results
    plot2 = fig2.add_subplot()
    plot2.grid()
    plot2.set_title("Laser/VCSEL L-I-V Test",fontsize=14)
    plot2.plot(x_array,y_array,'-o',color='blue')    

    plot22 = plot2.twinx()
    plot22.plot(x_array,y2_array,'-o',color='red')    

    canvas2.draw() 

    for i in range(len(x_buffer)):
        print("{:.5e}".format(x_buffer[i]), "{:.5e}".format(y_buffer[i]), "{:.5e}".format(y2_buffer[i]), sep="\t")
    print("LIV test done")
    print("###########################################\n")

############################################# Pulse Waveform Test ##############################################
################################################################################################################

    tsp_command = [
        f"slot[{slot_no_3}].smu[{chan_no_3}].source.output = 0 \n",
        f"slot[{slot_no_3}].trigger.model.delete(\"TM_sweepV_pulse\")\n"
    ]
    for cmd in tsp_command:
        myMP5000.write(cmd)

    print("\n######## Pulse Test ########")
    print("Time\t\tV")
   
    # Retrieve timestamp data
    x_buffer = []
    data = f"printbuffer(1,slot[{slot_no_3}].smu[{chan_no_3}].defbuffer2.n,slot[{slot_no_3}].smu[{chan_no_3}].defbuffer2.timestamps)\n"
    readBuffer = myMP5000.query(data)
    readBuffer = readBuffer.strip().split(",")
    x_buffer = [float(i) for i in readBuffer]
    # Retrieve voltage data
    y_buffer = []
    data = f"printbuffer(1,slot[{slot_no_3}].smu[{chan_no_3}].defbuffer2.n,slot[{slot_no_3}].smu[{chan_no_3}].defbuffer2)\n"
    readBuffer = myMP5000.query(data)
    readBuffer = readBuffer.strip().split(",")
    y_buffer = [float(i) for i in readBuffer]

    # Plot data
    plot3 = fig3.add_subplot()
    plot3.grid()
    plot3.set_title("Voltage Pulse Sweep",fontsize=14)
    plot3.plot(x_buffer,y_buffer,linewidth = 3,color='magenta')    
    canvas3.draw() 
    
    for i in range(len(x_buffer)):
        print("{:.5e}".format(x_buffer[i]), "{:.5e}".format(y_buffer[i]), sep="\t")
    print("Pulse test done")
    print("############################\n")

############################################## Sine Waveform Test ##############################################
################################################################################################################

    tsp_command = [
        f"slot[{slot_no_4}].smu[{chan_no_4}].source.output = 0 \n",
        f"slot[{slot_no_4}].trigger.model.delete(\"TM_sine\")\n"
    ]
    for cmd in tsp_command:
        myMP5000.write(cmd)

    print("\n######## Sine Test #########")
    print("Time\t\tV")
   
    # Retrieve timestamp data
    x_buffer = []
    data = "printbuffer(1,readingBuffer2.n,readingBuffer2.timestamps)\n"
    readBuffer = myMP5000.query(data)
    readBuffer = readBuffer.strip().split(",")
    x_buffer = [float(i) for i in readBuffer]
    # Retrieve voltage data
    y_buffer = []
    data = "printbuffer(1,readingBuffer2.n,readingBuffer2)\n"
    readBuffer = myMP5000.query(data)
    readBuffer = readBuffer.strip().split(",")
    y_buffer = [float(i) for i in readBuffer]
    # Plot results
    plot4 = fig4.add_subplot()
    plot4.grid()
    plot4.set_title("Sine Generation",fontsize=14)
    plot4.plot(x_buffer,y_buffer,linewidth = 3, color='darkblue')    
    canvas4.draw() 
    
    for i in range(len(x_buffer)):
        print("{:.5e}".format(x_buffer[i]), "{:.5e}".format(y_buffer[i]), sep="\t")
    myMP5000.close() 
    print("Sine test done")
    print("############################\n")


###################################### Generate UI ######################################
#########################################################################################

# Create Window
window = tk.Tk() 
window.config(bg='grey')
window.geometry("1260x730")
s = ttk.Style()
s.theme_use('clam')
s.configure('new.TFrame',background = 'grey')
s.configure("TButton", background = 'darkgrey')

# Create figure locations
content = ttk.Frame(window,style = 'new.TFrame')
content.grid(column=0, row=0)
fig1 = Figure(figsize = (5, 3), dpi = 100,facecolor='lightgrey') 
fig2 = Figure(figsize = (5, 3), dpi = 100,facecolor='lightgrey') 
fig3 = Figure(figsize = (5, 3), dpi = 100,facecolor='lightgrey') 
fig4 = Figure(figsize = (5, 3), dpi = 100,facecolor='lightgrey') 


frame1 = ttk.Frame(content)
frame2 = ttk.Frame(content)
frame3 = ttk.Frame(content)
frame4 = ttk.Frame(content)

# Check VISA string settings
check_button = ttk.Button(master = content,command = check_SMU,text = "Check Inst") 
check_button.grid(column=0,row=0,ipadx=10,sticky = "w")
# VISA entry box
ip_entry = ttk.Entry(content,width=15,foreground='black')
ip_entry.insert(0,'TCPIP0::192.168.0.2::5025::SOCKET')
ip_entry.grid(column=1, row=0, columnspan=1,sticky="w")

# Loadscript button
loadscript = ttk.Button(content, command = load_script, text="LoadScript")
loadscript.grid(column=0,row=1,ipadx=10,sticky = "w")
# VISA output string
string_idn  = ttk.Label(content,background='grey')
string_idn.grid(column=0,row=2,columnspan =3,sticky="w")
# Title string
text=ttk.Label(content,text="6CH SMU Parallel Test in Synchronization",foreground="white",background="grey",font=('Aerial bold',20))
text.grid(column=4, row=0,rowspan = 2, columnspan = 15)

# Run task one button
run_button_1= ttk.Button(master = content,command = run_test_drain_family,text = "Run Task1") 
run_button_1.grid(column=0, row=3,ipadx=10, rowspan=1,sticky = "w")
# Task 1 configuration
task1_name  = ttk.Label(content,text="Drain Family Curve",background='grey')
task1_name.grid(column=1, row=3,sticky="w")
task1_assign= ttk.Label(content,text="Assign {slot_ga,ch_ga,slot_dr,ch_dr}",background='grey')
task1_assign.grid(column=0, row=4,columnspan=2,sticky="w")
task1_assign_input= ttk.Entry(content,width=30)
task1_assign_input.insert(0,"{1,1,1,2}")
task1_assign_input.grid(column=0, row=5,columnspan=2,sticky="w")
task1_drain= ttk.Label(content,text="Drain {StartV,StopV,NoPts,Rng_Id,LimitId}",background='grey')
task1_drain.grid(column=0, row=6,columnspan=2,sticky="w")
task1_drain_input= ttk.Entry(content,width=30)
task1_drain_input.insert(0,"{0,2,41,100e-3,100e-3}")
task1_drain_input.grid(column=0, row=7,columnspan=2,sticky="w")
task1_gate= ttk.Label(content,text="Gate {StartV,StopV,NoPts,LimitIg}",background='grey')
task1_gate.grid(column=0, row=8,columnspan=2,sticky="w")
task1_gate_input= ttk.Entry(content,width=30)
task1_gate_input.insert(0,"{1.4,1.8,3,0.1}")
task1_gate_input.grid(column=0, row=9,columnspan=2,sticky="w")

string_empty2  = ttk.Label(content,background='grey')
string_empty2.grid(column=0,row=10,sticky="w")

# Run task two button
run_button_2= ttk.Button(master = content,command = liv_test,text = "Run Task2") 
run_button_2.grid(column=0, row=11,ipadx=10, rowspan=1,sticky = "w")
# Task two configuration
task2_name  = ttk.Label(content,text="LIV Test",background='grey')
task2_name.grid(column=1, row=11,sticky="w")
task2_assign= ttk.Label(content,text="Assign {slot_ld,ch_ld,slot_pd,ch_pd}",background='grey')
task2_assign.grid(column=0, row=12,columnspan=2,sticky="w")
task2_assign_input= ttk.Entry(content,width=30)
task2_assign_input.insert(0,"{2,1,2,2}")
task2_assign_input.grid(column=0, row=13,columnspan=2,sticky="w")
task2_ld= ttk.Label(content,text="LD {StartI,StopI,NoPts,RngI,limV,MeaRngV}",background='grey')
task2_ld.grid(column=0, row=14,columnspan=2,sticky="w")
task2_ld_input= ttk.Entry(content,width=30)
task2_ld_input.insert(0,"{0,100e-3,21,1,6,6}")
task2_ld_input.grid(column=0, row=15,columnspan=2,sticky="w")
task2_pd= ttk.Label(content,text="PD {BiasV,SrcRngV,MeaRngI}",background='grey')
task2_pd.grid(column=0, row=16,columnspan=2,sticky="w")
task2_pd_input= ttk.Entry(content,width=30)
task2_pd_input.insert(0,"{0,6,10e-3}")
task2_pd_input.grid(column=0, row=17,columnspan=2,sticky="w")

string_empty3  = ttk.Label(content,background='grey')
string_empty3.grid(column=0,row=18,sticky="w")

# Run task three button
run_button_3= ttk.Button(master = content,command = pulse_test,text = "Run Task3") 
run_button_3.grid(column=0, row=19,ipadx=10, rowspan=1,sticky = "w")
# Task three configuration
task3_name  = ttk.Label(content,text="Pulse Test",background='grey')
task3_name.grid(column=1, row=19,sticky="w")
task3_assign= ttk.Label(content,text="Assign {slot_smu,ch_smu}",background='grey')
task3_assign.grid(column=0, row=20,columnspan=2,sticky="w")
task3_assign_input= ttk.Entry(content,width=30)
task3_assign_input.insert(0,"{3,1}")
task3_assign_input.grid(column=0, row=21,columnspan=2,sticky="w")
task3_src= ttk.Label(content,text="Src Set {StartV,StopV,NoPts,LimI}",background='grey')
task3_src.grid(column=0, row=22,columnspan=2,sticky="w")
task3_src_input= ttk.Entry(content,width=30)
task3_src_input.insert(0,"{-5,5,11,0.1}")
task3_src_input.grid(column=0, row=23,columnspan=2,sticky="w")
task3_pulse= ttk.Label(content,text="Pulse {Period,Width,Delay,Intg}",background='grey')
task3_pulse.grid(column=0, row=24,columnspan=2,sticky="w")
task3_pulse_input= ttk.Entry(content,width=30)
task3_pulse_input.insert(0,"{5e-3,3e-3,1e-3,0.1e-3}")
task3_pulse_input.grid(column=0, row=25,columnspan=2,sticky="w")

string_empty4  = ttk.Label(content,background='grey')
string_empty4.grid(column=0,row=26,sticky="w")

# Run task four button
run_button_4= ttk.Button(master = content,command = sine_test,text = "Run Task4") 
run_button_4.grid(column=0, row=27,ipadx=10, rowspan=1,sticky = "w")
# Task four configuration
task4_name  = ttk.Label(content,text="Sine Test",background='grey')
task4_name.grid(column=1, row=27,sticky="w")
task4_src= ttk.Label(content,text="Input:slot,ch,Vrms,NoCyle,Freq,LimI",background='grey')
task4_src.grid(column=0, row=28,columnspan=2,sticky="w")
task4_src_input= ttk.Entry(content,width=30)
task4_src_input.insert(0,"{3, 2, 5, 3, 60, 0.1}")
task4_src_input.grid(column=0, row=29,columnspan=2,sticky="w")

string_empty5  = ttk.Label(content,background='grey')
string_empty5.grid(column=0,row=30,sticky="w")
# Run all button
plot_button = ttk.Button(master = content,command = plot,text = "Run All") 
plot_button.grid(column=0, row=31,ipadx=10, ipady=5, rowspan=2,sticky = "w")

# Place frames
frame1.grid(column=4, row=3, columnspan=5, rowspan=15,sticky='nw')
frame2.grid(column=10, row=3, columnspan=5, rowspan=15,sticky='ne')
frame3.grid(column=4, row=16, columnspan=5, rowspan=15)
frame4.grid(column=10, row=16, columnspan=5, rowspan=15)

# Test title
window.title('Parallel Test in Synchronization')

canvas1 = FigureCanvasTkAgg(fig1, master = frame1)
canvas2 = FigureCanvasTkAgg(fig2, master = frame2)
canvas3 = FigureCanvasTkAgg(fig3, master = frame3)
canvas4 = FigureCanvasTkAgg(fig4, master = frame4)

canvas1_widget = canvas1.get_tk_widget()
canvas2_widget = canvas2.get_tk_widget()
canvas3_widget = canvas3.get_tk_widget()
canvas4_widget = canvas4.get_tk_widget()
canvas1_widget.pack()
canvas2_widget.pack()
canvas3_widget.pack()
canvas4_widget.pack()

# Start window
window.mainloop() 
