-----------------------------------------------------------------------------------------
-- This script toggles outputs with varying slewrates to demonstrate this feature. 
-- This is best paired with a scope to capture the  effects. 
-----------------------------------------------------------------------------------------
---
reset()

-- Alais PSU
local moduleSlot = slot[2]
local module = moduleSlot.psu[1]

-- Set voltage and current limits for each channel
module.source.levelv = 5.0
module.source.limiti = 1.0

-- Slewrate of 1 v/s
module.source.slewratev = 1


-- Turn on each channel with delays
delay(0.0)  -- Delay for chan_1
module.source.output = moduleSlot.psu.ON

-- Wait for 1 seconds
delay(1)

-- Turn off each channel
module.source.output = moduleSlot.psu.OFF

-- Set voltage and current limits again
module.source.levelv = 5.0 
module.source.limiti = 1.0

-- Slewrate of 10000 v/s
module.source.slewratev = 10000

-- Turn on output with delays again
delay(1)
module.source.output = moduleSlot.psu.ON

-- Wait for 1 seconds
delay(1)

-- Turn off outputs
module.source.output = moduleSlot.psu.OFF
