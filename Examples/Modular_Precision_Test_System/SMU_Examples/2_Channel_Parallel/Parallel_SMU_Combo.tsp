--[[
################################################################################

Script File: Parallel_SMU_Combo.tsp

    ************************************************************************
    *** Copyright Tektronix, Inc.                                        ***
    *** See www.tek.com/sample-license for licensing terms.              ***
    ************************************************************************

Description:
  This script is example code, which creates (and subsequently calls) several
  functions that can be used with the Model MP5000 Based SMUs to perform a
	voltage sweeping. The purpose is show that you can perform voltage sweeping
  with two channel SMU combination in parallel to increase current. Each SMU
	assigned to one terminal for the high and the other for the low terminal.	
	Upon completion of each test, the data is printed to the TSP Toolkit Console 
	in a format that is suitable for copying and pasting into Microsoft Excel for 
	graphing and analysis.

Required Equipment: 1 Model MP5000 Mainframe 
					          2 channel SMU (MSMU Series)
                    1 Resistive load

Note:  The functions do not perform any error checking.  It is the user's 
       responsibility to specify settings that are compatible with the 
       instrument model being used, and with its power envelope.
       
Note:  It is the user's responsibility to follow all safety guidelines given in 
       the instrument's Reference Manual.  This is especially critical if 
       voltages in excess of 42VDC will be present in the test circuits.  Such 
       voltage levels are hazardous. 
       
Functions created by this script:
    * DC_Vsweep_2CH_Combination_inParallel(infoSMU,{startV,stopV,noPoints,limitI},{measRangeV, measRangeI, autoRangeI, nplc,mDelay,remoteSense})

Example Usage:
    * DC_Vsweep_2CH_Combination_inParallel(infoSMU,{startV,stopV,noPoints,limitI},{measRangeV, measRangeI, autoRangeI, nplc,mDelay,remoteSense})
	
################################################################################
--]]
function DC_Vsweep_2CH_Combination_inParallel(infoSMU,srcSettings,meaSettings)
  function configSMU(assignSMU)
    self = {}
    local total_channel = table.getn(assignSMU)
    print("total channel: ".. total_channel)
    function self.sourceSetting(param,value)
      -- Assign source settings for all channels
      for i=1, total_channel do
        if param == "limiti" then
          -- Divide current limit between channels
          assignSMU[i][1].source[param] = value/total_channel
        else
          assignSMU[i][1].source[param] = value
        end
      end
    end
    function self.measSetting(param,value)
      -- Assign measure settings for all channels
      for i=1, total_channel do
        assignSMU[i][1].measure[param] = value
      end
    end
    function self.generalSetting(param,value)
      -- Assign settings for all channels
      for i=1, total_channel do
        assignSMU[i][1][param] = value
      end
    end  
    function self.measureiv()
      -- Measure i/v on all channels
      local read_v, read_i
      local sum_v = 0
      local sum_i = 0
      for i=1, total_channel do
        read_i , read_v = assignSMU[i][1].measure.iv()
        -- Sum i/v measurements
        sum_v = sum_v + read_v
        sum_i = sum_i + read_i
      end
      -- Divide voltage among channels
      return sum_i, sum_v/total_channel
    end
    function self.reset()
      -- Reset all channels
      for i=1, total_channel do
        assignSMU[i][1].reset()
        assignSMU[i][1].defbuffer1.clear()
        assignSMU[i][1].defbuffer1.appendmode		= 1
        assignSMU[i][1].defbuffer2.clear()
        assignSMU[i][1].defbuffer2.appendmode		= 1
      end
    end
    return self
  end

  combineSMU = configSMU(infoSMU)

  -- Source Settings
  combineSMU.reset()
  combineSMU.sourceSetting("func",slot[1].smu[1].FUNC_DC_VOLTAGE)
  combineSMU.sourceSetting("rangev",math.max(math.abs(srcSettings[1]), math.abs(srcSettings[2])))
  combineSMU.sourceSetting("limiti",srcSettings[4])
  combineSMU.sourceSetting("levelv",0)

  -- Measure Settings
  combineSMU.measSetting("rangev",meaSettings[1])
  combineSMU.measSetting("nplc",meaSettings[4])

  if meaSettings[3] == true then
    combineSMU.measSetting("autorangei",1)
	else
		combineSMU.measSetting("autorangei",0)
    combineSMU.measSetting("rangei",meaSettings[2])
	end
	if meaSettings[6] == true then
    combineSMU.generalSetting("sense",slot[1].smu[1].SENSE_4WIRE)
	else
    combineSMU.generalSetting("sense",slot[1].smu[1].SENSE_2WIRE)
	end	

  -- Calcualte change in voltage for each iteration
	local deltaV = (srcSettings[2] - srcSettings[1])/ (srcSettings[3] - 1)
  -- Turn outputs on
  combineSMU.sourceSetting("output",1)
  combineSMU.sourceSetting("output",1)

	print("I_total\t\t V")
	for j = 1, srcSettings[3] , 1 do
    -- Set voltage source level on all channels
		combineSMU.sourceSetting("levelv", srcSettings[1] + ((j-1) * deltaV))
		delay(meaSettings[5])
    -- Measure i/v on all channels
    print(combineSMU.measureiv())
	end
  -- Turn outputs off
  combineSMU.sourceSetting("output",0)

end

-- No more than two channels should be combined
local infoSMU = { }
  infoSMU[1] = {slot[1].smu[1],1,1}
  infoSMU[2] = {slot[1].smu[2],1,2}

-- Source Settings
local startV 		= 0
local stopV 		= 10
local noPoints  = 6
local limitI 		= 0.2       -- Total current for all channels
-- Measure Settings
local measRangeV 	= 12       
local measRangeI	= 100e-3  -- Same range setting for each range
local autoRangeI 	= true
local nplc 			= 1
local mDelay 		= 0
local remoteSense = false

DC_Vsweep_2CH_Combination_inParallel(infoSMU,{startV,stopV,noPoints,limitI},{measRangeV, measRangeI, autoRangeI, nplc,mDelay,remoteSense})