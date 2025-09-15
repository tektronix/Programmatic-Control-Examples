--[[
################################################################################

Script File: MOSFET_Drain_Family_Curve.tsp

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
	* DrainFamilyCurve_VdId_RunTimeEnv({gate_slot,gate_channel,drain_slot,drain_channel},{startVd,stopVd,noSwpPoints,rangeId,limitId},{startVg,stopVg,noStpPoints,limitIg},{nplc,mDelay})
	* DrainFamilyCurve_VdId_TriggerInOneSlot({common_slot,gate_channel,drain_channel},{startVd,stopVd,noSwpPoints,rangeId,limitId},{startVg,stopVg,noStpPoints,limitIg},{nplc,mDelay},{"tm_vdid"})
	* DrainFamilyCurve_VdId_TwoTriggers({gate_slot,gate_channel,drain_slot,drain_channel},{startVd,stopVd,noSwpPoints,rangeId,limitId},{startVg,stopVg,noStpPoints,limitIg},{nplc,mDelay},{"tm_gate","tm_drain"})

Example Usage:
	* DrainFamilyCurve_VdId_RunTimeEnv({1,1,1,2},{0,2,41,0.1,0.1},{1.4,1.8,3,0.1},{1,0})
	* DrainFamilyCurve_VdId_TriggerInOneSlot({1,1,2},{0,2,41,0.1,0.1},{1.4,1.8,3,0.1},{1,0},{"tm_vdid"})
	* DrainFamilyCurve_VdId_TwoTriggers({1,1,1,2},{0,2,41,0.1,0.1},{1.4,1.8,3,0.1},{1,0},{"tm_gate","tm_drain"})
    
################################################################################
--]]
function DrainFamilyCurve_VdId_RunTimeEnv(infoSMU,dSMUsettings, gSMUsettings, meaSettings)
	-- SMU channel assignment
	local gateSMU      							= slot[infoSMU[1]].smu[infoSMU[2]]
	local drainSMU     							= slot[infoSMU[3]].smu[infoSMU[4]]
	local smu_id								= {gateSMU,drainSMU}
	-- Configure both channels for a voltage sweep
	for i = 1, 2 do	
		smu_id[i].reset()
		smu_id[i].source.func					= smu_id[i].FUNC_DC_VOLTAGE
		smu_id[i].sense							= smu_id[i].SENSE_2WIRE
		
		if smu_id[i] == gateSMU then
			smu_id[i].source.rangev				= math.max(math.abs(gSMUsettings[1]), math.abs(gSMUsettings[2]))
			smu_id[i].source.limiti				= gSMUsettings[4]
	
		else
			smu_id[i].source.rangev				= math.max(math.abs(dSMUsettings[1]), math.abs(dSMUsettings[2]))
			smu_id[i].source.limiti				= dSMUsettings[5]	
			smu_id[i].measure.rangei			= dSMUsettings[4]
		end	
		smu_id[i].source.levelv 				= 0
		smu_id[i].measure.nplc					= meaSettings[1]

		smu_id[i].defbuffer1.clear()
		smu_id[i].defbuffer1.appendmode			= 1
		smu_id[i].defbuffer2.clear()
		smu_id[i].defbuffer2.appendmode			= 1
	end

	-- Calculate the voltage step for both channels
	local deltaVd = (dSMUsettings[2] - dSMUsettings[1])/ (dSMUsettings[3] - 1)
	local deltaVg = (gSMUsettings[2] - gSMUsettings[1])/ (gSMUsettings[3] - 1)

	gateSMU.source.output   = 1
	gateSMU.source.output   = 1

	drainSMU.source.output  = 1
	drainSMU.source.output  = 1

	print("Vg\t\t Ig\t\t Vd\t\t Id")
	-- Execute both sweeps
	for gateLoop = 1, gSMUsettings[3], 1 do
		-- Advance gate voltage
		gateSMU.source.levelv = gSMUsettings[1] + ((gateLoop -1) * deltaVg)
		for drainLoop = 1, dSMUsettings[3] , 1 do
			-- Advance drain voltage
			drainSMU.source.levelv = dSMUsettings[1] + ((drainLoop-1) * deltaVd)
			delay(meaSettings[2])
			-- Measure i/vo n both channels, store in default buffers
			gateSMU.measure.iv(gateSMU.defbuffer1,gateSMU.defbuffer2)
			drainSMU.measure.iv(drainSMU.defbuffer1,drainSMU.defbuffer2)
			-- Display results
			print(gateSMU.defbuffer2[(dSMUsettings[3]*(gateLoop-1)) + drainLoop ],gateSMU.defbuffer1[(dSMUsettings[3]*(gateLoop-1)) + drainLoop],drainSMU.defbuffer2[(dSMUsettings[3]*(gateLoop-1)) + drainLoop],drainSMU.defbuffer1[(dSMUsettings[3]*(gateLoop-1)) + drainLoop])
		end 
	end
	gateSMU.source.output   = 0
	drainSMU.source.output  = 0

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

