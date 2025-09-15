--[[ 
Purpose:

This demo showcases the bipolar capabilities of the MP5000 power supply unit (PSU). 
Unlike many power supplies that require recabling (switching HI and LO) to transition 
from sourcing positive to negative voltage, the MP5000 can achieve this seamlessly 
due to its bipolar functionality. This demo illustrates that with its bipolar capabilities, 
both the Forward Voltage and Reverse Zener Voltage can be tested without the need for recabling.
]]

--////////////////////////////////////////////////////////////////////

-- UPDATE THE FOLLOWING
slotNumber = 2 -- The slot number where your PSU is located
slotChannel = 2 -- The channel you are using on your PSU

--///////////////////////////////////////////////////////////////////

-- Begin by configuring the PSU for Forward Bias:
-- Set Voltage Source Level = 1.5 V
-- Set Current Limit = 1 A

local psu = slot[slotNumber].psu[slotChannel]
psu.source.limiti = 1
psu.source.levelv = 1.5

-- Turn output on
psu.source.output = 1 

-- Store the voltage and then print out the voltage reading for 1.5 volts set as the Voltage Source Level
local voltageReading = psu.measure.v()
print("Set 1.5V Measured: " .. voltageReading) 


--UPDATE IF USING DIFFERENT DIODE
psu.source.limiti = 0.065 -- Change current limit
psu.source.levelv = -25 -- Change Source Voltage Level


-- Store the voltage and then print out the voltage reading for -25 volts set as the Voltage Source Level
local voltageReading2 = psu.measure.v()
print("Set ".. psu.source.levelv .."V Measured: " .. voltageReading2) 

-- Turn off output
psu.source.output = 0
