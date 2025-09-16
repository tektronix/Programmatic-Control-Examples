--[[
################################################################################

Script File: Sweep_Current_Diode.tsp

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
	Upon completion of each test, the data is printed to the TSP Toolkit Console 
	in a format that is suitable for copying and pasting into Microsoft Excel for 
	graphing and analysis.

Required Equipment: 1 Model MP5000 Mainframe 
					1 channel SMU (MSMU Series)
					1 Diode

Note:  The functions do not perform any error checking.  It is the user's 
       responsibility to specify settings that are compatible with the 
       instrument model being used, and with its power envelope.
       
Note:  It is the user's responsibility to follow all safety guidelines given in 
       the instrument's Reference Manual.  This is especially critical if 
       voltages in excess of 42VDC will be present in the test circuits.  Such 
       voltage levels are hazardous. 
       
Functions created by this script:
    * DC_Current_Sweep_Diode_RunTimeEnv({slot_no,IF_channel},{startIF, stopIF,noPoints, rangeI, limitV}, {measRangeV,nplc,mDelay,remoteSense})
    * DC_Current_Sweep_Diode_inTriggerModel({slot_no,IF_channel},{startIF, stopIF,noPoints, rangeI, limitV}, {measRangeV,nplc,mDelay,remoteSense},triggerName)

Example Usage:
    * DC_Current_Sweep_Diode_RunTimeEnv({1,1},{0,300e-3,31 , 1000e-3, 6}, {6, 1, 0, false})
	* DC_Current_Sweep_Diode_inTriggerModel({1,1},{0,300e-3,31, 1000e-3, 6}, {6, 1, 0,false},"TM_Diode")
################################################################################
--]]

function DC_Current_Sweep_Diode_RunTimeEnv(infoSMU,srcSettings,meaSettings)
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
	IF_SMU.measure.nplc						= meaSettings[2]
	IF_SMU.measure.autorangei				= 1
	if meaSettings[4] == true then
		IF_SMU.sense						= IF_SMU.SENSE_4WIRE
	else
		IF_SMU.sense						= IF_SMU.SENSE_2WIRE
	end
	-- Buffer clear
	IF_SMU.defbuffer1.clear()
	IF_SMU.defbuffer1.appendmode			= 1
	IF_SMU.defbuffer2.clear()
	IF_SMU.defbuffer2.appendmode			= 1

	-- Current step size
	local deltaIF = (srcSettings[2] - srcSettings[1])/ (srcSettings[3] - 1)
	IF_SMU.source.output = 1

	-- Sweep through current values
	print("IF\t\t VF")
	for j = 1, srcSettings[3] , 1 do
		-- Set current level
		IF_SMU.source.leveli = srcSettings[1] + ((j-1) * deltaIF)
		-- Timing is handled with a runtime delay() will be less accurate than a trigger model
		delay(meaSettings[3])
		-- Measure current/voltage and store in default buffers
		IF_SMU.measure.iv(IF_SMU.defbuffer1, IF_SMU.defbuffer2)
		-- Display last readings
		print(IF_SMU.defbuffer1[j],IF_SMU.defbuffer2[j])
	end

	IF_SMU.source.output = 0

	-- Check for and display errors
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

function DC_Current_Sweep_Diode_inTriggerModel(infoSMU,srcSettings,meaSettings,triggerName)
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
	IF_SMU.measure.nplc						= meaSettings[2]
	IF_SMU.measure.autorangei				= 1
	if meaSettings[4] == true then
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
	-- Set trigger model current and voltage measurements to be stored in the default buffers
	IF_SMU.trigger.measure.iv(IF_SMU.defbuffer1,IF_SMU.defbuffer2)

	-- Configure trigger model
	local triggerModel = slot[infoSMU[1]].trigger.model
	triggerModel.create(triggerName) 
	-- Set source level to next value in linear current sweep
	triggerModel.addblock.source.action.step(triggerName, "IF_sweep", infoSMU[2])
	-- Delay handled in trigger model, very accurate
	triggerModel.addblock.delay.constant(triggerName, "IF_delay", meaSettings[3])
	-- Measure iv and store in default buffers
	triggerModel.addblock.measure(triggerName, "VF_measure", infoSMU[2], 1)
	-- Loop for a set number of iterations
	triggerModel.addblock.branch.counter(triggerName, "IF_branch", "IF_sweep", srcSettings[3])
	-- Return source to 0
	triggerModel.addblock.source.action.bias(triggerName, "IF_bias", infoSMU[2])


	IF_SMU.source.output = 1
	-- Initiate trigger model, delete when done
	triggerModel.initiate(triggerName)
	waitcomplete()
	IF_SMU.source.output = 0
	triggerModel.delete(triggerName)	

	-- Display data from measurement buffers
	print("IF\t\t VF")
	for j = 1, IF_SMU.defbuffer1.n , 1 do
		print(IF_SMU.defbuffer1[j],IF_SMU.defbuffer2[j])
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
local stopIF 		= 300e-3
local noPoints 		= 31
local rangeI 		= 1000e-3
local limitV 		= 6
-- Measure Settings
local measRangeV 	= 6
local nplc 			= 1
local mDelay 		= 0
local remoteSense 	= false

local tm_name		= "TM_Diode"

--DC_Current_Sweep_Diode_RunTimeEnv({slot_no,IF_channel},{startIF,stopIF,noPoints, rangeI, limitV},{measRangeV,nplc,mDelay, remoteSense})

-- Trigger model is used by default for greater accuracy
DC_Current_Sweep_Diode_inTriggerModel({slot_no,IF_channel},{startIF,stopIF,noPoints, rangeI, limitV},{measRangeV,nplc,mDelay, remoteSense},tm_name)

errorQUEUE()