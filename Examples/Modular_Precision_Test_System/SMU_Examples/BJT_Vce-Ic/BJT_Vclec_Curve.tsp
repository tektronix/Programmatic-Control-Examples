--[[
################################################################################

Script File: BJT_Vclec_Curve.tsp

    ************************************************************************
    *** Copyright Tektronix, Inc.                                        ***
    *** See www.tek.com/sample-license for licensing terms.              ***
    ************************************************************************

Description:
    This script is example code, which creates (and subsequently calls) several
    functions that can be used with the Model MP5000 Based SMUs to perform a
	drain family of curve test for MOSFET devices. The purpose is show that 
	you can perform the semiductor device characterization with the SMUs  
    As written, two channels of SMU are assigned to the base/collector and the two
	LOs from the two channels are tied together to the emitter. There are three different
	scripts for the same test. One is operation in run time environment, the other
	is single trigger model for both channels in the same slot. The third is another trigger
	model example for each channel in different slot or in the same slot in the trigger
	trigger model. 
	Upon completion of each test, the data is printed to the TSP Toolkit Console 
	in a format that is suitable for copying and pasting into Microsoft Excel for 
	graphing and analysis.

Required Equipment: 1 Model MP5000 Mainframe 
					2 channel SMUs 
					1 BJT transistor

Note:  The functions do not perform any error checking.  It is the user's 
       responsibility to specify settings that are compatible with the 
       instrument model being used, and with its power envelope.
       
Note:  It is the user's responsibility to follow all safety guidelines given in 
       the instrument's Reference Manual.  This is especially critical if 
       voltages in excess of 42VDC will be present in the test circuits.  Such 
       voltage levels are hazardous. 
       
Functions created by this script:
	* OutputCurve_VceIc_RunTimeEnv({base_slot,collector_slot,base_channel,collector_channel},{startVc,stopVc,noSwpPoints,rangeIc,limitIc},{startIb,stopIb,noStpPoints,limitVb},{nplc,mDelay})
	* OutputCurve_VceIc_TriggerInOneSlot({common_slot,base_channel,collector_channel},{startVc,stopVc,noSwpPoints,rangeIc,limitIc},{startIb,stopIb,noStpPoints,limitVb},{nplc,mDelay},{"tm_vcic"})
	* OutputCurve_VceIc_TwoTriggers({base_slot,collector_slot,base_channel,collector_channel},{startVc,stopVc,noSwpPoints,rangeIc,limitIc},{startIb,stopIb,noStpPoints,limitVb},{nplc,mDelay},{"tm_base","tm_collector"})

Example Usage:
	* OutputCurve_VceIc_RunTimeEnv({base_slot,collector_slot,base_channel,collector_channel},{startVc,stopVc,noSwpPoints,rangeIc,limitIc},{startIb,stopIb,noStpPoints,limitVb},{nplc,mDelay})
	* OutputCurve_VceIc_TriggerInOneSlot({common_slot,base_channel,collector_channel},{startVc,stopVc,noSwpPoints,rangeIc,limitIc},{startIb,stopIb,noStpPoints,limitVb},{nplc,mDelay},{"tm_vcic"})
	* OutputCurve_VceIc_TwoTriggers({base_slot,collector_slot,base_channel,collector_channel},{startVc,stopVc,noSwpPoints,rangeIc,limitIc},{startIb,stopIb,noStpPoints,limitVb},{nplc,mDelay},{"tm_base","tm_collector"})
    
################################################################################
--]]
function OutputCurve_VceIc_RunTimeEnv(infoSMU,cSMUsettings, bSMUsettings, meaSettings)
	-- SMU channel assignment
	local baseSMU      							= slot[infoSMU[1]].smu[infoSMU[2]]
	local collectorSMU     						= slot[infoSMU[3]].smu[infoSMU[4]]
	local smu_id								= {baseSMU,collectorSMU}

	-- Configure both channel settings
	for i = 1, 2 do	
		smu_id[i].reset()
		-- Base set to perform current sweep
		if smu_id[i] == baseSMU then
			smu_id[i].source.func				= smu_id[i].FUNC_DC_CURRENT
			smu_id[i].source.rangei				= math.max(math.abs(bSMUsettings[1]), math.abs(bSMUsettings[2]))
			smu_id[i].source.limitv				= bSMUsettings[4]
		-- Collector to perform voltage sweep
		else
			smu_id[i].source.func				= smu_id[i].FUNC_DC_VOLTAGE
			smu_id[i].source.rangev				= math.max(math.abs(cSMUsettings[1]), math.abs(cSMUsettings[2]))
			smu_id[i].source.limiti				= cSMUsettings[5]	
			smu_id[i].measure.rangei			= cSMUsettings[4]
		end	

		smu_id[i].sense							= smu_id[i].SENSE_2WIRE
		smu_id[i].measure.nplc					= meaSettings[1]

		smu_id[i].defbuffer1.clear()
		smu_id[i].defbuffer1.appendmode			= 1
		smu_id[i].defbuffer2.clear()
		smu_id[i].defbuffer2.appendmode			= 1
	end

	-- Calculate the change in voltage/current for the two terminals
	local deltaVd = (cSMUsettings[2] - cSMUsettings[1])/ (cSMUsettings[3] - 1)
	local deltaIg = (bSMUsettings[2] - bSMUsettings[1])/ (bSMUsettings[3] - 1)

	-- Turn outputs on
	baseSMU.source.output   = 1
	baseSMU.source.output   = 1

	collectorSMU.source.output  = 1
	collectorSMU.source.output  = 1

	-- Perform current sweep on collector, voltage sweep on base
	print("Vb\t\t Ib\t\t Vce\t\t Ic")
	for gateLoop = 1, bSMUsettings[3], 1 do
		-- Set base current to next value in sweep
		baseSMU.source.leveli = bSMUsettings[1] + ((gateLoop -1) * deltaIg)
		for drainLoop = 1, cSMUsettings[3] , 1 do
			-- Set collector voltage to next value in sweep
			collectorSMU.source.levelv = cSMUsettings[1] + ((drainLoop-1) * deltaVd)
			delay(meaSettings[2])
			-- Measure i/v on both channels and store in default buffers
			baseSMU.measure.iv(baseSMU.defbuffer1,baseSMU.defbuffer2)
			collectorSMU.measure.iv(collectorSMU.defbuffer1,collectorSMU.defbuffer2)
			-- Display results
			print(baseSMU.defbuffer2[(cSMUsettings[3]*(gateLoop-1)) + drainLoop ],baseSMU.defbuffer1[(cSMUsettings[3]*(gateLoop-1)) + drainLoop],collectorSMU.defbuffer2[(cSMUsettings[3]*(gateLoop-1)) + drainLoop],collectorSMU.defbuffer1[(cSMUsettings[3]*(gateLoop-1)) + drainLoop])
		end 
	end
	baseSMU.source.output   = 0
	collectorSMU.source.output  = 0

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

