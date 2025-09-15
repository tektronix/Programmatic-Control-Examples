
--[[
################################################################################

Script File: Laser_VSCEL.tsp

    ************************************************************************
    *** Copyright Tektronix, Inc.                                        ***
    *** See www.tek.com/sample-license for licensing terms.              ***
    ************************************************************************

Description:
    This script is example code, which creates (and subsequently calls) several
    functions that can be used with the Model MP5000 Based SMUs to perform a
	current sweeping. The purpose is show that you can perform a laser/VCLSE device
	characterization with the SMUs. As written, one channel of SMU is assigned to 
	the anode for the high and cathode for the low terminal. the high of the other SMU
	is assigned to the high of a PD anode and the low is to cathod. One channels performs
	current sweeping on the laser/or VCSEL measuring voltage and current. The other channel
	keeps a constanst voltage bias measurement current of the PD device. This test provides
	three different scripts. One is DC sweep measurement in run time environment. The second
	is still DC test tested in trigger model. The third is a pulse test in trigger model. 
	This feature gives a lot of convience and speed in LED sequence test. 
	Upon completion of each test, the data is printed to the TSP Toolkit Console 
	in a format that is suitable for copying and pasting into Microsoft Excel for 
	graphing and analysis.

Required Equipment: 1 Model MP5000 Mainframe 
					2 channel SMU 
					1 Laser/VSCEL unit

Note:  The functions do not perform any error checking.  It is the user's 
       responsibility to specify settings that are compatible with the 
       instrument model being used, and with its power envelope.
       
Note:  It is the user's responsibility to follow all safety guidelines given in 
       the instrument's Reference Manual.  This is especially critical if 
       voltages in excess of 42VDC will be present in the test circuits.  Such 
       voltage levels are hazardous. 
       
Functions created by this script:
    * DC_Laser_VCSEL_LIV_RunTimeEnv({IF_slot,IF_channel,PD_slot,PD_channel},{startIF,stopIF,noPoints, rangeI, limitV,measRangeV},{biasV_PD,srcRangeV_PD,measRangeI_PD},{nplc,mDelay, remoteSense})
	* DC_Laser_VCSEL_LIV_inTriggerModel({IF_slot,IF_channel,PD_slot,PD_channel},{startIF,stopIF,noPoints, rangeI, limitV,measRangeV},{biasV_PD,srcRangeV_PD,measRangeI_PD},{nplc,mDelay, remoteSense},{"tm_if","tm_pd"})
	* Pulse_Laser_VCSEL_LIV_inTriggerModel({IF_slot,IF_channel,PD_slot,PD_channel},{startIF,stopIF,noPoints, rangeI, limitV,measRangeV},{biasV_PD,srcRangeV_PD,measRangeI_PD},{nplc,remoteSense},{pulsePeriod,pulseWidth,mDelay,apertureTime},{"tm_if","tm_pd"})

Example Usage:
   	* DC_Laser_VCSEL_LIV_RunTimeEnv({1,1,1,2},{0,100e-3,11, 100e-3, 6,6},{0,6,6},{1,0, false})
	* DC_Laser_VCSEL_LIV_inTriggerModel({1,1,1,2},{0,100e-3,11, 100e-3, 6,6},{0,6,6},{1,0, false},{"tm_if","tm_pd"})
	* Pulse_Laser_VCSEL_LIV_inTriggerModel({1,1,1,2},{0,100e-3,11, 100e-3, 6,6},{0,6,6},{0,false},{5e-3,3e-3,0,1e-3},{"tm_if","tm_pd"})
	
################################################################################
--]]

