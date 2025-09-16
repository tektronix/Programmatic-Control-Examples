-- SMU Channel Settings 
local slot_no = 1
local chan_no = 1
-- Source Settings
local startI		    = 1e-3
local stopI 		    = 10e-3
local noPoints 	    	= 10
local limitV 		    = 25
-- Measure Settings
local measRangeI    	= 100e-3
local measRangeV    	= 15
local remoteSense 		= false

-- Pulse Settings
local pulsePeriod	  	= 5e-3  -- pulsePeriod should be longer than pulseWidth + mDelay + apertureTime
local pulseWidth	  	= 3e-3
local mDelay 		    = 1e-3
local apertureTime		= 100e-6

local tm_name			= "TM_pulse_digitizer"

-- Channel assignment
local sweepI_SMU = slot[slot_no].smu[chan_no]
sweepI_SMU.reset()
-- Source settings
sweepI_SMU.source.func              = sweepI_SMU.FUNC_DC_CURRENT
sweepI_SMU.source.rangei            = math.max(math.abs(startI), math.abs(stopI))
sweepI_SMU.source.limitv            = limitV
sweepI_SMU.source.leveli            = 0
-- Measure settings
sweepI_SMU.measure.rangei           = measRangeI
sweepI_SMU.measure.rangev           = measRangeV
sweepI_SMU.measure.aperture         = apertureTime
sweepI_SMU.measure.autorangev       = 0

if remoteSense then
    sweepI_SMU.sense                = sweepI_SMU.SENSE_4WIRE
else
    sweepI_SMU.sense                = sweepI_SMU.SENSE_2WIRE
end
-- Buffer clear
sweepI_SMU.defbuffer1.clear()
sweepI_SMU.defbuffer1.appendmode    = 1
sweepI_SMU.defbuffer2.clear()
sweepI_SMU.defbuffer2.appendmode	= 1
-- Calculate number of points
local nPoints = math.ceil(((pulsePeriod * noPoints) + pulsePeriod) / apertureTime)

-- Configure trigger model source for linear currrent sweep
sweepI_SMU.trigger.source.lineari(startI, stopI, noPoints)
-- Set trigger model to measure i/v and store in default buffers
sweepI_SMU.trigger.measure.iv(sweepI_SMU.defbuffer1, sweepI_SMU.defbuffer2)

-- Configure trigger model
local triggerModel = slot[slot_no].trigger.model
triggerModel.create(tm_name)
-- Measureoverlapped allows measurements to be taken while trigger model is running in parallel
triggerModel.addblock.measureoverlapped(tm_name, "measure_IV", chan_no, nPoints)
triggerModel.addblock.delay.constant(tm_name, "prepulse_delay", pulsePeriod/2)
-- Advance to next current value in current sweep
triggerModel.addblock.source.action.step(tm_name, "sweepI_IV", chan_no)
triggerModel.addblock.delay.constant(tm_name, "meas_pulse_width", pulseWidth, "sweepI_IV")
-- Set source level to 0
triggerModel.addblock.source.action.bias(tm_name, "pulse_bias", chan_no)
triggerModel.addblock.delay.constant(tm_name, "meas_pulse_period", pulsePeriod, "sweepI_IV")
-- Loop through all current sweep values
triggerModel.addblock.branch.counter(tm_name, "branch-counter", "sweepI_IV", noPoints)

-- Initiate trigger model, delete when finished
sweepI_SMU.source.output = 1
triggerModel.initiate(tm_name)
waitcomplete()
sweepI_SMU.source.output = 0
triggerModel.delete(tm_name)

-- Retrieve values from buffers and display
print("Time\t\t V\t\t I")
for j = 1, sweepI_SMU.defbuffer1.n, 1 do
    print(sweepI_SMU.defbuffer1.timestamps[j], sweepI_SMU.defbuffer2[j], sweepI_SMU.defbuffer1[j])
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