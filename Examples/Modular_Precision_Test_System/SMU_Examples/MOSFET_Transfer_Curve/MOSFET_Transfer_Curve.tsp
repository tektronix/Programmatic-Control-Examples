--[[
################################################################################

Script File: MOSFET_Transfer_Curve.tsp

    ************************************************************************
    *** Copyright Tektronix, Inc.                                        ***
    *** See www.tek.com/sample-license for licensing terms.              ***
    ************************************************************************

Description:
    This script is example code, which creates (and subsequently calls) several
    functions that can be used with the Model MP5000 Based SMUs to perform a
	drain famility of curve test for MOSFET devices. The purpose is show that 
	you can perform the semiductor device characterization with the SMUs  
    As written, two channels of SMU are assigned to the gate, drain, and the two
	LOs from the two channels are tied together to source.
	Upon completion of each test, the data is printed to the TSP Toolkit Console 
	in a format that is suitable for copying and pasting into Microsoft Excel for 
	graphing and analysis.

Required Equipment: 1 Model MP5000 Mainframe 
					2 channel SMUs 
					1 MOSFET

Note:  The functions do not perform any error checking.  It is the user's 
       responsibility to specify settings that are compatible with the 
       instrument model being used, and with its power envelope.
       
Note:  It is the user's responsibility to follow all safety guidelines given in 
       the instrument's Reference Manual.  This is especially critical if 
       voltages in excess of 42VDC will be present in the test circuits.  Such 
       voltage levels are hazardous. 
       
Functions created by this script:
    * TransferCurve_VgId_RunTimeEnv({gate_slot,gate_channel,drain_slot,drain_channel},{Vd,limitId},{startVg,stopVg,noSwpPoints,limitIg},{nplc,mDelay})
	* TransferCurve_VgId_TriggerOneSlot({common_slot,gate_channel,drain_channel},{Vd,limitId},{startVg,stopVg,noSwpPoints,limitIg},{nplc,mDelay})
	* TransferCurve_VgId_TwoTriggers({gate_slot,gate_channel,drain_slot,drain_channel},{Vd,limitId},{startVg,stopVg,noSwpPoints,limitIg},{nplc,mDelay})

Example Usage:
    * TransferCurve_VgId_RunTimeEnv({1,1,1,2},{1,0.1},{0,2.2,45,0.1},{1,0})
	* TransferCurve_VgId_TriggerOneSlot({1,1,2},{1,0.1},{0,2.2,45,0.1},{1,0},{"tm_vgid"})
	* TransferCurve_VgId_TwoTriggers({1,1,1,1},{1,0.1},{0,2.2,45,0.1},{1,0},{"tm_gate","tm_drain"})
	
################################################################################
--]]
function TransferCurve_VgId_RunTimeEnv(infoSMU,dSMUsettings, gSMUsettings, meaSettings)
	-- SMU channel assignment
	local gateSMU      							= slot[infoSMU[1]].smu[infoSMU[2]]
	local drainSMU     							= slot[infoSMU[3]].smu[infoSMU[4]]
	local smu_id 								= {gateSMU,drainSMU}
	-- Set both channels for voltage output
	for i = 1, 2 do	
		smu_id[i].reset()
		smu_id[i].source.func					= smu_id[i].FUNC_DC_VOLTAGE
		smu_id[i].sense							= smu_id[i].SENSE_2WIRE
		if smu_id[i] == gateSMU then
			smu_id[i].source.rangev				=  math.max(math.abs(gSMUsettings[1]), math.abs(gSMUsettings[2]))
			smu_id[i].source.limiti				= gSMUsettings[4]
		else
			smu_id[i].source.rangev				= dSMUsettings[1]
			smu_id[i].source.limiti				= dSMUsettings[2]
		end
		smu_id[i].source.levelv 				= 0
		smu_id[i].measure.nplc					= meaSettings[1]
		smu_id[i].measure.autorangei			= 1
		smu_id[i].defbuffer1.clear()
		smu_id[i].defbuffer1.appendmode			= 1
		smu_id[i].defbuffer2.clear()
		smu_id[i].defbuffer2.appendmode			= 1
	end

	-- Calculate change in voltage for each iteration
	local deltaVg = (gSMUsettings[2] - gSMUsettings[1])/ (gSMUsettings[3] - 1)
	gateSMU.source.output = 1
	drainSMU.source.output = 1
	-- Set constant drain voltage
	drainSMU.source.levelv = dSMUsettings[1]

	print("Vg\t\t Ig\t\t Vd\t\t Id")
	for j = 1, gSMUsettings[3] , 1 do
		-- Advance gate source level
		gateSMU.source.levelv = gSMUsettings[1] + ((j-1) * deltaVg)
		delay(meaSettings[2])
		-- Measure i/v for both channels and store in default buffers
		gateSMU.measure.iv(gateSMU.defbuffer1, gateSMU.defbuffer2)
		drainSMU.measure.iv(drainSMU.defbuffer1, drainSMU.defbuffer2)
		-- Display results
		print(gateSMU.defbuffer2[j],gateSMU.defbuffer1[j],drainSMU.defbuffer2[j],drainSMU.defbuffer1[j])
	end

	gateSMU.source.output = 0
	drainSMU.source.output = 0

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

