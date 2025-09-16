--[[
################################################################################

Script File: Sweep_Voltage_Res.tsp

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
	For the same purpose, SMU support it in run time evironment and in trigger model.
	Upon completion of each test, the data is printed to the TSP Toolkit Console 
	in a format that is suitable for copying and pasting into Microsoft Excel for 
	graphing and analysis.

Required Equipment: 1 Model MP5000 Mainframe 
					1 channel SMU (MSMU Series)
					1 Resistive load

Note:  The functions do not perform any error checking.  It is the user's 
       responsibility to specify settings that are compatible with the 
       instrument model being used, and with its power envelope.
       
Note:  It is the user's responsibility to follow all safety guidelines given in 
       the instrument's Reference Manual.  This is especially critical if 
       voltages in excess of 42VDC will be present in the test circuits.  Such 
       voltage levels are hazardous. 
       
Functions created by this script:
    * DC_Voltage_Sweep_Resistor_RunTimeEnv({slot_no,smu_channel},,{startV,stopV,noPoints,limitI},{measRangeV, measRangeI, autoRangeI, nplc,mDelay,remoteSense})
    * DC_Voltage_Sweep_Resistor_inTriggerModel({slot_no,smu_channel},,{startV,stopV,noPoints,limitI},{measRangeV, measRangeI, autoRangeI, nplc,mDelay,remoteSense},tm_name)

Example Usage:
    * DC_Voltage_Sweep_Resistor_RunTimeEnv({1,1},-5,5,101,1,6, 1, 1, 1,0)
	* DC_Voltage_Sweep_Resistor_inTriggerModel({1,1},-5,5,101,1,6, 1, 1, 1,0,"TM_sweepV")
	
################################################################################
--]]
function DC_Voltage_Sweep_Resistor_RunTimeEnv(infoSMU,srcSettings,meaSettings)
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
	sweepV_SMU.measure.nplc					= meaSettings[4]
	sweepV_SMU.sense						= sweepV_SMU.SENSE_2WIRE
	if meaSettings[3] == true then
		sweepV_SMU.measure.autorangei		= 1
	else
		sweepV_SMU.measure.autorangei		= 0
		sweepV_SMU.measure.ranagei			= meaSettings[2]
	end

	if meaSettings[6] == true then
		sweepV_SMU.sense					= sweepV_SMU.SENSE_4WIRE
	else
		sweepV_SMU.sense					= sweepV_SMU.SENSE_2WIRE
	end	
	-- Buffer clear
	sweepV_SMU.defbuffer1.clear()
	sweepV_SMU.defbuffer1.appendmode		= 1
	sweepV_SMU.defbuffer2.clear()
	sweepV_SMU.defbuffer2.appendmode		= 1

	-- Voltage change each cycle
	local deltaV = (srcSettings[2] - srcSettings[1])/ (srcSettings[3] - 1)

	sweepV_SMU.source.output = 1

	-- Iterate through voltage values
	print("V\t\t I\t\t R")
	for j = 1, srcSettings[3] , 1 do
		sweepV_SMU.source.levelv = srcSettings[1] + ((j-1) * deltaV)
		delay(meaSettings[5])
		-- Measure iv and store in default buffers, display results
		sweepV_SMU.measure.iv(sweepV_SMU.defbuffer1, sweepV_SMU.defbuffer2)
		print(sweepV_SMU.defbuffer2[j],sweepV_SMU.defbuffer1[j],(sweepV_SMU.defbuffer2[j]/sweepV_SMU.defbuffer1[j]))
	end

	sweepV_SMU.source.output = 0

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


function DC_Voltage_Sweep_Resistor_inTriggerModel(infoSMU,srcSettings,meaSettings,triggerName)
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
	sweepV_SMU.measure.nplc					= meaSettings[4]
	sweepV_SMU.sense						= sweepV_SMU.SENSE_2WIRE
	if meaSettings[3] == true then
		sweepV_SMU.measure.autorangei		= 1
	else
		sweepV_SMU.measure.autorangei		= 0
		sweepV_SMU.measure.rangei			= meaSettings[2]
	end

	if meaSettings[6] == true then
		sweepV_SMU.sense					= sweepV_SMU.SENSE_4WIRE
	else
		sweepV_SMU.sense					= sweepV_SMU.SENSE_2WIRE
	end	
	-- Buffer clear
	sweepV_SMU.defbuffer1.clear()
	sweepV_SMU.defbuffer1.appendmode		= 1
	sweepV_SMU.defbuffer2.clear()
	sweepV_SMU.defbuffer2.appendmode		= 1

	-- Setup trigger model source levels for linear voltage sweep
	sweepV_SMU.trigger.source.linearv(srcSettings[1], srcSettings[2], srcSettings[3])
	-- Set trigger model iv measurements to store in default buffers
	sweepV_SMU.trigger.measure.iv(sweepV_SMU.defbuffer1,sweepV_SMU.defbuffer2)

	-- Configure trigger model 
	local triggerModel = slot[infoSMU[1]].trigger.model
	triggerModel.create(triggerName)
	-- Step source level to next value in sweep
	triggerModel.addblock.source.action.step(triggerName, "sweepV_IV", infoSMU[2])
	-- Constant delay in trigger model is very accurate
	triggerModel.addblock.delay.constant(triggerName, "IV_delay", meaSettings[5])
	-- Measure iv and store in buffers
	triggerModel.addblock.measure(triggerName, "measure_IV", infoSMU[2], 1)
	-- Loop for each value in sweep
	triggerModel.addblock.branch.counter(triggerName, "branch-counter", "sweepV_IV", srcSettings[3])

	sweepV_SMU.source.output = 1

	-- Initiate trigger model and delete when complete
	triggerModel.initiate(triggerName)
	waitcomplete()
	sweepV_SMU.source.output = 0
	triggerModel.delete(triggerName)

	-- Read measurement buffers and display
	print("V\t\t I\t\t R")
	for j = 1, sweepV_SMU.defbuffer1.n , 1 do
		print(sweepV_SMU.defbuffer2[j],sweepV_SMU.defbuffer1[j],(sweepV_SMU.defbuffer2[j]/sweepV_SMU.defbuffer1[j]))
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
local measRangeI	= 100e-3
local autoRangeI 	= true
local nplc 			= 1
local mDelay 		= 0
local remoteSense 	= false

local tm_name		= "TM_sweepV"

-- DC_Voltage_Sweep_Resistor_RunTimeEnv({slot_no, sweepV_channel},{startV,stopV,noPoints,limitI},{measRangeV, measRangeI, autoRangeI, nplc,mDelay,remoteSense})

-- Trigger model is used for greater accuracy
DC_Voltage_Sweep_Resistor_inTriggerModel({slot_no, sweepV_channel},{startV,stopV,noPoints,limitI},{measRangeV, measRangeI, autoRangeI, nplc,mDelay,remoteSense},tm_name)
errorQUEUE()