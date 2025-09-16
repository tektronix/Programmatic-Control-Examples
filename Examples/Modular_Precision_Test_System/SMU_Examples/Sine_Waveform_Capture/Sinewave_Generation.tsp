--[[
################################################################################

Script File: Sinewave_Generation.tsp

    ************************************************************************
    *** Copyright Tektronix, Inc.                                        ***
    *** See www.tek.com/sample-license for licensing terms.              ***
    ************************************************************************

Description:
    This script is example code, which creates (and subsequently calls) several
    functions that can be used with the Model MP5000 Based SMUs to perform a
	current sweeping. The purpose is show that you can make a sine waveform in output
	As written, one channel of SMU is assigned to the high and the other to the low 
	terminal. The script shows fast changing source bias to be enough to make a sine. 
	For the same purpose, SMU support it in run time evironment and in trigger model.
	Upon completion of each test, the data is printed to the TSP Toolkit Console 
	in a format that is suitable for copying and pasting into Microsoft Excel for 
	graphing and analysis.

Required Equipment: 1 Model MP5000 Mainframe 
					1 channel SMU (MSMU Series)
					1 Resistor

Note:  The functions do not perform any error checking.  It is the user's 
       responsibility to specify settings that are compatible with the 
       instrument model being used, and with its power envelope.
       
Note:  It is the user's responsibility to follow all safety guidelines given in 
       the instrument's Reference Manual.  This is especially critical if 
       voltages in excess of 42VDC will be present in the test circuits.  Such 
       voltage levels are hazardous. 
       
Functions created by this script:
    * Sine_Waveform_Generate_MSMU_MP5000(noSlot, noCh, Vrms, numCycles, frequency, limitI,triggerName)
 
Example Usage:
    * Sine_Waveform_Generate_MSMU_MP5000(1, 1, 5, 5, 60, 0.1,"tm_sine")
	
################################################################################
--]]

function Sine_Waveform_Generate_MSMU_MP5000(noSlot, noCh, Vrms, numCycles, frequency, limitI,triggerName)
	-- SMU alias
	local smu_ID = slot[noSlot].smu[noCh]
	-- Calculate sinewave values
	local Vpp				= Vrms * math.sqrt(2)
	local sourceValues		= {} 
	local pointsPerCycle	= 7200 / frequency
    local timeInterval      = 1/7200
	local numDataPoints		= pointsPerCycle * numCycles
	local numReadings
	-- Generate voltage sweep values
	for i=1, numDataPoints do
		sourceValues[i]		= (Vpp * math.sin(i * 2 * math.pi / pointsPerCycle))
	end
	-- Create reading buffers
	numReadings = 280 * numCycles
	smu_ID.reset()
	readingBuffer1 = smu_ID.makebuffer(5000)
	readingBuffer2 = smu_ID.makebuffer(5000)

	-- Configure channel settings
	smu_ID.source.func = smu_ID.FUNC_DC_VOLTAGE
	smu_ID.source.autorangev = smu_ID.OFF
	smu_ID.source.rangev = 20
	smu_ID.source.limiti = limitI
	smu_ID.source.levelv = 0
	smu_ID.source.output = 1
	smu_ID.measure.aperture = 0.0001
	smu_ID.measure.rangei = 100e-3
	smu_ID.measure.rangev = 20

	-- Configure sweep voltage list
	smu_ID.trigger.source.listv(sourceValues)
	-- Set trigger model readings for i/v and store in reading buffers
	smu_ID.trigger.measure.iv(readingBuffer1,readingBuffer2) 

	-- Configure trigger model
	local triggermodel = slot[noSlot].trigger.model
	triggermodel.create(triggerName) 
	-- Measure overlapped allows for readings to happen while triggermodel is excecuting in parallel
	triggermodel.addblock.measureoverlapped(triggerName, "measure3", noCh, numReadings)
	triggermodel.addblock.delay.constant(triggerName, "delay-init", 2e-3)
	-- Advance through voltage sweep
	triggermodel.addblock.source.action.step(triggerName, "sweep_step1",noCh)
	triggermodel.addblock.delay.constant(triggerName, "delay-on2", timeInterval,"sweep_step1")
	-- Loop through all voltage values
	triggermodel.addblock.branch.counter(triggerName, "branch-counter7", "sweep_step1", numDataPoints)

	-- Initiate trigger model and delete when finished
	smu_ID.source.output = 1
	triggermodel.initiate(triggerName)
	waitcomplete()
	smu_ID.source.output = 0
	triggermodel.delete(triggerName)

	-- Display results from reading buffers
	print("Time\t\t V\t\t I")
	for j = 1, readingBuffer1.n , 1 do
		print(readingBuffer1.timestamps[j],readingBuffer2[j],readingBuffer1[j])
	end

end
-- SMU channel Settings
local slot_no 		= 1
local smu_channel 	= 1
-- AC input parameters
local Vrms			= 5
local numCycles 	= 3
local frequency		= 60
local limitI		= 100e-3

local tm_name 		= "tm_sine"

Sine_Waveform_Generate_MSMU_MP5000(slot_no, smu_channel, Vrms, numCycles, frequency, limitI,tm_name)

print(readingBuffer1)