function DrainFamilyCurve_VdId_TriggerInOneSlot(infoSMU,dSMUsettings, gSMUsettings, meaSettings,tmName)
	-- SMU channel assignment
	local gateSMU  								= slot[infoSMU[1]].smu[infoSMU[2]]
	local drainSMU 								= slot[infoSMU[1]].smu[infoSMU[3]]
	local smu_id       							= {gateSMU,drainSMU}
	-- Configure both channels for a voltage sweep
	for i = 1, 2 do	
		smu_id[i].reset()
		smu_id[i].source.func					= smu_id[i].FUNC_DC_VOLTAGE
		smu_id[i].sense							= smu_id[i].SENSE_2WIRE
		
		if smu_id[i] == gateSMU then
			smu_id[i].source.rangev				= math.max(math.abs(gSMUsettings[1]), math.abs(gSMUsettings[2]))
			smu_id[i].source.limiti				= gSMUsettings[4]
	
		else
			smu_id[i].source.rangev				= math.max(math.abs(dSMUsettings[1]), math.abs(dSMUsettings[2]))
			smu_id[i].source.limiti				= dSMUsettings[5]
			smu_id[i].measure.rangei			= dSMUsettings[4]
		end	
		smu_id[i].source.levelv 				= 0
		smu_id[i].measure.nplc					= meaSettings[1]

		smu_id[i].defbuffer1.clear()
		smu_id[i].defbuffer1.appendmode			= 1
		smu_id[i].defbuffer2.clear()
		smu_id[i].defbuffer2.appendmode			= 1
	end

	-- Set both trigger model sources to a linear voltage sweep
	drainSMU.trigger.source.linearv(dSMUsettings[1], dSMUsettings[2], dSMUsettings[3])
	-- Set both trigger model measurements to i/v and store in default buffers
	drainSMU.trigger.measure.iv(drainSMU.defbuffer1,drainSMU.defbuffer2)
	gateSMU.trigger.source.linearv(gSMUsettings[1], gSMUsettings[2], gSMUsettings[3])
	gateSMU.trigger.measure.iv(gateSMU.defbuffer1,gateSMU.defbuffer2)

--############################################## Trigger model ###############################################--
--############################################################################################################--

	local triggerModel = slot[infoSMU[1]].trigger.model
	triggerModel.create(tmName[1]) 

	-- Advance gate voltage to next value																		-- Loop 2
	triggerModel.addblock.source.action.step(tmName[1], "gateVoltage", infoSMU[2])									--##--
	-- Advance drain voltage to next value															-- Loop 1       --##--
	triggerModel.addblock.source.action.step(tmName[1], "drainVoltage", infoSMU[3])						--##--		--##--
	-- Measure i/v on both channels																		--##--		--##--
	triggerModel.addblock.measure(tmName[1], "measure", infoSMU[2], 1)									--##--		--##--
	triggerModel.addblock.measure(tmName[1], "measure2", infoSMU[3], 1)									--##--		--##--
	-- Loop back to advance drain voltage																--##--		--##--
	triggerModel.addblock.branch.counter(tmName[1], "branch-drain", "drainVoltage", dSMUsettings[3]) --##--		    --##--
	-- Loop back to advance gate voltage																			--##--
	triggerModel.addblock.branch.counter(tmName[1], "branch-gate", "gateVoltage", gSMUsettings[3])				 --##--
	-- Set sources to 0
	triggerModel.addblock.source.action.bias(tmName[1], "gatebiaszeo", infoSMU[2])
	triggerModel.addblock.source.action.bias(tmName[1], "drainbiaszeo", infoSMU[3])

