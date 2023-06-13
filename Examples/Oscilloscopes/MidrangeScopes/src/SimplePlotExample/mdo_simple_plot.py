# mdo simple plot
# python v3.x, pyvisa v1.8
# should work with MSO70k, DPO7k, MSO5k, MDO4k, MDO3k, and MSO2k series
# 5/6 Series MSO 

# incompatible with TDS2k and TBS1k series (see tbs simple plot)

import time # std module
import pyvisa as visa # http://github.com/hgrecco/pyvisa
import matplotlib.pyplot as plt # http://matplotlib.org/
import numpy as np # http://www.numpy.org/

visa_address = 'USB0::0x0699::0x0456::C000660::INSTR'

rm = visa.ResourceManager()
scope = rm.open_resource(visa_address)
scope.timeout = 10000 # ms
scope.encoding = 'latin_1'
scope.read_termination = '\n'
scope.write_termination = None
scope.write('*cls') # clear ESR

print(scope.query('*idn?'))

input("""
ACTION:
Connect probe to oscilloscope Channel 1 and the probe compensation signal.

Press Enter to continue...
""")

scope.write('*rst') # reset
t1 = time.perf_counter()
r = scope.query('*opc?') # sync
t2 = time.perf_counter()
print('reset time: {}'.format(t2 - t1))

scope.write('autoset EXECUTE') # autoset
t3 = time.perf_counter()
r = scope.query('*opc?') # sync
t4 = time.perf_counter()
print('autoset time: {} s'.format(t4 - t3))

# io config
scope.write('header 0')
scope.write('data:encdg SRIBINARY')
scope.write('data:source CH1') # channel
scope.write('data:start 1') # first sample
record = int(scope.query('horizontal:recordlength?'))
scope.write('data:stop {}'.format(record)) # last sample
scope.write('wfmoutpre:byt_n 1') # 1 byte per sample

# acq config
scope.write('acquire:state 0') # stop
scope.write('acquire:stopafter SEQUENCE') # single
scope.write('acquire:state 1') # run
t5 = time.perf_counter()
r = scope.query('*opc?') # sync
t6 = time.perf_counter()
print('acquire time: {} s'.format(t6 - t5))

# data query
t7 = time.perf_counter()
bin_wave = scope.query_binary_values('curve?', datatype='b', container=np.array)
t8 = time.perf_counter()
print('transfer time: {} s'.format(t8 - t7))

# retrieve scaling factors
tscale = float(scope.query('wfmoutpre:xincr?'))
tstart = float(scope.query('wfmoutpre:xzero?'))
vscale = float(scope.query('wfmoutpre:ymult?')) # volts / level
voff = float(scope.query('wfmoutpre:yzero?')) # reference voltage
vpos = float(scope.query('wfmoutpre:yoff?')) # reference position (level)

# error checking
r = int(scope.query('*esr?'))
print('event status register: 0b{:08b}'.format(r))
r = scope.query('allev?').strip()
print('all event messages: {}'.format(r))

scope.close()
rm.close()

# create scaled vectors
# horizontal (time)
total_time = tscale * record
tstop = tstart + total_time
scaled_time = np.linspace(tstart, tstop, num=record, endpoint=False)
# vertical (voltage)
unscaled_wave = np.array(bin_wave, dtype='double') # data type conversion
scaled_wave = (unscaled_wave - vpos) * vscale + voff

# plotting
plt.plot(scaled_time, scaled_wave)
plt.title('channel 1') # plot label
plt.xlabel('time (seconds)') # x label
plt.ylabel('voltage (volts)') # y label
print("look for plot window...")
plt.show()

print("\nend of demonstration")

