--[[
################################################################################

Script File: BJT_Gummel_Vblc.tsp

    ************************************************************************
    *** Copyright Tektronix, Inc.                                        ***
    *** See www.tek.com/sample-license for licensing terms.              ***
    ************************************************************************

Description:
    This script is example code, which creates (and subsequently calls) several
    functions that can be used with the Model MP5000 Based SMUs to perform a
	gummel curve test for n-type bipolar junction transitor devices. 
	The purpose is show that you can perform the semiductor device gummel characterization 
	with the SMUs As written, two channels of SMU are assigned to the collector/base. 
	LOs from the two channels are tied together to emitter. There are three different
	scripts for the same test. One is operation in run time environment, the other
	is single trigger model for both channels in the same slot. The third is another trigger
	model example for each channel in different slot or in the same slot in the trigger
	trigger model. 
	Upon completion of each test, the data is printed to the TSP Toolkit Console 
	in a format that is suitable for copying and pasting into Microsoft Excel for 
	graphing and analysis.

Required Equipment: 1 Model MP5000 Mainframe 
					2 channel SMUs 
					1 BJT Transistor

Note:  The functions do not perform any error checking.  It is the user's 
       responsibility to specify settings that are compatible with the 
       instrument model being used, and with its power envelope.
       
Note:  It is the user's responsibility to follow all safety guidelines given in 
       the instrument's Reference Manual.  This is especially critical if 
       voltages in excess of 42VDC will be present in the test circuits.  Such 
       voltage levels are hazardous. 
       
Functions created by this script:
	* Gummel_VbIc_RunTimeEnv({base_slot,base_channel,collecor_slot,collector_channel},{startVbVc,stopVbVc,noSwpPoints,limitIbIc},{nplc,mDelay})
	* Gummel_VbIc_TriggerInOneSlot({common_slot,base_channel,collector_channel},{startVbVc,stopVbVc,noSwpPoints,limitIbIc},{nplc,mDelay},{"tm_vbic"})
	* Gummel_VbIc_TwoTriggers({base_slot,base_channel,collecor_slot,collector_channel},{startVbVc,stopVbVc,noSwpPoints,limitIbIc},{nplc,mDelay},{"tm_base", "tm_collector"})

Example Usage:
	* Gummel_VbIc_RunTimeEnv({base_slot,base_channel,collecor_slot,collector_channel},{startVbVc,stopVbVc,noSwpPoints,limitIbIc},{nplc,mDelay})
	* Gummel_VbIc_TriggerInOneSlot({common_slot,base_channel,collector_channel},{startVbVc,stopVbVc,noSwpPoints,limitIbIc},{nplc,mDelay},{"tm_vbic"})
	* Gummel_VbIc_TwoTriggers({base_slot,base_channel,collecor_slot,collector_channel},{startVbVc,stopVbVc,noSwpPoints,limitIbIc},{nplc,mDelay},{"tm_base", "tm_collector"})
	
################################################################################
--]]
function Gummel_VbIc_RunTimeEnv(infoSMU,bcSMUsettings, meaSettings)
	-- SMU channel assignment
	local baseSMU      							= slot[infoSMU[1]].smu[infoSMU[2]]
	local collectorSMU     							= slot[infoSMU[3]].smu[infoSMU[4]]
	local smu_id 								= {baseSMU,collectorSMU}
	-- Setup both channels for a voltage sweep
	for i = 1, 2 do	
		smu_id[i].reset()
		smu_id[i].source.func					= smu_id[i].FUNC_DC_VOLTAGE
		smu_id[i].sense							= smu_id[i].SENSE_2WIRE
		smu_id[i].source.rangev					= math.max(math.abs(bcSMUsettings[1]), math.abs(bcSMUsettings[2]))
		smu_id[i].source.limiti					= bcSMUsettings[4]
		smu_id[i].source.levelv 				= 0
		smu_id[i].measure.nplc					= meaSettings[1]
		smu_id[i].measure.autorangei			= 1
		smu_id[i].defbuffer1.clear()
		smu_id[i].defbuffer1.appendmode			= 1
		smu_id[i].defbuffer2.clear()
		smu_id[i].defbuffer2.appendmode			= 1
	end
	-- Calculate the change in voltage for both the base and collector
	local deltaVg = (bcSMUsettings[2] - bcSMUsettings[1])/ (bcSMUsettings[3] - 1)
	-- Turn outputs on
	baseSMU.source.output = 1
	baseSMU.source.output = 1
	collectorSMU.source.output = 1
	collectorSMU.source.output = 1

	print("Vb\t\t Ib\t\t Vce\t\t Ic")
	-- Perform voltage sweep on both channels
	for j = 1, bcSMUsettings[3] , 1 do
		-- Increase voltage level on both channels
		collectorSMU.source.levelv = bcSMUsettings[1] + ((j-1) * deltaVg)
		baseSMU.source.levelv = bcSMUsettings[1] + ((j-1) * deltaVg)
		-- Runtime delay
		delay(meaSettings[2])
		-- Measure i/v on both channels and store in default buffers
		baseSMU.measure.iv(baseSMU.defbuffer1, baseSMU.defbuffer2)
		collectorSMU.measure.iv(collectorSMU.defbuffer1, collectorSMU.defbuffer2)
		-- Display results
		print(baseSMU.defbuffer2[j],baseSMU.defbuffer1[j],collectorSMU.defbuffer2[j],collectorSMU.defbuffer1[j])
	end

	baseSMU.source.output = 0
	collectorSMU.source.output = 0

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
	errorQUEUE()
