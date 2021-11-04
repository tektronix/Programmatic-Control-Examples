import pyvisa as visa
import time

print("set up VISA connection")

rm = visa.ResourceManager()

scope_address = "TCPIP0::192.168.1.15::inst0::INSTR"

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

scope.write("horizontal:mode manual")
scope.write("horizontal:mode:samplerate 6.25e9")
scope.write("trigger:a:level:ch1 1")
scope.write("ch1:scale 1")

scope.write("data:encdg rib")
scope.write("data:width 1")

scope.write("data:source CH1")

#turn on all the channels
for k in range(2,9):
    scope.write("disp:glob:ch{}:state 1".format(k))
scope.write("data:source CH1,CH2,CH3,CH4,CH5,CH6,CH7,CH8")

#this is in a list so it can iterate if necessary
record = [10000]

print("Begin test...")

source = scope.query("data:source?")

print("For a source of {}:".format(source))

#we'll need this lists for data collection

data = []

#only iterating once for the default demo
#this will matter if you uncomment the optional record assingment above
for r in record:

    scope.write("hor:reco {}".format(r))
    scope.write("data:stop {}".format(r))
    #let settings settle
    time.sleep(1)

    #enter curvestream state
    scope.write("curvestream?")

    #check the time
    time_start = time.time()

    #operate for 10 seconds
    while(time.time()-time_start < 10):
        #for the purposes of demo/speed, get the raw binary with no frills
        wave = scope.read_raw()
        data.append(wave)

    #stop curvestreaming
    scope.write("*CLS")

    #check how many waveforms we got
    wfms = len(data)

    print("{} record completed at {} wfms/s".format(r,wfms*8/10))
    print("{} acquisitions stored in local memory".format(len(data)))

#close the VISA objects
scope.close()
rm.close()