function TransferCurve_VgId_TriggerInOneSlot(infoSMU,dSMUsettings, gSMUsettings, meaSettings,tmName)
	-- SMU channel assignment
	local gateSMU  								= slot[infoSMU[1]].smu[infoSMU[2]]
	local drainSMU 								= slot[infoSMU[1]].smu[infoSMU[3]]
	local smu_id        						= {gateSMU,drainSMU}
	-- Set both channels for voltage output
	for i = 1, 2 do
		smu_id[i].reset()
		smu_id[i].source.func					= smu_id[i].FUNC_DC_VOLTAGE
		smu_id[i].sense							= smu_id[i].SENSE_2WIRE
		if smu_id[i] == gateSMU then
			smu_id[i].source.rangev				=  math.max(math.abs(gSMUsettings[1]), math.abs(gSMUsettings[2]))
			smu_id[i].source.limiti				= gSMUsettings[4]

		else
			smu_id[i].source.rangev				= dSMUsettings[1]
			smu_id[i].measure.rangev			= dSMUsettings[1]
			smu_id[i].source.limiti				= dSMUsettings[2]
		end
		smu_id[i].source.levelv 				= 0
		smu_id[i].measure.nplc					= meaSettings[1]
		smu_id[i].measure.autorangei			= 1
		
		smu_id[i].defbuffer1.clear()
		smu_id[i].defbuffer1.appendmode			= 1
		smu_id[i].defbuffer2.clear()
		smu_id[i].defbuffer2.appendmode			= 1
	end
	-- Configure both trigger models for voltage sweep
	-- Drain does not actually sweep, it remains constant
	drainSMU.trigger.source.linearv(dSMUsettings[1], dSMUsettings[1], 2)
	gateSMU.trigger.source.linearv(gSMUsettings[1], gSMUsettings[2], gSMUsettings[3])
	-- Set both trigger models to measure i/v and store in default buffer
	gateSMU.trigger.measure.iv(gateSMU.defbuffer1,gateSMU.defbuffer2)
	drainSMU.trigger.measure.iv(drainSMU.defbuffer1,drainSMU.defbuffer2)

--############################################## Trigger model ###############################################--
--############################################################################################################--

	local triggerModel = slot[infoSMU[1]].trigger.model
	triggerModel.create(tmName[1]) 

	-- Advance the drain source voltage
	triggerModel.addblock.source.action.step(tmName[1], "drainVoltage", infoSMU[3])
	-- Advance the gate source voltage																	-- Loop 1
	triggerModel.addblock.source.action.step(tmName[1], "gateVoltage", infoSMU[2])							--##--
	triggerModel.addblock.delay.constant(tmName[1],"meaDelay",meaSettings[2])								--##--
	-- Measure i/v on both channels																			--##--
	triggerModel.addblock.measure(tmName[1], "measure", infoSMU[2], 1)										--##--
	triggerModel.addblock.measure(tmName[1], "measure2", infoSMU[3], 1)										--##--
	-- Loop through all sweep values																		--##--
	triggerModel.addblock.branch.counter(tmName[1], "branch-counter", "gateVoltage", gSMUsettings[3])	 --##--

