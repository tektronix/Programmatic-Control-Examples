
--[[
################################################################################

Script File: LED_Sequence.tsp

    ************************************************************************
    *** Copyright Tektronix, Inc.                                        ***
    *** See www.tek.com/sample-license for licensing terms.              ***
    ************************************************************************

Description:
    This script is example code, which creates (and subsequently calls) several
    functions that can be used with the Model MP5000 Based SMUs to perform a
	current sweeping. The purpose is show that you can perform a LED device
	with the SMU. As written, one channel of SMU is assigned to the anode for 
	the high and cathode for the low terminal. This script shows the benefit of
	configlist feature. All the attributes of source and measurement are configured
	in configlist prior to the trigger. Then trigger recalls the configlist and run.
	This feature gives a lot of convience and speed in LED sequence test. 
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
    * LED_SequenceTest_MSMU_MP5000({IF_slot,IF_channel},{"tm_led","cl_led"})
Example Usage:
   	* LED_SequenceTest_MSMU_MP5000({1,1},{"tm_led","cl_led"})

################################################################################
--]]


function LED_SequenceTest_MSMU_MP5000(infoSMU,triggerSettings)
	local smu_ID = slot[infoSMU[1]].smu[infoSMU[2]]
	local triggerName = triggerSettings[1]
	local configName = triggerSettings[2]

	local test_items = {}
	-- test_items stores the various settings to create a config list
	--             Mode,   srcBias,   srcRng,   mDelay,  mTime,    Limit,      mRng
	test_items[1]  = {0, 0.000001,  0.00001,     0.01,    0.001, 	    1,        6}
	test_items[2]  = {0,  0.00001,   0.0001,    0.005,    0.001,   		3,        6}
	test_items[3]  = {0,   	 0.35,        1,    0.001,    0.001,	    5,        6}
	test_items[4]  = {1,   	   -7,       20,    0.005,    0.001,  0.00005,    0.001}
	test_items[5]  = {0, 0.000001,  0.00001,    0.003,    0.001, 	    1,        6}
	test_items[6]  = {0,    0.350,        1,    0.003,    0.001,       10,       20}
	test_items[7]  = {0, 0.000001,  0.00001,    0.003,    0.001, 	    1,        6}
	test_items[8]  = {1, 	  -40,       60,     0.01,   0.0001,   0.0005,     0.01}
	test_items[9]  = {1, 	  -20,       20,     0.01,   0.0001,   0.0005,     0.01}
	test_items[10] = {0,  0.00001,   0.0001,    0.003,    0.001, 	    3,        6}
	test_items[11] = {0,    0.030,        1,    0.003,    0.001,   	   10,       20}
	test_items[12] = {0,  0.00001,   0.0001,    0.003,    0.001, 	    3,        6}
	test_items[13] = {1,      -24,       60,    0.005,   0.0001,    0.005,    0.001}
	test_items[14] = {1,       -7,       20,    0.005,   0.0001,    0.005,    0.001}
	test_items[15] = {0, 0.000001,  0.00001,     0.01,    0.001, 	    1,        6}
	test_items[16] = {0,  0.00001,   0.0001,    0.005,    0.001,   		3,        6}
	test_items[17] = {0,   	 0.35,        1,    0.001,    0.001,	    5,        6}
	test_items[18] = {1,        7,       20,    0.005,   0.0001,    0.005,    0.001}

	-- Initialize SMU
	function initSMU()
		smu_ID.reset()
		smu_ID.source.func = smu_ID.OUTPUT_DCVOLTS
		smu_ID.source.rangev = 20
		smu_ID.source.levelv = 0
		smu_ID.source.limiti = 1e-6

		smu_ID.measure.rangei = 1e-6
		smu_ID.measure.rangev = 20
		smu_ID.measure.aperture = 5e-3
		smu_ID.defbuffer1.clear()
		smu_ID.defbuffer2.clear()
	end

	-- Create a configlist from the table
	function setConfiglist()
		seqCount = table.getn(test_items)
		local seqTable
		-- Create configlist
		smu_ID.configlist.create(configName)

		for i = 1, seqCount do
			seqTable = test_items[i]
			-- Setup SMU with settings from table
			if seqTable[1] == 0 then
				smu_ID.source.func = smu_ID.FUNC_DC_CURRENT
				smu_ID.source.rangei =  seqTable[3]  
				smu_ID.source.leveli = seqTable[2]
				smu_ID.source.limitv = seqTable[6]
		
				smu_ID.measure.rangev = seqTable[7]
				smu_ID.measure.rangei = seqTable[3]
				smu_ID.measure.delay = seqTable[4]
				smu_ID.measure.aperture = seqTable[5]
		
			elseif seqTable[1] == 1 then
				smu_ID.source.func = smu_ID.OUTPUT_DCVOLTS
				smu_ID.source.rangev =  seqTable[3]  
				smu_ID.source.levelv = seqTable[2] 
				smu_ID.source.limiti = seqTable[6] 
		
				smu_ID.measure.rangev = seqTable[3] 
				smu_ID.measure.rangei = seqTable[7] 
				smu_ID.measure.delay = seqTable[4] 
				smu_ID.measure.aperture = seqTable[5]
			end
			-- Store the current settings in configlist at index i
			smu_ID.configlist.store(configName,i)
		end
	end 

	-- Create and initialize trigger model
	function setTriggerModel()
		smu_ID.trigger.measure.iv(smu_ID.defbuffer1,smu_ID.defbuffer2) 
		triggerModel = slot[infoSMU[1]].trigger.model
		triggerModel.create(triggerName)
		-- Set SMU settings to next item in configlist
		triggerModel.addblock.configlist.next(triggerName, "recallBlockName", infoSMU[2], configName)   -- recall configlist which was already configured
		-- Take i/v measurements
		triggerModel.addblock.measure(triggerName, "measBlockname", infoSMU[2],1)                        -- make measurement with configured condition
		-- Loop through all items in configlist
		triggerModel.addblock.branch.counter(triggerName, "branch-counter", "recallBlockName", seqCount)    -- re-interate recalling the configlist list recall
	end

	-- Execute test
	setConfiglist()
	setTriggerModel()
	initSMU()

	smu_ID.source.levelv = 0
	smu_ID.source.output = 1

	triggerModel.initiate(triggerName)
	waitcomplete()

	print("Test Done")
	smu_ID.source.output = 0

	triggerModel.delete(triggerName)
	smu_ID.configlist.delete(triggerSettings[2])

	-- Display measurements from default buffers
	print("Current\t\t Voltage")
	for j = 1, smu_ID.defbuffer1.n , 1 do
		print(smu_ID.defbuffer1[j],smu_ID.defbuffer2[j])
	end

end

-- information of SMU
local IF_slot 		= 1
local IF_channel 	= 1

LED_SequenceTest_MSMU_MP5000({IF_slot,IF_channel},{"tm_led","cl_led"})