--############################################################################################################--

	-- Initiate trigger model, delete when completed
	gateSMU.source.output   = 1
	drainSMU.source.output  = 1

	triggerModel.initiate(tmName[1])
	waitcomplete()

	gateSMU.source.output   = 0
	drainSMU.source.output  = 0
	triggerModel.delete(tmName[1])

	-- Display results from buffers
	print("Vg\t\t Ig\t\t Vd\t\t Id")
	for j = 1, drainSMU.defbuffer1.n , 1 do
		print(gateSMU.defbuffer2[j],gateSMU.defbuffer1[j],drainSMU.defbuffer2[j],drainSMU.defbuffer1[j])
	end

	;-- Check for errors and display
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

function DrainFamilyCurve_VdId_TwoTriggers(infoSMU,dSMUsettings, gSMUsettings, meaSettings,tmName)
	-- SMU channel assignment
	local gateSMU      							= slot[infoSMU[1]].smu[infoSMU[2]]
	local drainSMU     							= slot[infoSMU[3]].smu[infoSMU[4]]
	local smu_id								= {gateSMU,drainSMU}
	-- Configure both channels for a voltage sweep
	for i = 1, 2 do	
		smu_id[i].reset()
		smu_id[i].source.func					= smu_id[i].FUNC_DC_VOLTAGE
		smu_id[i].sense							= smu_id[i].SENSE_2WIRE
		
		if smu_id[i] == gateSMU then
			smu_id[i].source.rangev				= math.max(math.abs(gSMUsettings[1]), math.abs(gSMUsettings[2]))
			smu_id[i].source.limiti				= gSMUsettings[4]
	
		else
			smu_id[i].source.rangev				= math.max(math.abs(dSMUsettings[1]), math.abs(dSMUsettings[2]))
			smu_id[i].source.limiti				= dSMUsettings[5]	
			smu_id[i].measure.rangei			= dSMUsettings[4]
		end	
		smu_id[i].source.levelv 				= 0
		smu_id[i].measure.nplc					= meaSettings[1]

		smu_id[i].defbuffer1.clear()
		smu_id[i].defbuffer1.appendmode			= 1
		smu_id[i].defbuffer2.clear()
		smu_id[i].defbuffer2.appendmode			= 1
	end

--########################################### Drain Trigger model ############################################--
--############################################################################################################--

	-- Configure trigger model source for linear voltage sweep
	drainSMU.trigger.source.linearv(dSMUsettings[1], dSMUsettings[2], dSMUsettings[3])
	-- Set trigger model measurements to i/v and store in default buffers
	drainSMU.trigger.measure.iv(drainSMU.defbuffer1,drainSMU.defbuffer2)

	local trigger_drain = slot[infoSMU[3]].trigger.model
	trigger_drain.create(tmName[2]) 

	-- Notify gate that sweep has began																					-- Loop 2
	trigger_drain.addblock.notify(tmName[2],"notifyStep",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY1)						--##--
																															--##--
	-- Wait for notification from gate that gate voltage has advanced														--##--
	trigger_drain.addblock.wait(tmName[2],"waitStep",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY2 )							--##--
	-- Advance drain source voltage																			-- Loop 1 		--##--
	trigger_drain.addblock.source.action.step(tmName[2], "drainSweep", infoSMU[4])								--##--		--##--
	-- Notify gate that drain voltage has advanced																--##--		--##--
	trigger_drain.addblock.notify(tmName[2],"notifyMeasure",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY3)		--##--		--##--
	-- Measure drain i/v																						--##--		--##--
	trigger_drain.addblock.measure(tmName[2], "measure", infoSMU[4], 1)											--##--		--##--
																												--##--		--##--
	-- Wait for notification that gate measurement has been taken												--##--		--##--
	trigger_drain.addblock.wait(tmName[2],"waitMeasure",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY4 )			--##--		--##--
	-- Loop back to advancing drain voltage																		--##--		--##--
	trigger_drain.addblock.branch.counter(tmName[2], "branch-sweep", "drainSweep", dSMUsettings[3])			 --##--			--##--
	-- Notify gate that drain voltage sweep has completed																	--##--
	trigger_drain.addblock.notify(tmName[2],"notifySweepDone",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY5)					--##--
	-- Loop back to notify gate to begin sweep																				--##--
	trigger_drain.addblock.branch.counter(tmName[2], "branch-step", "notifyStep",  gSMUsettings[3])						 --##--
	trigger_drain.addblock.source.action.bias(tmName[2], "drainbiaszeo", infoSMU[4])