end 

function Gummel_VbIc_TriggerInOneSlot(infoSMU,bcSMUsettings, meaSettings,tmName)
	-- SMU channel assignment
	local baseSMU  								= slot[infoSMU[1]].smu[infoSMU[2]]
	local collectorSMU 							= slot[infoSMU[1]].smu[infoSMU[3]]
	local smu_id        						= {baseSMU,collectorSMU}
	-- Configure both channels for a voltage sweep
	for i = 1, 2 do	
		smu_id[i].reset()
		smu_id[i].source.func					= smu_id[i].FUNC_DC_VOLTAGE
		smu_id[i].sense							= smu_id[i].SENSE_2WIRE
		smu_id[i].source.rangev					= math.max(math.abs(bcSMUsettings[1]), math.abs(bcSMUsettings[2]))
		smu_id[i].source.limiti					= bcSMUsettings[4]
		smu_id[i].source.levelv 				= 0
		smu_id[i].measure.nplc					= meaSettings[1]
		smu_id[i].measure.autorangei			= 1
		smu_id[i].defbuffer1.clear()
		smu_id[i].defbuffer1.appendmode			= 1
		smu_id[i].defbuffer2.clear()
		smu_id[i].defbuffer2.appendmode			= 1
	end

	-- Setup linear voltage sweep for both channels
	collectorSMU.trigger.source.linearv(bcSMUsettings[1], bcSMUsettings[2], bcSMUsettings[3])
	baseSMU.trigger.source.linearv(bcSMUsettings[1], bcSMUsettings[2], bcSMUsettings[3])
	-- Set trigger models to measure i/v and store in default buffers
	baseSMU.trigger.measure.iv(baseSMU.defbuffer1,baseSMU.defbuffer2)
	collectorSMU.trigger.measure.iv(collectorSMU.defbuffer1,collectorSMU.defbuffer2)

--############################################## Trigger model ###############################################--
--############################################################################################################--

	local triggerModel = slot[infoSMU[1]].trigger.model
	triggerModel.create(tmName[1]) 

	-- Advance both channels to the next voltage value														-- Loop 1
	triggerModel.addblock.source.action.step(tmName[1], "collectorVoltage", infoSMU[3])							--##--
	triggerModel.addblock.source.action.step(tmName[1], "baseVoltage", infoSMU[2])								--##--
	triggerModel.addblock.delay.constant(tmName[1],"meaDelay",meaSettings[2])									--##--
	-- Measure i/v																								--##--
	triggerModel.addblock.measure(tmName[1], "measure", infoSMU[2], 1)											--##--
	triggerModel.addblock.measure(tmName[1], "measure2", infoSMU[3], 1)											--##--
	-- Loop for every value in voltage sweeps																	--##--
	triggerModel.addblock.branch.counter(tmName[1], "branch-counter", "collectorVoltage", bcSMUsettings[3])	 --##--
	