--############################################################################################################--

	-- Initiate trigger model and delete when completed
	gateSMU.source.output = 1
	gateSMU.source.output = 1
	drainSMU.source.output = 1
	drainSMU.source.output = 1
	triggerModel.initiate(tmName[1])
	waitcomplete()

	-- Display results
	print("Vg\t\t Ig\t\t Vd\t\t Id")
	for j = 1, gateSMU.defbuffer1.n , 1 do
		print(gateSMU.defbuffer2[j],gateSMU.defbuffer1[j],drainSMU.defbuffer2[j],drainSMU.defbuffer1[j])
	end

	gateSMU.source.output = 0
	drainSMU.source.output = 0
	triggerModel.delete(tmName[1])

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


function TransferCurve_VgId_TwoTriggers(infoSMU,dSMUsettings, gSMUsettings, meaSettings,tmName)
	-- SMU channel assignment
	local gateSMU       						= slot[infoSMU[1]].smu[infoSMU[2]]
	local drainSMU      						= slot[infoSMU[3]].smu[infoSMU[4]]
	local smu_id        						= {gateSMU,drainSMU}
	-- Configure both channels for voltage output
	for i = 1, 2 do	
		smu_id[i].reset()
		smu_id[i].source.func					= smu_id[i].FUNC_DC_VOLTAGE
		smu_id[i].sense							= smu_id[i].SENSE_2WIRE
		
		if smu_id[i] == gateSMU then
			smu_id[i].source.rangev				= math.max(math.abs(gSMUsettings[1]), math.abs(gSMUsettings[2]))
			smu_id[i].source.limiti				= gSMUsettings[4]
		else
			smu_id[i].source.rangev				= dSMUsettings[1]
			smu_id[i].source.limiti				= dSMUsettings[2]	
		end	
		smu_id[i].source.levelv 				= 0
		smu_id[i].measure.nplc					= meaSettings[1]
		smu_id[i].measure.autorangei			= 1
		smu_id[i].defbuffer1.clear()
		smu_id[i].defbuffer1.appendmode			= 1
		smu_id[i].defbuffer2.clear()
		smu_id[i].defbuffer2.appendmode			= 1
	end

--############################################ Gate trigger model ############################################--
--############################################################################################################--

	-- Configure gate source for linear voltage sweep
	gateSMU.trigger.source.linearv(gSMUsettings[1], gSMUsettings[2], gSMUsettings[3])
	-- Set trigger model to measure i/v and store in default buffer
	gateSMU.trigger.measure.iv(gateSMU.defbuffer1,gateSMU.defbuffer2)

	local trigger_gate = slot[infoSMU[1]].trigger.model
	trigger_gate.create(tmName[1])

	-- Notify drain that sweep has began
	trigger_gate.addblock.notify(tmName[1],"notifyDrainStep",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY1)
	
	-- Wait for notification that drain source voltage has advanced
	trigger_gate.addblock.wait(tmName[1],"waitDrainStep",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY2 )
	-- Advance gate voltage source level																-- Loop 1
	trigger_gate.addblock.source.action.step(tmName[1], "gateVoltage", infoSMU[2])							--##--
	-- Notify drain that source voltage has advanced														--##--
	trigger_gate.addblock.notify(tmName[1],"notify",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY3)			--##--
	-- Measure drain i/v																					--##--
	trigger_gate.addblock.measure(tmName[1], "measure", infoSMU[2], 1)										--##--
																											--##--
	-- Wait for measurement completed notification from drain 												--##--
	trigger_gate.addblock.wait(tmName[1],"wait",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY4 )				--##--
	-- Loop back to advance source voltage																	--##--
	trigger_gate.addblock.branch.counter(tmName[1], "branch-gate", "gateVoltage", gSMUsettings[3])		 --##--
	-- Notify drain that sweep has completed
	trigger_gate.addblock.notify(tmName[1],"notifySweepDone",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY5)
	trigger_gate.addblock.source.action.bias(tmName[1],"gatezero", infoSMU[2])

