--[[
    Example code below is intended to demonstrate how to take voltage and current readings
    and increase voltage through trials. set_channel configures the PSU for this sweep.

    ***  slot[modSlot].psu[modChan] defines the module slot "modSlot" and channel "modChan" for which the function is being called   ***
]]
function set_channel(modSlot, modChan, volt, curr)
    local psu = slot[modSlot].psu[modChan]
    psu.source.levelv = volt -- sets voltage level 
    psu.source.limiti = curr -- sets current limit 

    psu.source.output = slot[modSlot].psu.ON -- turns Output 

    voltageVal = psu.measure.v()   -- measures the voltage level  
    currentVal = psu.measure.i()   -- measures the current level

    print("Module 1/Channel 1:\nVoltage Reading:", voltageVal, "\nCurrent Reading:", currentVal) -- return readings

    psu.source.output = slot[modSlot].psu.OFF -- turn output OFF
end


--[[
    The example below will perform a linear voltage sweep

    PARAMETERS  -   
                modSlot : Module for given DUT
                modChan : Channel for given DUT
                start : starting value of voltage sweep
                stop :  stoping value of voltage sweep
                step :  step increment size
                setCurr : Programmed current limit

]]

function doSweep(modSlot, modChan, start, stop, step, setCurr)
    -- Alais PSU
    local psu = slot[modSlot].psu[modChan]
    -- Reset PSU 
    slot[modSlot].psu[modChan].reset()
    -- Configure source settings and turn output on
    psu.source.levelv = 0
    psu.source.limiti = setCurr
    psu.source.output = slot[modSlot].psu.ON 

    local voltageVal
    local currentVal

    -- Iterate through linear sweep voltage values
    for v = start, stop, step do
        psu.source.levelv = v
        delay(1) -- Constant 1 second delay
        print(string.format("\n\nSet Voltage: %.3f Set Current: %.3f", v, setCurr)) -- Output settings
        -- Take measurements
        voltageVal = slot[modSlot].psu[modChan].measure.v()     
        currentVal = slot[modSlot].psu[modChan].measure.i()  
        print(string.format("Module %d/Channel %d:\nVoltage Reading: %.3f \nCurrent Reading: %.3f", modSlot, modChan, voltageVal, currentVal)) -- Output readings
    end
    -- End test
    psu.source.output = slot[modSlot].psu.OFF
    print("\nDone")
end


doSweep(2, 2, 0.5, 5, 0.5, 1) -- UPDATE THIS LINE IF YOU WISH TO CHANGE THE SWEEP