function DC_Laser_VCSEL_LIV_RunTimeEnv(infoSMU,IF_Settings,PD_Settings, meaSettings)
	-- SMU channel assignment
	local IF_SMU 							= slot[infoSMU[1]].smu[infoSMU[2]]
	local PD_SMU 							= slot[infoSMU[3]].smu[infoSMU[4]]
	local smu_id 							= {IF_SMU, PD_SMU}

	-- Configure all channels
	for i = 1, 2 do
		smu_id[i].reset()
		-- Buffer clear
		smu_id[i].defbuffer1.clear()
		smu_id[i].defbuffer1.appendmode		= 1
		smu_id[i].defbuffer2.clear()
		smu_id[i].defbuffer2.appendmode		= 1
		if smu_id[i] == IF_SMU then
			-- Source Settings
			smu_id[i].source.func			= smu_id[i].FUNC_DC_CURRENT
			smu_id[i].source.rangei			= IF_Settings[4]
			smu_id[i].source.leveli			= 0
			smu_id[i].source.limitv			= IF_Settings[5]
			-- Measure Settings
			smu_id[i].measure.rangev		= IF_Settings[6]
			smu_id[i].measure.rangei		= IF_Settings[4]
		else
			-- Source Settings
			smu_id[i].source.func			= smu_id[i].FUNC_DC_VOLTAGE
			smu_id[i].source.rangev			= PD_Settings[2]
			smu_id[i].source.levelv			= PD_Settings[1]
			-- Measure Settings
			smu_id[i].measure.rangei		= PD_Settings[3]
		end

		smu_id[i].measure.nplc				= meaSettings[1]
		if meaSettings[3] == true then
			smu_id[i].sense					= smu_id[i].SENSE_4WIRE
		else
			smu_id[i].sense					= smu_id[i].SENSE_2WIRE
		end
	end

	-- Calculate current change per iteration
	local deltaIF = (IF_Settings[2] - IF_Settings[1])/ (IF_Settings[3] - 1)
	IF_SMU.source.output 					= 1
	IF_SMU.source.output 					= 1
	PD_SMU.source.output					= 1
	PD_SMU.source.output 					= 1
	PD_SMU.source.levelv					= PD_Settings[1]

	print("IF\t\t VF\t\t I_PD \t\t V_PD")
	for j = 1, IF_Settings[3] , 1 do
		-- Set current source level
		IF_SMU.source.leveli = IF_Settings[1] + ((j-1) * deltaIF)
		delay(meaSettings[2])
		-- Measure i/v for both Source and PD, store in default buffers
		IF_SMU.measure.iv(IF_SMU.defbuffer1, IF_SMU.defbuffer2)
		PD_SMU.measure.iv(PD_SMU.defbuffer1, PD_SMU.defbuffer2)
		-- Display results
		print(IF_SMU.defbuffer1[j],IF_SMU.defbuffer2[j],PD_SMU.defbuffer1[j],PD_SMU.defbuffer2[j])
	end

	IF_SMU.source.output 					= 0
	PD_SMU.source.output 					= 0

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

function DC_Laser_VCSEL_LIV_inTriggerModel(infoSMU,IF_Settings,PD_Settings, meaSettings,tmName)
	-- SMU channel assignment
	local IF_SMU 							= slot[infoSMU[1]].smu[infoSMU[2]]
	local PD_SMU 							= slot[infoSMU[3]].smu[infoSMU[4]]
	local smu_id 							= {IF_SMU, PD_SMU}

	-- Configure all channels
	for i = 1, 2 do
		smu_id[i].reset()
		-- Buffer clear
		smu_id[i].defbuffer1.clear()
		smu_id[i].defbuffer1.appendmode		= 1
		smu_id[i].defbuffer2.clear()
		smu_id[i].defbuffer2.appendmode		= 1
		if smu_id[i] == IF_SMU then
			-- Source Settings
			smu_id[i].source.func			= smu_id[i].FUNC_DC_CURRENT
			smu_id[i].source.rangei			= IF_Settings[4]
			smu_id[i].source.leveli			= 0
			smu_id[i].source.limitv			= IF_Settings[5]
			-- Measure Settings
			smu_id[i].measure.rangev		= IF_Settings[6]
			smu_id[i].measure.rangei		= IF_Settings[4]
		else
			-- Source Settings
			smu_id[i].source.func			= smu_id[i].FUNC_DC_VOLTAGE
			smu_id[i].source.rangev			= PD_Settings[2]
			smu_id[i].source.levelv			= PD_Settings[1]
			-- Measure Settings
			smu_id[i].measure.rangei		= PD_Settings[3]
		end

		smu_id[i].measure.nplc				= meaSettings[1]
		if meaSettings[3] == true then
			smu_id[i].sense					= smu_id[i].SENSE_4WIRE
		else
			smu_id[i].sense					= smu_id[i].SENSE_2WIRE
		end
	end

