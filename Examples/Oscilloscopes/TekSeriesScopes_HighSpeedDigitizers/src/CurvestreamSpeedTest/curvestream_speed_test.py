import pyvisa as visa
import time

print("set up VISA connection")

rm = visa.ResourceManager()

scope_address = "TCPIP0::192.168.1.27::inst0::INSTR"

scope = rm.open_resource(scope_address)
scope.timeout = 20000

print(scope.query("*IDN?"))

print("reset scope")
scope.write("*RST")
scope.write("*CLS")

#turn off all the waveform displays
print("turn off waveform display")
scope.write("display:waveform 0")

print("set up scope")

scope.write("hor:mode manual")
scope.write("hor:mode:samplerate 6.25e9")
scope.write("trig:a:level:ch1 1")
scope.write("ch1:sca 1")

scope.write("data:encdg rib")
scope.write("data:width 1")

scope.write("data:source CH1")

#turn on all the channels
for k in range(2,9):
    scope.write("disp:glob:ch{}:state 1".format(k))
scope.write("data:source CH1,CH2,CH3,CH4,CH5,CH6,CH7,CH8")

##for k in range(2,5):
##    scope.write("disp:glob:ch{}:state 1".format(k))
##scope.write("data:source CH1,CH2,CH3,CH4")

#scope.write("disp:glob:ch2:state 1")

#scope.write("data:source CH1,CH2")



print("Begin test...")

record = [1000, 2000, 5000, 10000, 20000, 50000]#, 100000, 200000, 500000, 1000000]

source = scope.query("data:source?")

print("For a source of {}:".format(source))

size = []

for r in record:

    data = []

    scope.write("hor:reco {}".format(r))
    scope.write("data:stop {}".format(r))
    #let settings settle
    time.sleep(1)

    scope.write("curvestream?")

    time_start = time.time()

    while(time.time()-time_start < 10):
        wave = scope.read_raw()
        data.append( wave )

    scope.write("*CLS")

    runs = len(data)
    size.append(len(data[0]))

    print("{} record completed at {} acqs/s and {} record".format(r,runs/10, len(data[0])))

print("Size check: {} {} {}".format(size[0], size[1], size[2]))

scope.close()
rm.close()
