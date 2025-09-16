import pyvisa

def plotResults(x, y):
    import matplotlib.pyplot as pt
    pt.plot(x, y, 'o-')
    pt.xlabel("Time (s)")
    pt.ylabel("Measured Current (A)")
    pt.title("Digital Pulse Generation")
    pt.grid(True)
    pt.show()

# Configure Visa Connection
rm = pyvisa.ResourceManager()
inst = rm.open_resource('TCPIP0::192.168.0.2::5025::SOCKET')
# for using the sockets based implementation
inst.write_termination = "\n"
inst.read_termination = "\n"
inst.send_end = True
inst.timeout = 10000

# SMU Channel Settings 
slot_no = 1
chan_no = 1
smu = f"slot[{slot_no}].smu[{chan_no}]"
# Source Settings
startI		    = 1e-3
stopI 		    = 10e-3
noPoints 	    = 10
limitV 		    = 25
# Measure Settings
measRangeI    	= 100e-3
measRangeV    	= 15
remoteSense 	= "false"

# Pulse Settings
pulsePeriod	    = 5e-3  # pulsePeriod should be longer than pulseWidth + mDelay + apertureTime
pulseWidth	  	= 3e-3
mDelay 		    = 1e-3
apertureTime	= 100e-6

tm_name			= "TM_pulse_digitizer"

script_buffer = [
    # Channel assignment
    f"{smu}.reset()",
    # Source settings
    f"{smu}.source.func              = {smu}.FUNC_DC_CURRENT",
    f"{smu}.source.rangei            = math.max(math.abs({startI}), math.abs({stopI}))",
    f"{smu}.source.limitv            = {limitV}",
    f"{smu}.source.leveli            = 0",
    # Measure settings",
    f"{smu}.measure.rangei           = {measRangeI}",
    f"{smu}.measure.rangev           = {measRangeV}",
    f"{smu}.measure.aperture         = {apertureTime}",
    f"{smu}.measure.autorangev       = 0",

    f"if {remoteSense} then",
    f"    {smu}.sense                = {smu}.SENSE_4WIRE",
    f"else",
    f"    {smu}.sense                = {smu}.SENSE_2WIRE",
    f"end",
    # Buffer clear",
    f"{smu}.defbuffer1.clear()",
    f"{smu}.defbuffer1.appendmode = 1",
    f"{smu}.defbuffer2.clear()",
    f"{smu}.defbuffer2.appendmode = 1",
    # Calculate number of points
    f"nPoints = math.ceil((({pulsePeriod} * {noPoints}) + {pulsePeriod}) / {apertureTime})",

    # Configure trigger model source for linear currrent sweep
    f"{smu}.trigger.source.lineari({startI}, {stopI}, {noPoints})",
    # Set trigger model to measure i/v and store in default buffers
    f"{smu}.trigger.measure.iv({smu}.defbuffer1, {smu}.defbuffer2)",

    # Configure trigger model
    f"triggerModel = slot[{slot_no}].trigger.model",
    f"triggerModel.create(\"{tm_name}\")",
    # Measureoverlapped allows measurements to be taken while trigger model is running in parallel
    f"triggerModel.addblock.measureoverlapped(\"{tm_name}\", \"measure_IV\", {chan_no}, nPoints)",
    f"triggerModel.addblock.delay.constant(\"{tm_name}\", \"prepulse_delay\", {pulsePeriod}/2)",
    # Advance to next current value in current sweep
    f"triggerModel.addblock.source.action.step(\"{tm_name}\", \"sweepI_IV\", {chan_no})",
    f"triggerModel.addblock.delay.constant(\"{tm_name}\", \"meas_pulse_width\", {pulseWidth}, \"sweepI_IV\")",
    # Set source level to 0
    f"triggerModel.addblock.source.action.bias(\"{tm_name}\", \"pulse_bias\", {chan_no})",
    f"triggerModel.addblock.delay.constant(\"{tm_name}\", \"meas_pulse_period\", {pulsePeriod}, \"sweepI_IV\")",
    # Loop through all current sweep values
    f"triggerModel.addblock.branch.counter(\"{tm_name}\", \"branch-counter\", \"sweepI_IV\", {noPoints})",

    # Initiate trigger model, delete when finished
    f"{smu}.source.output = 1",
    f"triggerModel.initiate(\"{tm_name}\")",
    f"waitcomplete()",
    f"{smu}.source.output = 0",
    f"triggerModel.delete(\"{tm_name}\")"
]
inst.write("loadscript pulse")
for cmd in script_buffer:
    inst.write(cmd)
inst.write("endscript")
inst.write("pulse()")

# Retrieve buffer data
timestamps = inst.query(f"printbuffer(1, {smu}.defbuffer1.n, {smu}.defbuffer1.timestamps)").split(",")
timestamps = [float(x) for x in timestamps]
defbuffer1 = inst.query(f"printbuffer(1, {smu}.defbuffer1.n, {smu}.defbuffer1)").split(",")
defbuffer1 = [float(x) for x in defbuffer1]
defbuffer2 = inst.query(f"printbuffer(1, {smu}.defbuffer2.n, {smu}.defbuffer2)").split(",")
defbuffer2 = [float(x) for x in defbuffer2]

# Display buffer data
print("Time","V","I",sep="\t\t")
for i in range(len(defbuffer1)):
    print(f"{timestamps[i]:.5e}",
          f"{defbuffer2[i]:.5e}",
          f"{defbuffer1[i]:.5e}",
          sep="\t"
          )

inst.clear()
inst.close()

plotResults(timestamps, defbuffer1)