--####################################### Source channel trigger model #######################################--
--############################################################################################################--

	-- Setup trigger model source for linear current sweep
	IF_SMU.trigger.source.lineari(IF_Settings[1], IF_Settings[2], IF_Settings[3])
	-- Set trigger model to measure i/v and store in default buffers
	IF_SMU.trigger.measure.iv(IF_SMU.defbuffer1,IF_SMU.defbuffer2)

	local trigger_IF = slot[infoSMU[1]].trigger.model
	trigger_IF.create(tmName[1])

	-- Notify PD trigger model to begin
	trigger_IF.addblock.notify(tmName[1],"notifyPDStep",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY1)

	-- Wait for response from PD trigger model
	trigger_IF.addblock.wait(tmName[1],"waitPDStep",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY2 )
	-- Advance to next source value																	--Loop 1
	trigger_IF.addblock.source.action.step(tmName[1], "IF_sweep", infoSMU[2])							--##--
	trigger_IF.addblock.delay.constant(tmName[1],"meaDelay",meaSettings[2],"IF_sweep")					--##--
	-- Notify PD trigger model that step and wait are complete											--##--
	trigger_IF.addblock.notify(tmName[1],"notify",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY3)			--##--
	-- Measure iv on source terminals																	--##--
	trigger_IF.addblock.measure(tmName[1], "measure", infoSMU[2], 1)									--##--
																										--##--
	-- Wait for measurement completed notification														--##--
	trigger_IF.addblock.wait(tmName[1],"wait",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY4 )			--##--
	-- Loop back to advancing source current															--##--
	trigger_IF.addblock.branch.counter(tmName[1], "IF_branch", "IF_sweep", IF_Settings[3])			 --##--
	-- Notify PD trigger model that current sweep is completed
	trigger_IF.addblock.notify(tmName[1],"notifySweepDone",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY5)	
	trigger_IF.addblock.source.action.bias(tmName[1], "IF_bias", infoSMU[2])

--######################################### PD channel trigger model #########################################--
--############################################################################################################--

	-- Setup trigger model source for linear voltage sweep 
	-- (voltage sweep is only one value so will stay constant through test)
	PD_SMU.trigger.source.linearv(PD_Settings[1], PD_Settings[1], 1)
	-- Set trigger model to measure i/v and store in default buffers
	PD_SMU.trigger.measure.iv(PD_SMU.defbuffer1,PD_SMU.defbuffer2)

	local trigger_PD = slot[infoSMU[3]].trigger.model
	trigger_PD.create(tmName[2])

	-- Wait for initiation from source trigger model
	trigger_PD.addblock.wait(tmName[2],"waitStep",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY1 )
	-- Advance to next source value
	trigger_PD.addblock.source.action.step(tmName[2], "bias_PD", infoSMU[4])
	-- Notify source trigger model that source has been stepped
	trigger_PD.addblock.notify(tmName[2],"notifyStep",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY2)

	-- Wait for notification of completion from source trigger model								--Loop 1
	trigger_PD.addblock.wait(tmName[2],"waitMeas",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY3 )		--##--
	trigger_PD.addblock.delay.constant(tmName[2],"meaDelay",meaSettings[2])								--##--
	-- Measure iv on PD terminals																		--##--
	trigger_PD.addblock.measure(tmName[2], "measure", infoSMU[4], 1)									--##--
	-- Notify source trigger model that measurement is completed										--##--
	trigger_PD.addblock.notify(tmName[2],"notify",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY4)			--##--
	-- Loop back and wait for notification from source trigger model									--##--
	trigger_PD.addblock.branch.counter(tmName[2], "branch-PD", "waitMeas", IF_Settings[3])			 --##--

	-- Wait for notification that source trigger model is completed
	trigger_PD.addblock.wait(tmName[2],"waitPDDone",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY5 )
	-- Set source to 0
	trigger_PD.addblock.source.action.bias(tmName[2], "PDzero", infoSMU[4])

--############################################################################################################--

	-- Initiate trigger models, delete when completed
	IF_SMU.source.output 				= 1
	IF_SMU.source.output 				= 1
	PD_SMU.source.output				= 1
	PD_SMU.source.output 				= 1
	PD_SMU.source.levelv				= PD_Settings[1]

	trigger_PD.initiate(tmName[2])
	trigger_IF.initiate(tmName[1])

	waitcomplete()
	IF_SMU.source.output 				= 0
	PD_SMU.source.output 				= 0

	trigger_IF.delete(tmName[1])	
	trigger_PD.delete(tmName[2])	

	-- Display default buffer readings
	print("IF\t\t VF\t\t I_PD \t\t V_PD")
	for j = 1, IF_SMU.defbuffer1.n , 1 do
		print(IF_SMU.defbuffer1[j],IF_SMU.defbuffer2[j],PD_SMU.defbuffer1[j],PD_SMU.defbuffer2[j])
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

