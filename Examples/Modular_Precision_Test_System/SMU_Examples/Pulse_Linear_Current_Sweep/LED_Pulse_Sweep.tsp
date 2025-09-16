--[[
################################################################################

Script File: LED_Pulse_Sweep.tsp

    ************************************************************************
    *** Copyright Tektronix, Inc.                                        ***
    *** See www.tek.com/sample-license for licensing terms.              ***
    ************************************************************************

Description:
    This script is example code, which creates (and subsequently calls) several
    functions that can be used with the Model MP5000 Based SMUs to perform a
	current sweeping. The purpose is show that you can perform a diode device
	characterization with the SMUs. As written, one channel of SMU is 
	assigned to the anode for the high and cathode for the low terminal.
	This pulse test should be excuted in trigger model. the first script shows
	how much accurate the delay constance with reference makes pulse. 
	The second script shows how to make pulse with trigger timer object. 
	Upon completion of each test, the data is printed to the TSP Toolkit Console 
	in a format that is suitable for copying and pasting into Microsoft Excel for 
	graphing and analysis.

Required Equipment: 1 Model MP5000 Mainframe 
					1 channel SMU 
					1 small LED

Note:  The functions do not perform any error checking.  It is the user's 
       responsibility to specify settings that are compatible with the 
       instrument model being used, and with its power envelope.
       
Note:  It is the user's responsibility to follow all safety guidelines given in 
       the instrument's Reference Manual.  This is especially critical if 
       voltages in excess of 42VDC will be present in the test circuits.  Such 
       voltage levels are hazardous. 
       
Functions created by this script:
    * Pulse_Current_Sweep_Diode_inDelayConstant({slot_no,IF_channel},{startIF,stopIF,noPoints, rangeI, limitV},{measRangeV, remoteSense},{pulsePeriod, pulseWidth, mDelay, apertureTime},tm_name) 
    * DC_Current_Sweep_Diode_inTriggerModel({slot_no,IF_channel},{startIF,stopIF,noPoints, rangeI, limitV},{measRangeV, remoteSense},{pulsePeriod, pulseWidth, mDelay, apertureTime},tm_name)

Example Usage:
    * Pulse_Current_Sweep_Diode_inDelayConstant({1,1},{0,300e-3,31 , 1000e-3, 6}, {6, false}, {5e-3,3e-3,1e-3,1e-3},"TM_diode_pulse")
	* Pulse_Current_Sweep_Diode_inTriggerTimer({1,1},{0,300e-3,31 , 1000e-3, 6}, {6, false}, {5e-3,3e-3,1e-3,1e-3},"TM_diode_pulse")
	
################################################################################
--]]