function OutputCurve_VceIc_TriggerInOneSlot(infoSMU,cSMUsettings, bSMUsettings, meaSettings,tmName)
	-- SMU channel assignment
	local baseSMU  								= slot[infoSMU[1]].smu[infoSMU[2]]
	local collectorSMU 							= slot[infoSMU[1]].smu[infoSMU[3]]
	local smu_id       							= {baseSMU,collectorSMU}
	-- Configure both channel settings
	for i = 1, 2 do	
		smu_id[i].reset()
		-- Set base to perform current sweep
		if smu_id[i] == baseSMU then
			smu_id[i].source.func				= smu_id[i].FUNC_DC_CURRENT
			smu_id[i].source.rangei				= math.max(math.abs(bSMUsettings[1]), math.abs(bSMUsettings[2]))
			smu_id[i].source.limitv				= bSMUsettings[4]
		-- Set collector to perform voltage sweep
		else
			smu_id[i].source.func				= smu_id[i].FUNC_DC_VOLTAGE
			smu_id[i].source.rangev				= math.max(math.abs(cSMUsettings[1]), math.abs(cSMUsettings[2]))
			smu_id[i].source.limiti				= cSMUsettings[5]	
			smu_id[i].measure.rangei			= cSMUsettings[4]
		end	

		smu_id[i].sense							= smu_id[i].SENSE_2WIRE
		smu_id[i].measure.nplc					= meaSettings[1]

		smu_id[i].defbuffer1.clear()
		smu_id[i].defbuffer1.appendmode			= 1
		smu_id[i].defbuffer2.clear()
		smu_id[i].defbuffer2.appendmode			= 1
	end
	-- Configure voltage and current sweeps
	collectorSMU.trigger.source.linearv(cSMUsettings[1], cSMUsettings[2], cSMUsettings[3])
	-- Configure trigger model measurements to i/v and store in default buffers
	collectorSMU.trigger.measure.iv(collectorSMU.defbuffer1,collectorSMU.defbuffer2)
	baseSMU.trigger.source.lineari(bSMUsettings[1], bSMUsettings[2], bSMUsettings[3])
	baseSMU.trigger.measure.iv(baseSMU.defbuffer1,baseSMU.defbuffer2)

