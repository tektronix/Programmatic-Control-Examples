import time # std module
import visa # http://github.com/hgrecco/pyvisa
import matplotlib.pyplot as plt # http://matplotlib.org/
import numpy as np # http://www.numpy.org/

#input - how many seconds?  n seconds
seconds = int(input("How many seconds to log?"))

results = []

#Connect to scope/VISA

visa_address = 'TCPIP0::192.168.1.20::inst0::INSTR'

rm = visa.ResourceManager()
scope = rm.open_resource(visa_address)
scope.timeout = 10000 # ms
scope.encoding = 'latin_1'
scope.read_termination = '\n'
scope.write_termination = None
scope.write('*cls') # clear ESR

print(scope.query('*idn?'))

#set up scope - autoset
scope.write('*rst') # reset
r = scope.query('*opc?') # sync

scope.write('autoset EXECUTE') # autoset
r = scope.query('*opc?') # sync

scope.write('acquire:state 0') # stop
scope.write('acquire:stopafter SEQUENCE') # single

#set up measurements
scope.write("MEASUREMENT:ADDMEAS FREQUENCY")

for x in range(seconds):

    #acquire
    scope.write('acquire:state 1') # run
    r = scope.query('*opc?') # sync

    #query measurement
    meas = float(scope.query("measu:meas1:resu:curr:mean?"))
    print(meas)

    #wait 1000ms
    time.sleep(1)

    #log result
    results.append(meas)

#loop back to acquire n times

scope.close()
rm.close()

#plot result
plt.plot(range(seconds), results)
plt.title('frequency over time') # plot label
plt.xlabel('time (seconds)') # x label
plt.ylabel('frequency (Hz)') # y label
print("look for plot window...")
plt.show()