function Pulse_Laser_VCSEL_LIV_inTriggerModel(infoSMU,IF_Settings,PD_Settings, meaSettings,pulseSettings,tmName)
	-- SMU channel assignment
	local IF_SMU 							= slot[infoSMU[1]].smu[infoSMU[2]]
	local PD_SMU 							= slot[infoSMU[3]].smu[infoSMU[4]]
	local smu_id 							= {IF_SMU, PD_SMU}

	for i = 1, 2 do
		smu_id[i].reset()
		-- Buffer clear
		smu_id[i].defbuffer1.clear()
		smu_id[i].defbuffer1.appendmode		= 1
		smu_id[i].defbuffer2.clear()
		smu_id[i].defbuffer2.appendmode		= 1
		if smu_id[i] == IF_SMU then
			-- Source Settings
			smu_id[i].source.func			= smu_id[i].FUNC_DC_CURRENT
			smu_id[i].source.rangei			= IF_Settings[4]
			smu_id[i].source.leveli			= 0
			smu_id[i].source.limitv			= IF_Settings[5]
			-- Measure Settings
			smu_id[i].measure.rangev		= IF_Settings[6]
			smu_id[i].measure.rangei		= IF_Settings[4]
		else
			-- Source Settings
			smu_id[i].source.func			= smu_id[i].FUNC_DC_VOLTAGE
			smu_id[i].source.rangev			= PD_Settings[2]
			smu_id[i].source.levelv			= PD_Settings[1]
			-- Measure Settings
			smu_id[i].measure.rangei		= PD_Settings[3]
		end

		smu_id[i].measure.aperture			= pulseSettings[3]
		if meaSettings[2] == true then
			smu_id[i].sense					= smu_id[i].SENSE_4WIRE
		else
			smu_id[i].sense					= smu_id[i].SENSE_2WIRE
		end
	end

--####################################### Source channel trigger model #######################################--
--############################################################################################################--

	-- Configure trigger model for linear current sweep
	IF_SMU.trigger.source.lineari(IF_Settings[1], IF_Settings[2], IF_Settings[3])
	-- Set trigger model to measure i/v and store in default buffers
	IF_SMU.trigger.measure.iv(IF_SMU.defbuffer1,IF_SMU.defbuffer2)

	local trigger_IF = slot[infoSMU[1]].trigger.model
	trigger_IF.create(tmName[1]) 

	-- Notify PD trigger model to begin
	trigger_IF.addblock.notify(tmName[1],"notifyPDStep",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY1)

	-- Wait for PD channel to advance to next source value
	trigger_IF.addblock.wait(tmName[1],"waitPDStep",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY2 )
	-- Advance to next current value in sweep														--Loop 1
	trigger_IF.addblock.source.action.step(tmName[1], "IF_sweep", infoSMU[2])							--##--
	trigger_IF.addblock.delay.constant(tmName[1],"meaDelay",meaSettings[1],"IF_sweep")					--##--
	-- Notify PD trigger model that current value has advanced											--##--
	trigger_IF.addblock.notify(tmName[1],"notify",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY3)			--##--
	-- Measure source channel i/v																		--##--
	trigger_IF.addblock.measure(tmName[1], "measure", infoSMU[2], 1)									--##--
																										--##--
	-- Wait for notification that PD channel has been measured											--##--
	trigger_IF.addblock.wait(tmName[1],"wait",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY4 )			--##--
	trigger_IF.addblock.delay.constant(tmName[1],"pulse_width",pulseSettings[2],"IF_sweep")				--##--
	-- Set source value back to 0																		--##--
	trigger_IF.addblock.source.action.bias(tmName[1], "IF_off", infoSMU[2])								--##--
	trigger_IF.addblock.delay.constant(tmName[1],"pulse_period",pulseSettings[1],"IF_sweep")			--##--
	-- Loop back to advance source current																--##--
	trigger_IF.addblock.branch.counter(tmName[1], "IF_branch", "IF_sweep", IF_Settings[3])			 --##--
	-- Notify PD channel that sweep has completed
	trigger_IF.addblock.notify(tmName[1],"notifySweepDone",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY5)	
	trigger_IF.addblock.source.action.bias(tmName[1], "IF_bias", infoSMU[2])