--############################################## Trigger model ###############################################--
--############################################################################################################--

	local triggerModel = slot[infoSMU[1]].trigger.model
	triggerModel.create(tmName[1]) 
	-- Advance base voltage to next value in sweep																		-- Loop 2
	triggerModel.addblock.source.action.step(tmName[1], "baseVoltage", infoSMU[2])											--##--
	-- Advance collector current to next value in sweep														-- Loop 1 		--##--
	triggerModel.addblock.source.action.step(tmName[1], "collectorVoltage", infoSMU[3])							--##--		--##--
	-- Measure both channels i/v																				--##--		--##--
	triggerModel.addblock.measure(tmName[1], "measure", infoSMU[2], 1)											--##--		--##--
	triggerModel.addblock.measure(tmName[1], "measure2", infoSMU[3], 1)											--##--		--##--
	-- Loop back to advancing collector voltage																	--##--		--##--
	triggerModel.addblock.branch.counter(tmName[1], "branch-collector", "collectorVoltage", cSMUsettings[3]) --##--			--##--
	-- Loop back to advancing base current																					--##--
	triggerModel.addblock.branch.counter(tmName[1], "branch-base", "baseVoltage", bSMUsettings[3])						 --##--
	-- Reset sources to 0
	triggerModel.addblock.source.action.bias(tmName[1], "basebiaszeo", infoSMU[2])
	triggerModel.addblock.source.action.bias(tmName[1], "collectorbiaszeo", infoSMU[3])

--############################################################################################################--

	-- Initiate trigger model, delete when completed
	baseSMU.source.output   = 1
	collectorSMU.source.output  = 1

	triggerModel.initiate(tmName[1])
	waitcomplete()

	baseSMU.source.output   = 0
	collectorSMU.source.output  = 0
	triggerModel.delete(tmName[1])

	-- Display contents of buffers
	print("Vb\t\t Ib\t\t Vce\t\t Ic")
	for j = 1, collectorSMU.defbuffer1.n , 1 do
		print(baseSMU.defbuffer2[j],baseSMU.defbuffer1[j],collectorSMU.defbuffer2[j],collectorSMU.defbuffer1[j])
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
	errorQUEUE()
end 

