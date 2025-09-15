--[[
6Ch_Output_Sequence.tsp

This script performs output on and off sequencing using trigger models
]]

-- Set the number of channels you want to use
-- Will include channels from slot 1 first then 2 etc.
--
-- If you wish to skip earlier channels (Ex only use slots 2/3)
-- Be sure to include these in the channel count then simply disable them
-- By updating the enables list  
local Nchannels = 4

-- PSU alias names
local chs = {}
local slots = {}
for i = 1, Nchannels, 1 do
    chs[i] = slot[math.ceil(i/2)].psu[2-math.mod(i,2)]
    slots[math.ceil(i/2)] = slot[math.ceil(i/2)]
end

-- Enable channels (True = enabled, False = disabled)
local enables = {true, true, true, true, false, false}

-----------------------------------------------------------------------------------------
-- configureOutputOnSequence configures a output on sequence for the enabled channels 
-- using a trigger model for each channel.
-- 
-- :param delays: List of delays before each channel turns on. Min: 0s, Max: 2^34s
-- 
-- :return: None
-----------------------------------------------------------------------------------------
local function configureOutputOnSequence(delays)
    -- Create a trigger model for each channel to turn on the output after a specified delay
    for i = 1, Nchannels, 1 do
        if enables[i] then
            slots[math.ceil(i/2)].trigger.model.delete("onCh"..i)   -- Delete trigger models from previous tests
            slots[math.ceil(i/2)].trigger.model.create("onCh"..i)   -- Create trigger model
            slots[math.ceil(i/2)].trigger.model.addblock.wait("onCh"..i,"Wait", trigger.generator[1].EVENT_ID)  -- Wait for trigger generator event
            slots[math.ceil(i/2)].trigger.model.addblock.delay.constant("onCh"..i, "delayTurnOn", delays[i])    -- Delay before turn on
            slots[math.ceil(i/2)].trigger.model.addblock.source.output("onCh"..i, "chOn", 2-math.mod(i,2), 1)   -- urn on channel
        end
    end
end

-----------------------------------------------------------------------------------------
-- outputsOn Turns on the output for on all the enabled channels using the 
-- configured output on sequence.
-- 
-- :return: None
-----------------------------------------------------------------------------------------
local function outputsOn()
    -- Initiate output on seqeuence trigger models
    for i = 1, Nchannels, 1 do
        if enables[i] then
            slots[math.ceil(i/2)].trigger.model.initiate("onCh"..i)
        end
    end
    -- Assert trigger to turn outputs on
    trigger.generator[1].assert()

    waitcomplete()

end

-----------------------------------------------------------------------------------------
-- configureOutputOffSequence configures a output off sequence for the enabled channels 
-- using a trigger model for each channel.
-- 
-- :param delayChannels: List of delays before each channel turns off. Min: 0s, Max: 2^34s
-- 
-- :return: None
-----------------------------------------------------------------------------------------
local function configureOutputOffSequence(delays)
    -- Create a trigger model for each channel to turn off the output after a specified delay
    for i = 1, Nchannels, 1 do
        if enables[i] then
            slots[math.ceil(i/2)].trigger.model.delete("offCh"..i)
            slots[math.ceil(i/2)].trigger.model.create("offCh"..i)
            slots[math.ceil(i/2)].trigger.model.addblock.wait("offCh"..i,"Wait", trigger.generator[1].EVENT_ID)
            slots[math.ceil(i/2)].trigger.model.addblock.delay.constant("offCh"..i, "delayTurnOn", delays[i]) -- delay before turn off
            slots[math.ceil(i/2)].trigger.model.addblock.source.output("offCh"..i, "chOff", 2-math.mod(i,2), 0) -- turn off channel
        end
    end
end

-----------------------------------------------------------------------------------------
-- outputsOff turns on the output for off all the enabled channels using the 
-- configured output off sequence.
--
-- :return: None
-----------------------------------------------------------------------------------------
local function outputsOff()
    -- Initiate output on seqeuence trigger models
    for i = 1, Nchannels, 1 do
        if enables[i] then
            slots[math.ceil(i/2)].trigger.model.initiate("offCh"..i)
        end
    end
    -- Assert trigger to turn outputs off
    trigger.generator[1].assert()

    waitcomplete()
end

-- Set voltage level and current limit for all channels
local v_level = 5
local i_limit = 5
local slewrate = 10000

for i = 1, Nchannels, 1 do
    if enables[i] then
        chs[i].source.levelv = v_level
        chs[i].source.limiti = i_limit
        chs[i].source.slewratev = slewrate
    end
end

-- On Delays
local onDelays = {
    0.000,
    0.005,
    0.010,
    0.015,
    0.000,
    0.000
}

-- Off Delays
local offDelays = {
    0.015,
    0.010,
    0.005,
    0.000,
    0.000,
    0.000
}

local onTime = 0.01 -- Time for Channels to be On

configureOutputOnSequence(onDelays)     -- Configure output on sequence

configureOutputOffSequence(offDelays)   -- Configure output off sequence

outputsOn()     -- Turn outputs on using trigger models

delay(onTime)

outputsOff()    -- Turn outputs off using trigger models