function Pulse_Current_Sweep_Diode_inDelayConstant(infoSMU,srcSettings,meaSettings,pulseSettings,triggerName)
	-- SMU channel assignment
	local IF_SMU 							= slot[infoSMU[1]].smu[infoSMU[2]]
	IF_SMU.reset()
	-- Source Settings
	IF_SMU.source.func						= IF_SMU.FUNC_DC_CURRENT
	IF_SMU.source.rangei					= srcSettings[4]
	IF_SMU.source.leveli					= 0
	IF_SMU.source.limitv					= srcSettings[5]
	-- Measure Settings
	IF_SMU.measure.rangev					= meaSettings[1]
	IF_SMU.measure.rangei					= srcSettings[4]
	IF_SMU.measure.aperture					= pulseSettings[4]
	IF_SMU.measure.autorangei				= 0
	if meaSettings[2] == true then
		IF_SMU.sense						= IF_SMU.SENSE_4WIRE
	else
		IF_SMU.sense						= IF_SMU.SENSE_2WIRE
	end
	-- Buffer clear
	IF_SMU.defbuffer1.clear()
	IF_SMU.defbuffer1.appendmode			= 1
	IF_SMU.defbuffer2.clear()
	IF_SMU.defbuffer2.appendmode			= 1

	-- Configure trigger model source for a linear current sweep
	IF_SMU.trigger.source.lineari(srcSettings[1], srcSettings[2], srcSettings[3])
	-- Set trigger model measurements to store in default buffers and measure current/voltage
	IF_SMU.trigger.measure.iv(IF_SMU.defbuffer1,IF_SMU.defbuffer2)

	-- Configure trigger model
	local triggerModel = slot[infoSMU[1]].trigger.model
	triggerModel.create(triggerName) 
	-- Step to next source value
	triggerModel.addblock.source.action.step(triggerName, "IF_sweep", infoSMU[2])
	triggerModel.addblock.delay.constant(triggerName, "meas_delay", pulseSettings[3])
	-- Measure iv and store in buffers
	triggerModel.addblock.measure(triggerName, "VF_measure", infoSMU[2], 1)
	triggerModel.addblock.delay.constant(triggerName, "delay_pulse_width", pulseSettings[2],"IF_sweep")
	-- Reset source to 0
	triggerModel.addblock.source.action.bias(triggerName, "pulse_bias", infoSMU[2])	
	triggerModel.addblock.delay.constant(triggerName, "delay_pulse_period", pulseSettings[1],"IF_sweep")
	-- Loop through all values in current sweep
	triggerModel.addblock.branch.counter(triggerName, "IF_branch", "IF_sweep", srcSettings[3])
	-- Reset source to 0 at end of cycle
	triggerModel.addblock.source.action.bias(triggerName, "IF_bias", infoSMU[2])

	IF_SMU.source.output = 1
	IF_SMU.source.output = 1

	-- Initiate model, delete when completed
	triggerModel.initiate(triggerName)
	waitcomplete()
	IF_SMU.source.output = 0
	triggerModel.delete(triggerName)	

	-- Read buffers and display
	print("T\t\t IF\t\t VF")
	for j = 1, IF_SMU.defbuffer1.n , 1 do
		print(IF_SMU.defbuffer1.timestamps[j], IF_SMU.defbuffer1[j],IF_SMU.defbuffer2[j])
	end

	-- Check for errors and display
	function errorQUEUE()
		errorqueue_Count = errorqueue.count
		print("Error Queue Count:".. errorqueue_Count)
		if errorqueue_Count > 0 then
		  for i = 1, errorqueue_Count do
			print(i, errorqueue.next())
		  end
		end
	end
end

