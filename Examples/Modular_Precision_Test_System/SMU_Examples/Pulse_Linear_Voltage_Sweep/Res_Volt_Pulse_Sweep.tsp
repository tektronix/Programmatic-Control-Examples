--[[
################################################################################

Script File: Res_Volt_Pulse_Sweep.tsp

    ************************************************************************
    *** Copyright Tektronix, Inc.                                        ***
    *** See www.tek.com/sample-license for licensing terms.              ***
    ************************************************************************

Description:
    This script is example code, which creates (and subsequently calls) several
    functions that can be used with the Model MP5000 Based SMUs to perform a
	voltage sweeping. The purpose is show that you can perform a resistor 
	device characterization with the SMUs. As written, one channel of SMU is 
	assigned to one terminal for the high and the other for the low terminal.
	This pulse test should be excuted in trigger model. the first script shows
	how much accurate the delay constance with reference makes pulse. 
	The second script shows how to make pulse with trigger timer object. 
	Upon completion of each test, the data is printed to the TSP Toolkit Console 
	in a format that is suitable for copying and pasting into Microsoft Excel for 
	graphing and analysis.

Required Equipment: 1 Model MP5000 Mainframe 
					1 channel SMU 
					1 Resistor

Note:  The functions do not perform any error checking.  It is the user's 
       responsibility to specify settings that are compatible with the 
       instrument model being used, and with its power envelope.
       
Note:  It is the user's responsibility to follow all safety guidelines given in 
       the instrument's Reference Manual.  This is especially critical if 
       voltages in excess of 42VDC will be present in the test circuits.  Such 
       voltage levels are hazardous. 
       
Functions created by this script:
    * DC_Voltage_Sweep_Resistor_RunTimeEnv({slot_no,smu_channel},,{startV,stopV,noPoints,limitI},{measRangeV, measRangeI, autoRangeI, nplc,mDelay,remoteSense},tm_name)
    * DC_Voltage_Sweep_Resistor_inTriggerModel({slot_no,smu_channel},,{startV,stopV,noPoints,limitI},{measRangeV, measRangeI, autoRangeI, nplc,mDelay,remoteSense},tm_name)

Example Usage:
    * DC_Voltage_Sweep_Resistor_RunTimeEnv({1,1},-5,5,101,1,6, 1, 1, 1,0,"TM_sweepV_pulse")
	* DC_Voltage_Sweep_Resistor_inTriggerModel({1,1},-5,5,101,1,6, 1, 1, 1,0,"TM_sweepV_pulse")
	
################################################################################
--]]

function Pulse_Voltage_Sweep_Resistor_inDelayConstant(infoSMU,srcSettings,meaSettings,pulseSettings,triggerName)
	-- SMU channel assignment
	local sweepV_SMU 						= slot[infoSMU[1]].smu[infoSMU[2]]
	sweepV_SMU.reset()
	-- Source Settings
	sweepV_SMU.source.func					= sweepV_SMU.FUNC_DC_VOLTAGE
	sweepV_SMU.source.rangev				=  math.max(math.abs(srcSettings[1]), math.abs(srcSettings[2]))
	sweepV_SMU.source.limiti				= srcSettings[4]
	sweepV_SMU.source.levelv 				= 0
	-- Measure Settings
	sweepV_SMU.measure.rangev				= meaSettings[1]
	sweepV_SMU.measure.rangei				= meaSettings[2]
	sweepV_SMU.measure.aperture				= pulseSettings[4]
	sweepV_SMU.sense						= sweepV_SMU.SENSE_2WIRE
	sweepV_SMU.measure.autorangei			= 0
	if meaSettings[3] == true then
		sweepV_SMU.sense					= sweepV_SMU.SENSE_4WIRE
	else
		sweepV_SMU.sense					= sweepV_SMU.SENSE_2WIRE
	end	
	-- Buffer clear
	sweepV_SMU.defbuffer1.clear()
	sweepV_SMU.defbuffer1.appendmode		= 1
	sweepV_SMU.defbuffer2.clear()
	sweepV_SMU.defbuffer2.appendmode		= 1

	-- Setup trigger model source for linear voltage sweep
	sweepV_SMU.trigger.source.linearv(srcSettings[1], srcSettings[2], srcSettings[3])
	-- Set trigger model measurements to store in default buffers and measure voltage/current
	sweepV_SMU.trigger.measure.iv(sweepV_SMU.defbuffer1,sweepV_SMU.defbuffer2)

	-- Configure trigger model 
	local triggerModel = slot[infoSMU[1]].trigger.model
	triggerModel.create(triggerName)
	-- Step to next voltage value in sweep
	triggerModel.addblock.source.action.step(triggerName, "sweepV_IV", infoSMU[2])
	triggerModel.addblock.delay.constant(triggerName, "meas_delay", pulseSettings[3])
	-- Measure iv and store in buffers
	triggerModel.addblock.measure(triggerName, "measure_IV", infoSMU[2], 1)
	triggerModel.addblock.delay.constant(triggerName, "meas_pulse_width", pulseSettings[2],"sweepV_IV")
	-- Set source back to 0
	triggerModel.addblock.source.action.bias(triggerName, "pulse_bias", infoSMU[2])
	triggerModel.addblock.delay.constant(triggerName, "meas_pulse_period", pulseSettings[1],"sweepV_IV")
	-- Loop through all sweep values
	triggerModel.addblock.branch.counter(triggerName, "branch-counter", "sweepV_IV", srcSettings[3])

	-- Initiate trigger model and delete when completed
	sweepV_SMU.source.output = 1
	triggerModel.initiate(triggerName)
	waitcomplete()
	sweepV_SMU.source.output = 0
	triggerModel.delete(triggerName)

	-- Display measurement buffer contents
	print("V\t\t I\t\t R")
	for j = 1, sweepV_SMU.defbuffer1.n , 1 do
		print(sweepV_SMU.defbuffer2[j],sweepV_SMU.defbuffer1[j],(sweepV_SMU.defbuffer2[j]/sweepV_SMU.defbuffer1[j]))
	end

	-- Display all errors
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