--######################################### PD channel trigger model #########################################--
--############################################################################################################--

	-- Setup trigger model source for linear voltage sweep 
	-- (voltage sweep is only one value so will stay constant through test)
	PD_SMU.trigger.source.linearv(PD_Settings[1], PD_Settings[1], 1)
	-- Set trigger model to measure i/v and store in default buffers
	PD_SMU.trigger.measure.iv(PD_SMU.defbuffer1,PD_SMU.defbuffer2)

	local trigger_PD = slot[infoSMU[3]].trigger.model
	trigger_PD.create(tmName[2])

	-- Wait for source trigger model to begin
	trigger_PD.addblock.wait(tmName[2],"waitStep",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY1 )
	-- Advance to next source value in sweep
	trigger_PD.addblock.source.action.step(tmName[2], "bias_PD", infoSMU[4])
	-- Notify source that voltage value has been advanced
	trigger_PD.addblock.notify(tmName[2],"notifyStep",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY2)

	-- Wait for source trigger model to advance source current										--Loop 1
	trigger_PD.addblock.wait(tmName[2],"waitMeas",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY3 )		--##--
	-- Measure i/v on PD channel																		--##--
	trigger_PD.addblock.measure(tmName[2], "measure", infoSMU[4], 1)									--##--
	-- Notify source trigger model that measurement has been completed									--##--
	trigger_PD.addblock.notify(tmName[2],"notify",slot[infoSMU[3]].trigger.model.EVENT_NOTIFY4)			--##--
	-- Loop back to wait for notification from source trigger model										--##--
	trigger_PD.addblock.branch.counter(tmName[2], "branch-PD", "waitMeas", IF_Settings[3])			 --##--

	-- Wait for notification from source that the sweep has been completed
	trigger_PD.addblock.wait(tmName[2],"waitPDDone",slot[infoSMU[1]].trigger.model.EVENT_NOTIFY5 )
	trigger_PD.addblock.source.action.bias(tmName[2], "PDzero", infoSMU[4])

--############################################################################################################--

	-- Initiate trigger model, delete when finished
	IF_SMU.source.output 				= 1
	IF_SMU.source.output 				= 1
	PD_SMU.source.output				= 1
	PD_SMU.source.output 				= 1
	PD_SMU.source.levelv				= PD_Settings[1]

	trigger_PD.initiate(tmName[2])
	trigger_IF.initiate(tmName[1])

	waitcomplete()
	IF_SMU.source.output 				= 0
	PD_SMU.source.output 				= 0

	trigger_IF.delete(tmName[1])	
	trigger_PD.delete(tmName[2])	

	-- Display contents of measurement buffers
	print("IF\t\t VF\t\t I_PD \t\t V_PD")
	for j = 1, IF_SMU.defbuffer1.n , 1 do
		print(IF_SMU.defbuffer1[j],IF_SMU.defbuffer2[j],PD_SMU.defbuffer1[j],PD_SMU.defbuffer2[j])
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
local IF_slot 		= 1
local IF_channel 	= 1
local PD_slot 		= 1
local PD_channel 	= 2

-- IF Settings
local startIF 		= 0
local stopIF 		= 100e-3
local noPoints 		= 60
local rangeI 		= 1000e-3
local limitV 		= 6
local measRangeV	= 6

-- PD Source Measure Settings
local biasV_PD 		= 0
local srcRangeV_PD 	= 6
local measRangeI_PD = 10e-3
-- Mesaure Settings
local nplc 			= 1
local mDelay 		= 1e-3
local remoteSense 	= false

-- Pulse Settings
local pulsePeriod	= 5e-3  -- pulsePeriod should be longer than pulseWidth + mDelay + apertureTime
local pulseWidth	= 3e-3
local apertureTime	= 1e-3


--DC_Laser_VCSEL_LIV_RunTimeEnv({IF_slot,IF_channel,PD_slot,PD_channel},{startIF,stopIF,noPoints, rangeI, limitV,measRangeV},{biasV_PD,srcRangeV_PD,measRangeI_PD},{nplc,mDelay, remoteSense})
--DC_Laser_VCSEL_LIV_inTriggerModel({IF_slot,IF_channel,PD_slot,PD_channel},{startIF,stopIF,noPoints, rangeI, limitV,measRangeV},{biasV_PD,srcRangeV_PD,measRangeI_PD},{nplc,mDelay, remoteSense},{"tm_if","tm_pd"})
Pulse_Laser_VCSEL_LIV_inTriggerModel({IF_slot,IF_channel,PD_slot,PD_channel},{startIF,stopIF,noPoints, rangeI, limitV,measRangeV},{biasV_PD,srcRangeV_PD,measRangeI_PD},{mDelay,remoteSense},{pulsePeriod,pulseWidth,apertureTime},{"tm_if","tm_pd"})



