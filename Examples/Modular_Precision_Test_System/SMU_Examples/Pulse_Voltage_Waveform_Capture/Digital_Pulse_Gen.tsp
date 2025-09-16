--[[
################################################################################

Script File: Pulse_Waveform_Capture_MSMU_MP5000.tsp

    ************************************************************************
    *** Copyright Tektronix, Inc.                                        ***
    *** See www.tek.com/sample-license for licensing terms.              ***
    ************************************************************************

Description:
    This script is example code, which creates (and subsequently calls) several
    functions that can be used with the Model MP5000 Based SMUs to perform a
	voltage sweeping. The purpose is show that you can make digitiazer for pulse train
	As written, one channel of SMU is assigned to the high and the other to the low 
	terminal. The script generates voltage pulses measuring voltage and current with
	digitizers at a same time. 
	For the same purpose, SMU support is in run time evironment and in trigger model.
	Upon completion of each test, the data is printed to the TSP Toolkit Console 
	in a format that is suitable for copying and pasting into Microsoft Excel for 
	graphing and analysis.

Required Equipment: 1 Model MP5000 Mainframe 
					1 channel SMU 

Note:  The functions do not perform any error checking.  It is the user's 
       responsibility to specify settings that are compatible with the 
       instrument model being used, and with its power envelope.
       
Note:  It is the user's responsibility to follow all safety guidelines given in 
       the instrument's Reference Manual.  This is especially critical if 
       voltages in excess of 42VDC will be present in the test circuits.  Such 
       voltage levels are hazardous. 
       
Functions created by this script:
    * Pulse_Waveform_Capture_MSMU_MP5000({slot_no, sweepV_channel},{startV,stopV,noPoints,limitI},{measRangeV, measRangeI, remoteSense}, {pulsePeriod, pulseWidth, mDelay,apertureTime},tm_name)
Example Usage:
    * Pulse_Waveform_Capture_MSMU_MP5000({1, 1},{1,10,10,0.1},{10, 0.1, false}, {5e-3, 3e-3, 1e-3,1e-3},"tm_pulse_digitizer")
	
################################################################################
--]]

function Pulse_Waveform_Capture_MSMU_MP5000(infoSMU,srcSettings,meaSettings,pulseSettings,triggerName)
	-- SMU channel assignment
	local sweepV_SMU 						    = slot[infoSMU[1]].smu[infoSMU[2]]
	sweepV_SMU.reset()
	-- Source Settings
	sweepV_SMU.source.func					    = sweepV_SMU.FUNC_DC_VOLTAGE
	sweepV_SMU.source.rangev				    =  math.max(math.abs(srcSettings[1]), math.abs(srcSettings[2]))
	sweepV_SMU.source.limiti				    = srcSettings[4]
	sweepV_SMU.source.levelv 				    = 0
	-- Measure Settings
	sweepV_SMU.measure.rangev				    = meaSettings[1]
	sweepV_SMU.measure.rangei				    = meaSettings[2]
	sweepV_SMU.measure.aperture			    	= pulseSettings[4]
	sweepV_SMU.sense						    = sweepV_SMU.SENSE_2WIRE
	sweepV_SMU.measure.autorangei		    	= 0

	if meaSettings[3] == true then
		sweepV_SMU.sense					    = sweepV_SMU.SENSE_4WIRE
	else
		sweepV_SMU.sense					    = sweepV_SMU.SENSE_2WIRE
	end	
	-- Buffer clear
	sweepV_SMU.defbuffer1.clear()
	sweepV_SMU.defbuffer1.appendmode    		= 1
	sweepV_SMU.defbuffer2.clear()
	sweepV_SMU.defbuffer2.appendmode			= 1
	-- Calculate number of points
  	local nPoints = math.ceil(((pulseSettings[1] * srcSettings[3]) + pulseSettings[1]) / pulseSettings[4])
	
	-- Configure trigger model source for linear voltage sweep
	sweepV_SMU.trigger.source.linearv(srcSettings[1], srcSettings[2], srcSettings[3])
	-- Set trigger model to measure i/v and store in default buffers
	sweepV_SMU.trigger.measure.iv(sweepV_SMU.defbuffer1,sweepV_SMU.defbuffer2)

	-- Configure trigger model 
	local triggerModel = slot[infoSMU[1]].trigger.model
	triggerModel.create(triggerName) 
	-- Measureoverlapped allows measurements to be taken while trigger model is running in parallel
	triggerModel.addblock.measureoverlapped(triggerName, "measure_IV", infoSMU[2], nPoints)
  	triggerModel.addblock.delay.constant(triggerName, "prepulse_delay", pulseSettings[1]/2)
	-- Advance to next voltage value in voltage sweep
	triggerModel.addblock.source.action.step(triggerName, "sweepV_IV", infoSMU[2])
	triggerModel.addblock.delay.constant(triggerName, "meas_pulse_width", pulseSettings[2],"sweepV_IV")
	-- Set source level to 0
	triggerModel.addblock.source.action.bias(triggerName, "pulse_bias", infoSMU[2])
	triggerModel.addblock.delay.constant(triggerName, "meas_pulse_period", pulseSettings[1],"sweepV_IV")
	-- Loop through all voltage sweep values
	triggerModel.addblock.branch.counter(triggerName, "branch-counter", "sweepV_IV", srcSettings[3])
  	triggerModel.addblock.delay.constant(triggerName, "postpulse_delay", pulseSettings[1]) 

	-- Initiate trigger model, delete when finished
	sweepV_SMU.source.output = 1
	triggerModel.initiate(triggerName)
	waitcomplete()
	sweepV_SMU.source.output = 0
	triggerModel.delete(triggerName)
  
	-- Retrieve values from buffers and display
	print("Time\t\t V\t\t I")
	for j = 1, sweepV_SMU.defbuffer1.n , 1 do
		print(sweepV_SMU.defbuffer1.timestamps[j],sweepV_SMU.defbuffer2[j],sweepV_SMU.defbuffer1[j])
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
local slot_no 		  	= 1
local sweepV_channel	= 1
-- Source Settings
local startV 		    = 1
local stopV 		    = 10
local noPoints 	    	= 10
local limitI 		    = 1
-- Measure Settings
local measRangeV    	= 10
local measRangeI    	= 1
local remoteSense 		= false

-- Pulse Settings
local pulsePeriod	  	= 5e-3  -- pulsePeriod should be longer than pulseWidth + mDelay + apertureTime
local pulseWidth	  	= 3e-3
local mDelay 		    = 1e-3
local apertureTime		= 100e-6

local tm_name			= "TM_pulse_digitizer"

Pulse_Waveform_Capture_MSMU_MP5000({slot_no, sweepV_channel},{startV,stopV,noPoints,limitI},{measRangeV, measRangeI, remoteSense}, {pulsePeriod, pulseWidth, mDelay,apertureTime},tm_name)