function Pulse_Voltage_Sweep_Resistor_inTriggerTimer(infoSMU,srcSettings,meaSettings,pulseSettings,triggerName)
	-- SMU channel assignment
	local sweepV_SMU 						= slot[infoSMU[1]].smu[infoSMU[2]]
	sweepV_SMU.reset()
	-- Source Settings
	sweepV_SMU.source.func					= sweepV_SMU.FUNC_DC_VOLTAGE
	sweepV_SMU.source.rangev				=  math.max(math.abs(srcSettings[1]), math.abs(srcSettings[2]))
	sweepV_SMU.source.limiti				= srcSettings[4]
	sweepV_SMU.source.levelv 				= 0
	-- Measure Settings
	sweepV_SMU.measure.rangev				= meaSettings[1]
	sweepV_SMU.measure.rangei				= meaSettings[2]
	sweepV_SMU.measure.aperture				= pulseSettings[4]
	sweepV_SMU.sense						= sweepV_SMU.SENSE_2WIRE
	sweepV_SMU.measure.autorangei			= 0
	if meaSettings[3] == true then
		sweepV_SMU.sense					= sweepV_SMU.SENSE_4WIRE
	else
		sweepV_SMU.sense					= sweepV_SMU.SENSE_2WIRE
	end	
	-- Buffer clear
	sweepV_SMU.defbuffer1.clear()
	sweepV_SMU.defbuffer1.appendmode		= 1
	sweepV_SMU.defbuffer2.clear()
	sweepV_SMU.defbuffer2.appendmode		= 1

	-- Pulse period timer settings
	local pulse_period 						= trigger.timer[1]
	pulse_period.delay 						= pulseSettings[1]
	-- Passthrough allows for script to continue running
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

	-- Setup trigger model source for linear voltage sweep
	sweepV_SMU.trigger.source.linearv(srcSettings[1], srcSettings[2], srcSettings[3])
	-- Setup measurements to store in default buffers and measure current/voltage
	sweepV_SMU.trigger.measure.iv(sweepV_SMU.defbuffer1,sweepV_SMU.defbuffer2)

	-- Configure trigger model 
	local triggerModel = slot[infoSMU[1]].trigger.model
	triggerModel.create(triggerName) 
	-- Wait for event from pulse period timer
	triggerModel.addblock.wait(triggerName, "wait_period", pulse_period.EVENT_ID)
	-- Advance to next source level in sweep
	triggerModel.addblock.source.action.step(triggerName, "sweepV_IV", infoSMU[2])
	-- Wait for event from mdelay
	--triggerModel.addblock.delay.constant(triggerName, "delay", pulseSettings[3], "sweepV_IV")
	triggerModel.addblock.wait(triggerName, "wait_mdelay", mdelay_on_pulse.EVENT_ID)
	-- Measure current/voltage
	triggerModel.addblock.measure(triggerName, "measure_IV", infoSMU[2], 1)
	-- Wait for event from pulse_width
	triggerModel.addblock.wait(triggerName, "wait_width", pulse_width.EVENT_ID)
	triggerModel.addblock.source.action.bias(triggerName, "pulse_bias", infoSMU[2])
	-- Loop through all voltage values in sweep
	triggerModel.addblock.branch.counter(triggerName, "branch-counter", "wait_period", srcSettings[3])

	-- Initiate trigger model, delete when finished
	sweepV_SMU.source.output = 1
	triggerModel.initiate(triggerName)
	trigger.generator[1].assert()
	waitcomplete()
	sweepV_SMU.source.output = 0
	triggerModel.delete(triggerName)

	-- Read and display measurement buffers
	print("V\t\t I\t\t R")
	for j = 1, sweepV_SMU.defbuffer1.n , 1 do
		print(sweepV_SMU.defbuffer2[j],sweepV_SMU.defbuffer1[j],(sweepV_SMU.defbuffer2[j]/sweepV_SMU.defbuffer1[j]))
	end

	-- Display all errors
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

-- SMU channel Settings
local slot_no 		= 1
local sweepV_channel= 1
-- Source Settings
local startV 		= -5
local stopV 		= 5
local noPoints 		= 101
local limitI 		= 1
-- Measure Settings
local measRangeV 	= 6
local measRangeI	= 1
local remoteSense 	= false
-- Pulse Settings
local pulsePeriod	= 5e-3  -- pulsePeriod should be longer than pulseWidth + mDelay + apertureTime
local pulseWidth	= 3e-3
local mDelay 		= 1e-3
local apertureTime	= 1e-3

local tm_name		= "TM_sweepV_pulse"

Pulse_Voltage_Sweep_Resistor_inDelayConstant({slot_no, sweepV_channel},{startV,stopV,noPoints,limitI},{measRangeV, measRangeI, remoteSense}, {pulsePeriod, pulseWidth, mDelay, apertureTime},tm_name)
--Pulse_Voltage_Sweep_Resistor_inTriggerTimer({slot_no, sweepV_channel},{startV,stopV,noPoints,limitI},{measRangeV, measRangeI, remoteSense}, {pulsePeriod, pulseWidth, mDelay, apertureTime},tm_name)