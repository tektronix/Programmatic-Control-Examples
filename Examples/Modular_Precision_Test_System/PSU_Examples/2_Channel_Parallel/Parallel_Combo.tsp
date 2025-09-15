-- Alais SMU
local slot_no = 2
local psu1 = slot[slot_no].psu[1]
local psu2 = slot[slot_no].psu[2]
-- Source settings
local v_level = 20
local i_level = 300e-3
local i_limit = 350e-3
-- Reset psu's
psu1.reset()
psu2.reset()
-- Clear all buffers
psu1.defbuffer1.clear()
psu1.defbuffer2.clear()
psu2.defbuffer1.clear()
psu2.defbuffer2.clear()
-- Setup buffers for trigger model measurements
psu1.trigger.measure.iv(psu1.defbuffer1, psu1.defbuffer2)
psu2.trigger.measure.iv(psu2.defbuffer1, psu2.defbuffer2)

-- Configure psu source settings
-- To avoid channels sinking eachother one channel 
-- has a higher levelv and the other has a higher current limit
psu1.source.levelv = v_level+100e-3
psu2.source.levelv = v_level
psu1.source.limiti = i_level/2
psu2.source.limiti = i_level/2 + (i_limit-i_level)

-- Create a trigger model to turn channels on/off at same time
local tm_name = "tm"
local triggerModel = slot[slot_no].trigger.model
triggerModel.create(tm_name)
triggerModel.addblock.source.output(tm_name, "outputs-on", {1,2}, 1)
triggerModel.addblock.delay.constant(tm_name, "delay1", 10e-3)
triggerModel.addblock.measure(tm_name, "measure", {1,2}, 20)
triggerModel.addblock.delay.constant(tm_name, "delay2", 10e-3)
triggerModel.addblock.source.output(tm_name, "outputs-off", {1,2}, 0)

-- Initiate trigger model and delete
triggerModel.initiate(tm_name)
waitcomplete()
triggerModel.delete(tm_name)

-- Display measurements to terminal
print("V1\t\t I1\t\t V2\t\t I2")
for i=1, psu1.defbuffer1.n do
    print(psu1.defbuffer2[i], psu1.defbuffer1[i], psu2.defbuffer2[i], psu2.defbuffer1[i])
end