--############################################################################################################--

	-- Initiate trigger model, delete when completed 
	baseSMU.source.output = 1
	collectorSMU.source.output = 1
	triggerModel.initiate(tmName[1])
	waitcomplete()
	baseSMU.source.output = 0
	collectorSMU.source.output = 0
	triggerModel.delete(tmName[1])

	-- Display results from buffers
	print("Vb\t\t Ib\t\t Vce\t\t Ic")
	for j = 1, baseSMU.defbuffer1.n , 1 do
		print(baseSMU.defbuffer2[j],baseSMU.defbuffer1[j],collectorSMU.defbuffer2[j],collectorSMU.defbuffer1[j])
	end

	-- Check for errors and dipslay
	function errorQUEUE()
		errorqueue_Count = errorqueue.count
		print("Error Queue Count:".. errorqueue_Count)
		if errorqueue_Count > 0 then
		  for i = 1, errorqueue_Count do
			print(i, errorqueue.next())
		  end
		end
	end
	errorQUEUE()
end 


function Gummel_VbIc_TwoTriggers(infoSMU,bcSMUsettings, meaSettings,tmName)
	-- SMU channel assignment
	local baseSMU       						= slot[infoSMU[1]].smu[infoSMU[2]]
	local collectorSMU      					= slot[infoSMU[3]].smu[infoSMU[4]]
	local smu_id        						= {baseSMU,collectorSMU}
	-- Configure both channels for a voltage sweep
	for i = 1, 2 do	
		smu_id[i].reset()
		smu_id[i].source.func					= smu_id[i].FUNC_DC_VOLTAGE
		smu_id[i].sense							= smu_id[i].SENSE_2WIRE
		smu_id[i].source.rangev					= math.max(math.abs(bcSMUsettings[1]), math.abs(bcSMUsettings[2]))
		smu_id[i].source.limiti					= bcSMUsettings[4]
		smu_id[i].source.levelv 				= 0
		smu_id[i].measure.nplc					= meaSettings[1]
		smu_id[i].measure.autorangei			= 1
		smu_id[i].defbuffer1.clear()
		smu_id[i].defbuffer1.appendmode			= 1
		smu_id[i].defbuffer2.clear()
		smu_id[i].defbuffer2.appendmode			= 1
	end

--############################################ Base Trigger model ############################################--
--############################################################################################################--

	-- Set source values for linear voltage sweep
	baseSMU.trigger.source.linearv(bcSMUsettings[1], bcSMUsettings[2], bcSMUsettings[3])
	-- Set trigger model measurements to i/v and store in default buffers
	baseSMU.trigger.measure.iv(baseSMU.defbuffer1,baseSMU.defbuffer2)

	local trigger_base = slot[infoSMU[1]].trigger.model
	trigger_base.create(tmName[1])

	-- Notify collector model that sweep has begun																-- Loop 1
	trigger_base.addblock.notify(tmName[1],"notifyCollectorStep",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY1)		--##--
	-- Advance source to next voltage value																			--##--
	trigger_base.addblock.source.action.step(tmName[1], "baseVoltage", infoSMU[2])									--##--
	trigger_base.addblock.delay.constant(tmName[1],"meaDelay",meaSettings[2])										--##--
	-- Measure i/v on base																							--##--
	trigger_base.addblock.measure(tmName[1], "measure", infoSMU[2], 1)												--##--
																													--##--
	-- Wait for notification that collector model finished measurement												--##--
	trigger_base.addblock.wait(tmName[1],"waitCollectorStep",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY2 )			--##--
	-- Loop to notify collector model of next iteration																--##--
	trigger_base.addblock.branch.counter(tmName[1], "branch-gate", "notifyCollectorStep", bcSMUsettings[3])		--##--
	-- Notify collector model that voltage sweep has completed
	trigger_base.addblock.notify(tmName[1],"notifySweepDone",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY5)
	trigger_base.addblock.source.action.bias(tmName[1],"basezero", infoSMU[2])