function OutputCurve_VceIc_TwoTriggers(infoSMU,cSMUsettings, bSMUsettings, meaSettings,tmName)
	-- SMU channel assignment
	local baseSMU      							= slot[infoSMU[1]].smu[infoSMU[3]]
	local collectorSMU     						= slot[infoSMU[2]].smu[infoSMU[4]]
	local smu_id								= {baseSMU,collectorSMU}
	-- Configure channel settings
	for i = 1, 2 do	
		smu_id[i].reset()
		-- Set base channel to perform current sweep
		if smu_id[i] == baseSMU then
			smu_id[i].source.func				= smu_id[i].FUNC_DC_CURRENT
			smu_id[i].source.rangei				= math.max(math.abs(bSMUsettings[1]), math.abs(bSMUsettings[2]))
			smu_id[i].source.limitv				= bSMUsettings[4]
		-- Set collector channel to perform voltage sweep
		else
			smu_id[i].source.func				= smu_id[i].FUNC_DC_VOLTAGE
			smu_id[i].source.rangev				= math.max(math.abs(cSMUsettings[1]), math.abs(cSMUsettings[2]))
			smu_id[i].source.limiti				= cSMUsettings[5]	
			smu_id[i].measure.rangei			= cSMUsettings[4]
		end	

		smu_id[i].sense							= smu_id[i].SENSE_2WIRE
		smu_id[i].measure.nplc					= meaSettings[1]

		smu_id[i].defbuffer1.clear()
		smu_id[i].defbuffer1.appendmode			= 1
		smu_id[i].defbuffer2.clear()
		smu_id[i].defbuffer2.appendmode			= 1
	end

--######################################### Collector trigger model ##########################################--
--############################################################################################################--

	-- Configure trigger model for a linear voltage sweep
	collectorSMU.trigger.source.linearv(cSMUsettings[1], cSMUsettings[2], cSMUsettings[3])
	-- Set trigger model measurements to i/v and store in default buffers
	collectorSMU.trigger.measure.iv(collectorSMU.defbuffer1,collectorSMU.defbuffer2)

	local trigger_collector = slot[infoSMU[2]].trigger.model
	trigger_collector.create(tmName[2])

	-- Notify base model that collector model has began																		-- Loop 2
	trigger_collector.addblock.notify(tmName[2],"notifyStep",slot[infoSMU[2]].trigger.model.EVENT_NOTIFY1)						--##--
																																--##--
	-- Wait for notification that base current has been advanced																--##--
	trigger_collector.addblock.wait(tmName[2],"waitStep",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY2 )							--##--
	-- Advance voltage source value																				-- Loop 1		--##--
	trigger_collector.addblock.source.action.step(tmName[2], "collectorSweep", infoSMU[4])							--##--		--##--
	-- Notify base that voltage sweep has been advanced																--##--		--##--
	trigger_collector.addblock.notify(tmName[2],"notifyMeasure",slot[infoSMU[2]].trigger.model.EVENT_NOTIFY3)		--##--		--##--
	-- Measure collector channel i/v 																				--##--		--##--
	trigger_collector.addblock.measure(tmName[2], "measure", infoSMU[4], 1)											--##--		--##--
																													--##--		--##--
	-- Wait for notification from base that mesurement has been taken												--##--		--##--
	trigger_collector.addblock.wait(tmName[2],"waitMeasure",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY4 )			--##--		--##--
	-- Loop back to advance voltage value																			--##--		--##--
	trigger_collector.addblock.branch.counter(tmName[2], "branch-sweep", "collectorSweep", cSMUsettings[3])		 --##--			--##--
	-- Notify base that voltage sweep has completed																				--##--
	trigger_collector.addblock.notify(tmName[2],"notifySweepDone",slot[infoSMU[2]].trigger.model.EVENT_NOTIFY5)					--##--
	-- Loop back to notify base that sweep has begun																			--##--
	trigger_collector.addblock.branch.counter(tmName[2], "branch-step", "notifyStep",  bSMUsettings[3])						 --##--
	trigger_collector.addblock.source.action.bias(tmName[2], "collectorbiaszeo", infoSMU[4])