function Pulse_Current_Sweep_Diode_inTriggerTimer(infoSMU,srcSettings,meaSettings,pulseSettings,triggerName)
	-- SMU channel assignment
	local IF_SMU 							= slot[infoSMU[1]].smu[infoSMU[2]]
	IF_SMU.reset()
	-- Source Settings
	IF_SMU.source.func						= IF_SMU.FUNC_DC_CURRENT
	IF_SMU.source.rangei					= srcSettings[4]
	IF_SMU.source.leveli					= 0
	IF_SMU.source.limitv					= srcSettings[5]
	-- Measure Settings
	IF_SMU.measure.rangev					= meaSettings[1]
	IF_SMU.measure.rangei					= srcSettings[4]
	IF_SMU.measure.aperture					= pulseSettings[4]
	IF_SMU.measure.autorangei				= 0
	if meaSettings[2] == true then
		IF_SMU.sense						= IF_SMU.SENSE_4WIRE
	else
		IF_SMU.sense						= IF_SMU.SENSE_2WIRE
	end
	-- Buffer clear
	IF_SMU.defbuffer1.clear()
	IF_SMU.defbuffer1.appendmode			= 1
	IF_SMU.defbuffer2.clear()
	IF_SMU.defbuffer2.appendmode			= 1

	-- Setup multiple trigger timers to handle timing
	-- Pulse period timer settings
	local pulse_period 						= trigger.timer[1]
	pulse_period.delay 						= pulseSettings[1]
	-- Passthrough allows script to continue running
	pulse_period.passthrough 				= true
	pulse_period.count 						= srcSettings[3]
	pulse_period.stimulus 					= trigger.generator[1].EVENT_ID
	-- Measure delay timer settings
	local mdelay_on_pulse 					= trigger.timer[2]
	mdelay_on_pulse.delay 					= pulseSettings[3]
	mdelay_on_pulse.passthrough 			= false
	mdelay_on_pulse.count 					= 1
	mdelay_on_pulse.stimulus 				= pulse_period.EVENT_ID
	-- Pulse width timer settings
	local pulse_width 						= trigger.timer[3]
	pulse_width.delay 						= pulseSettings[2]
	pulse_width.passthrough 				= false
	pulse_width.count 						= 1
	pulse_width.stimulus 					= pulse_period.EVENT_ID

	-- Configure trigger model source for a linear current sweep
	IF_SMU.trigger.source.lineari(srcSettings[1], srcSettings[2], srcSettings[3])
	-- Set trigger model measurements to store in default buffers and measure current/voltage
	IF_SMU.trigger.measure.iv(IF_SMU.defbuffer1,IF_SMU.defbuffer2)

	-- Configure trigger model
	local triggerModel = slot[infoSMU[1]].trigger.model
	triggerModel.create(triggerName)
	-- Wait for event
	triggerModel.addblock.wait(triggerName, "wait_period", pulse_period.EVENT_ID)
	-- Continue to next source level
	triggerModel.addblock.source.action.step(triggerName, "IF_sweep", infoSMU[2])
	-- Wait for measure delay stimulus
	triggerModel.addblock.wait(triggerName, "wait_mdelay", mdelay_on_pulse.EVENT_ID)
	-- Measure iv and store in default buffers
	triggerModel.addblock.measure(triggerName, "VF_measure", infoSMU[2], 1)
	-- Wait for pulse width stimulus
	triggerModel.addblock.wait(triggerName, "wait_width", pulse_width.EVENT_ID)	
	-- Set source to 0
	triggerModel.addblock.source.action.bias(triggerName, "pulse_bias", infoSMU[2])
	-- Repeat for each source level
	triggerModel.addblock.branch.counter(triggerName, "IF_branch", "wait_period", srcSettings[3])
	triggerModel.addblock.source.action.bias(triggerName, "IF_bias", infoSMU[2])

	IF_SMU.source.output = 1
	-- Initiate trigger model, generate trigger event to begin
	triggerModel.initiate(triggerName)
	trigger.generator[1].assert()
	waitcomplete()
	IF_SMU.source.output = 0
	triggerModel.delete(triggerName)	

	-- Read measurement buffers and display
	print("T\t\t IF\t\t VF")
	for j = 1, IF_SMU.defbuffer1.n , 1 do
		print(IF_SMU.defbuffer1.timestamps[j], IF_SMU.defbuffer1[j],IF_SMU.defbuffer2[j])
	end

	-- Check for errors and display
	function errorQUEUE()
		errorqueue_Count = errorqueue.count
		print("Error Queue Count:".. errorqueue_Count)
		if errorqueue_Count > 0 then
		  for i = 1, errorqueue_Count do
			print(i, errorqueue.next())
		  end
		end
	end
end 

-- information of SMU
local slot_no 		= 1
local IF_channel 	= 1
-- Source Settings
local startIF 		= 0
local stopIF 		= 12e-3
local noPoints 		= 101
local rangeI 		= 100e-3
local limitV 		= 3
-- Measure Settings
local measRangeV 	= 6
local remoteSense 	= false
-- Pulse Settings
local pulsePeriod	= 5e-4  -- pulsePeriod should be longer than pulseWidth + mDelay + apertureTime
local pulseWidth	= 3e-4
local mDelay 		= 1e-4
local apertureTime	= 1e-4

local tm_name 		= "TM_diode_pulse"

Pulse_Current_Sweep_Diode_inDelayConstant({slot_no,IF_channel},{startIF,stopIF,noPoints, rangeI, limitV},{measRangeV, remoteSense},{pulsePeriod, pulseWidth, mDelay, apertureTime},tm_name)
--Pulse_Current_Sweep_Diode_inTriggerTimer({slot_no,IF_channel},{startIF,stopIF,noPoints, rangeI, limitV},{measRangeV, remoteSense},{pulsePeriod, pulseWidth, mDelay, apertureTime},tm_name)

errorQUEUE()