--######################################### Collector Trigger model ##########################################--
--############################################################################################################--

	-- Set source values for linear voltage sweep
	collectorSMU.trigger.source.linearv(bcSMUsettings[1], bcSMUsettings[2], bcSMUsettings[3])
	-- Set trigger model measurements to i/v and store in default buffers
	collectorSMU.trigger.measure.iv(collectorSMU.defbuffer1,collectorSMU.defbuffer2)

	local trigger_collector = slot[infoSMU[3]].trigger.model
	trigger_collector.create(tmName[2])

	-- Wait for notification from base to begin sweep														-- Loop 1
	trigger_collector.addblock.wait(tmName[2],"waitStep",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY1 )			--##--
	-- Advance source to next voltage value																		--##--
	trigger_collector.addblock.source.action.step(tmName[2], "collectorVoltage", infoSMU[4])					--##--
	trigger_collector.addblock.delay.constant(tmName[2],"meaDelay",meaSettings[2])								--##--
	-- Measure i/v on collector																					--##--
	trigger_collector.addblock.measure(tmName[2], "measure", infoSMU[4], 1)										--##--
	-- Notify base model that measurment has been completed														--##--
	trigger_collector.addblock.notify(tmName[2],"notifyStep",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY2)		--##--
	-- Loop to wait for base notification																		--##--
	trigger_collector.addblock.branch.counter(tmName[2], "branch-drain", "waitStep", bcSMUsettings[3])		 --##--
	
	-- Wait for notification that sweep has been completed
	trigger_collector.addblock.wait(tmName[2],"waitSweepDone",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY5 )
	trigger_collector.addblock.source.action.bias(tmName[2], "collectorzero", infoSMU[4])

--############################################################################################################--

	-- Initiate trigger models, delete when completed
	baseSMU.source.output = 1
	baseSMU.source.output = 1
	collectorSMU.source.output = 1
	collectorSMU.source.output = 1

	trigger_collector.initiate(tmName[2])
	trigger_base.initiate(tmName[1])
	waitcomplete()
	baseSMU.source.output = 0
	collectorSMU.source.output = 0

	trigger_collector.delete(tmName[2])
	trigger_base.delete(tmName[1])

	-- Display results from buffers
	print("Vb\t\t Ib\t\t Vce\t\t Ic")
	for j = 1, baseSMU.defbuffer1.n , 1 do
		print(baseSMU.defbuffer2[j],baseSMU.defbuffer1[j],collectorSMU.defbuffer2[j],collectorSMU.defbuffer1[j])
	end	

	-- Check for errors and
	function errorQUEUE()
		errorqueue_Count = errorqueue.count
		print("Error Queue Count:".. errorqueue_Count)
		if errorqueue_Count > 0 then
		  for i = 1, errorqueue_Count do
			print(i, errorqueue.next())
		  end
		end
	end
	errorQUEUE()
end 

-- information of SMU
local base_slot     = 1
local collector_slot = 1
local common_slot 	= 1
local base_channel  = 1
local collector_channel = 2

-- Base & Collector Channel Settings
local startVbVc		= 0
local stopVbVc		= 1
local noSwpPoints	= 41
local limitIbIc		= 500e-3
-- Measure Settings for both channels
local nplc			= 1
local mDelay		= 0

--Gummel_VbIc_RunTimeEnv({base_slot,base_channel,collector_slot,collector_channel},{startVbVc,stopVbVc,noSwpPoints,limitIbIc},{nplc,mDelay})

Gummel_VbIc_TriggerInOneSlot({common_slot,base_channel,collector_channel},{startVbVc,stopVbVc,noSwpPoints,limitIbIc},{nplc,mDelay},{"tm_vbic"})

--Gummel_VbIc_TwoTriggers({base_slot,base_channel,collector_slot,collector_channel},{startVbVc,stopVbVc,noSwpPoints,limitIbIc},{nplc,mDelay},{"tm_base", "tm_collector"})