--########################################### Drain trigger model ############################################--
--############################################################################################################--

	-- Configure drain source to maintain constant voltage
	drainSMU.trigger.source.linearv(dSMUsettings[1], dSMUsettings[1], 1)
	-- Set trigger model to measure i/v and store in default buffers
	drainSMU.trigger.measure.iv(drainSMU.defbuffer1,drainSMU.defbuffer2)

	local trigger_drain = slot[infoSMU[3]].trigger.model
	trigger_drain.create(tmName[2])

	-- Wait for notificaiton that sweep has begun
	trigger_drain.addblock.wait(tmName[2],"waitStep",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY1 )
	-- Advance source voltage level
	trigger_drain.addblock.source.action.step(tmName[2], "drainVoltage", infoSMU[4])
	-- Notify gate that source voltage has advanced
	trigger_drain.addblock.notify(tmName[2],"notifyStep",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY2)
	
	-- Wait for notification that gate voltage source has advanced										-- Loop 1
	trigger_drain.addblock.wait(tmName[2],"waitMeas",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY3 )			--##--
	trigger_drain.addblock.delay.constant(tmName[2],"meaDelay",meaSettings[2])								--##--
	-- Measure drain i/v																					--##--
	trigger_drain.addblock.measure(tmName[2], "measure", infoSMU[4], 1)										--##--
	-- Notify gate that measurement has been taken															--##--
	trigger_drain.addblock.notify(tmName[2],"notify",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY4)			--##--
	-- Loop back to wait block																				--##--
	trigger_drain.addblock.branch.counter(tmName[2], "branch-drain", "waitMeas", gSMUsettings[3])		--##--
	
	-- Wait for notification that sweep has completed
	trigger_drain.addblock.wait(tmName[2],"waitSweepDone",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY5 )
	trigger_drain.addblock.source.action.bias(tmName[2], "drainzero", infoSMU[4])

--############################################################################################################--

	-- Initiate trigger models, delete when finished
	gateSMU.source.output = 1
	gateSMU.source.output = 1

	drainSMU.source.output = 1
	drainSMU.source.output = 1

	trigger_drain.initiate(tmName[2])
	trigger_gate.initiate(tmName[1])

	waitcomplete()

	-- Display results
	print("Vg\t\t Ig\t\t Vd\t\t Id")
	for j = 1, gateSMU.defbuffer1.n , 1 do
		print(gateSMU.defbuffer2[j],gateSMU.defbuffer1[j],drainSMU.defbuffer2[j],drainSMU.defbuffer1[j])
	end

	gateSMU.source.output = 0
	drainSMU.source.output = 0

	trigger_drain.delete(tmName[2])
	trigger_gate.delete(tmName[1])

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

-- information of SMU
local gate_slot     = 1
local drain_slot    = 1
local common_slot 	= 1
local gate_channel  = 1
local drain_channel = 2
-- Drain Channel Settings
local Vd			= 1
local limitId		= 0.1
-- Gate Channel Settings
local startVg		= 0
local stopVg		= 2.2
local noSwpPoints	= 45
local limitIg		= 0.1
-- Measure Settings for both channels
local nplc			= 1
local mDelay		= 0

--TransferCurve_VgId_RunTimeEnv({gate_slot,gate_channel,drain_slot,drain_channel},{Vd,limitId},{startVg,stopVg,noSwpPoints,limitIg},{nplc,mDelay})

TransferCurve_VgId_TriggerInOneSlot({common_slot,gate_channel,drain_channel},{Vd,limitId},{startVg,stopVg,noSwpPoints,limitIg},{nplc,mDelay},{"tm_vgid"})

--TransferCurve_VgId_TwoTriggers({gate_slot,gate_channel,drain_slot,drain_channel},{Vd,limitId},{startVg,stopVg,noSwpPoints,limitIg},{nplc,mDelay},{"tm_gate", "tm_drain"})





