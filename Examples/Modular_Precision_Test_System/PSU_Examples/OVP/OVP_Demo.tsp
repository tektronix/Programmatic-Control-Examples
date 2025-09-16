local psu = slot[2].psu[1]

local v_start = 5.0
local v_end = 20
local i_start = 1
local i_end = 2
local ovp_level = 12
local ocp_level = 5.5

reset()

-- Configure Channel
psu.source.levelv = v_start
psu.source.limiti = i_start

-- Configure Protect
psu.source.protect.levelv = ovp_level
psu.source.protect.leveli = ocp_level

-- delay
delay(2.5)

-- Turn output on to trigger OVP
psu.source.output = 1

-- Configure Channel to higher level"
psu.source.levelv = v_end
psu.source.limiti = i_end