--############################################ Base trigger model ############################################--
--############################################################################################################--

	-- Configure trigger model for a linear current sweep
	baseSMU.trigger.source.lineari(bSMUsettings[1], bSMUsettings[2], bSMUsettings[3])
	-- Set trigger model measurements i/v and store in default buffers
	baseSMU.trigger.measure.iv(baseSMU.defbuffer1,baseSMU.defbuffer2)

	local trigger_base = slot[infoSMU[1]].trigger.model
	trigger_base.create(tmName[1])

	-- Wait for notification that collector model has started														-- Loop 2
	trigger_base.addblock.wait(tmName[1],"waitStep",slot[infoSMU[2]].trigger.model.EVENT_NOTIFY1 )						--##--
	-- Advance current source value																						--##--
	trigger_base.addblock.source.action.step(tmName[1], "baseVoltage", infoSMU[3])										--##--
	-- Notify collector that current has been advanced																	--##--
	trigger_base.addblock.notify(tmName[1],"notify",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY2)						--##--
																														--##--
	-- Wait for notificaiton from collector that measurement has been taken								-- Loop 1   	--##--
	trigger_base.addblock.wait(tmName[1],"waitMeasure",slot[infoSMU[2]].trigger.model.EVENT_NOTIFY3 )		--##--		--##--
	-- Measure base channel i/v																				--##--		--##--
	trigger_base.addblock.measure(tmName[1],"measure",infoSMU[3],1)											--##--		--##--
	-- Notify collector that measurement has been taken														--##--		--##--
	trigger_base.addblock.notify(tmName[1],"notify",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY4)			--##--		--##--
	-- Loop back to wait for notification from collector													--##--		--##--
	trigger_base.addblock.branch.counter(tmName[1], "branch-Measure", "waitMeasure", cSMUsettings[3])	 --##--			--##--
																														--##--
	-- Wait for notification that collector voltage sweep has completed													--##--
	trigger_base.addblock.wait(tmName[1],"waitSweepDone",slot[infoSMU[2]].trigger.model.EVENT_NOTIFY5 )					--##--
	-- Loop back to wait for notification from collector and advance current											--##--
	trigger_base.addblock.branch.counter(tmName[1], "branch-Step", "waitStep",  bSMUsettings[3])					 --##--
	trigger_base.addblock.source.action.bias(tmName[1], "gatebiaszero", infoSMU[3])

--############################################################################################################--

	-- Initiate trigger models, delete when finished
	baseSMU.source.output   = 1
	collectorSMU.source.output  = 1
	trigger_base.initiate(tmName[1])
	trigger_collector.initiate(tmName[2])

	waitcomplete()

	baseSMU.source.output   = 0
	collectorSMU.source.output  = 0

	trigger_base.delete(tmName[1])
	trigger_collector.delete(tmName[2])

	-- Display results from default buffers
	print("Vb\t\t Ib\t\t Vce\t\t Ic")
	for j = 1, collectorSMU.defbuffer1.n , 1 do
		print(baseSMU.defbuffer2[j],baseSMU.defbuffer1[j],collectorSMU.defbuffer2[j],collectorSMU.defbuffer1[j])
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
	errorQUEUE()	
end 

-- Information of SMU
local base_slot     = 1
local collector_slot= 1
local common_slot 	= 1
local base_channel  = 1
local collector_channel = 2
-- Collector Channel Settings
local startVc		= 0
local stopVc		= 2
local noSwpPoints	= 41
local rangeIc		= 250e-3
local limitIc		= 250e-3
-- Base Channel Settings
local startIb		= 3.0e-3
local stopIb		= 10.0e-3
local noStpPoints	= 5
local limitVb		= 6
-- Measure Settings for both channels
local nplc			= 1
local mDelay		= 0

--OutputCurve_VceIc_RunTimeEnv({base_slot,collector_slot,base_channel,collector_channel},{startVc,stopVc,noSwpPoints,rangeIc,limitIc},{startIb,stopIb,noStpPoints,limitVb},{nplc,mDelay})

OutputCurve_VceIc_TriggerInOneSlot({common_slot,base_channel,collector_channel},{startVc,stopVc,noSwpPoints,rangeIc,limitIc},{startIb,stopIb,noStpPoints,limitVb},{nplc,mDelay},{"tm_vcic"})

--OutputCurve_VceIc_TwoTriggers({base_slot,collector_slot,base_channel,collector_channel},{startVc,stopVc,noSwpPoints,rangeIc,limitIc},{startIb,stopIb,noStpPoints,limitVb},{nplc,mDelay},{"tm_base","tm_collector"})