--############################################ Gate Trigger model ############################################--
--############################################################################################################--

	-- Configure trigger model source for linear voltage sweep
	gateSMU.trigger.source.linearv(gSMUsettings[1], gSMUsettings[2], gSMUsettings[3])
	-- Set trigger model measurements to i/v and store in default buffers
	gateSMU.trigger.measure.iv(gateSMU.defbuffer1,gateSMU.defbuffer2)

	local trigger_gate = slot[infoSMU[1]].trigger.model
	trigger_gate.create(tmName[1]) 

	-- Wait for notification from drain to begin																		-- Loop 2
	trigger_gate.addblock.wait(tmName[1],"waitStep",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY1 )							--##--
	-- Advance gate source voltage																							--##--
	trigger_gate.addblock.source.action.step(tmName[1], "gateVoltage", infoSMU[2])											--##--
	-- Notify drain that gate voltage has advanced																			--##--
	trigger_gate.addblock.notify(tmName[1],"notify",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY2)							--##--
																															--##--
	-- Wait for notification that drain source voltage has advanced											-- Loop 1 		--##--
	trigger_gate.addblock.wait(tmName[1],"waitMeasure",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY3 )			--##--		--##--
	-- Measure gate i/v																							--##--		--##--
	trigger_gate.addblock.measure(tmName[1],"measure",infoSMU[2],1)												--##--		--##--
	-- Notify drain that measurement has been taken																--##--		--##--
	trigger_gate.addblock.notify(tmName[1],"notify",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY4)				--##--		--##--
	-- Loop back to wait for drain voltage to advance															--##--		--##--
	trigger_gate.addblock.branch.counter(tmName[1], "branch-Measure", "waitMeasure", dSMUsettings[3])		 --##--			--##--
																															--##--
	-- Wait for notification that drain voltage sweep has completed															--##--
	trigger_gate.addblock.wait(tmName[1],"waitSweepDone",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY5 )						--##--
	-- Loop back to wait for drain to begin																					--##--
	trigger_gate.addblock.branch.counter(tmName[1], "branch-Step", "waitStep",  gSMUsettings[3])						 --##--
	trigger_gate.addblock.source.action.bias(tmName[1], "gatebiaszero", infoSMU[2])

--############################################################################################################--

	-- Initiate trigger models and delete when completed
	gateSMU.source.output   = 1
	drainSMU.source.output  = 1
	trigger_gate.initiate(tmName[1])
	trigger_drain.initiate(tmName[2])

	waitcomplete()

	-- Display results from default buffers
	print("Vg\t\t Ig\t\t Vd\t\t Id")
	for j = 1, drainSMU.defbuffer1.n , 1 do
		print(gateSMU.defbuffer2[j],gateSMU.defbuffer1[j],drainSMU.defbuffer2[j],drainSMU.defbuffer1[j])
	end

	gateSMU.source.output   = 0
	drainSMU.source.output  = 0

	trigger_gate.delete(tmName[1])
	trigger_drain.delete(tmName[2])

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
local startVd		= 0
local stopVd		= 2
local noSwpPoints	= 41
local rangeId		= 100e-3
local limitId		= 100e-3
-- Gate Channel Settings
local startVg		= 1.4
local stopVg		= 1.8
local noStpPoints	= 3
local limitIg		= 0.1
-- Measure Settings for both channels
local nplc			= 1
local mDelay		= 0

-- DrainFamilyCurve_VdId_RunTimeEnv({gate_slot,gate_channel,drain_slot,drain_channel},{startVd,stopVd,noSwpPoints,rangeId,limitId},{startVg,stopVg,noStpPoints,limitIg},{nplc,mDelay})

DrainFamilyCurve_VdId_TriggerInOneSlot({common_slot,gate_channel,drain_channel},{startVd,stopVd,noSwpPoints,rangeId,limitId},{startVg,stopVg,noStpPoints,limitIg},{nplc,mDelay},{"tm_vdid"})

--DrainFamilyCurve_VdId_TwoTriggers({gate_slot,gate_channel,drain_slot,drain_channel},{startVd,stopVd,noSwpPoints,rangeId,limitId},{startVg,stopVg,noStpPoints,limitIg},{nplc,mDelay},{"tm_gate","tm_drain"})

