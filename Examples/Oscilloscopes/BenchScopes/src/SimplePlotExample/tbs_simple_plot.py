# tbs simple plot
# python v3.x, pyvisa v1.8
# should work with TDS2k, TPS2k, and TBS1k series

# replaced 'wfmoutpre' with 'wfmpre' (see mdo simple plot)

import time # std module
import visa # http://github.com/hgrecco/pyvisa
import pylab as pl # http://matplotlib.org/
import numpy as np # http://www.numpy.org/

visa_address = 'ASRL1::INSTR'

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
print('reset time: {} s'.format(t2 - t1))

scope.write('autoset EXECUTE') # autoset
t3 = time.perf_counter()
r = scope.query('*opc?') # sync
t4 = time.perf_counter()
print('autoset time: {} s'.format(t4 - t3))

# io config
scope.write('header 0')
scope.write('data:encdg RIBINARY')
scope.write('data:source CH1') # channel
scope.write('data:start 1') # first sample
record = int(scope.query('wfmpre:nr_pt?'))
scope.write('data:stop {}'.format(record)) # last sample
scope.write('wfmpre:byt_nr 1') # 1 byte per sample

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
tscale = float(scope.query('wfmpre:xincr?'))
tstart = float(scope.query('wfmpre:xzero?'))
vscale = float(scope.query('wfmpre:ymult?')) # volts / level
voff = float(scope.query('wfmpre:yzero?')) # reference voltage
vpos = float(scope.query('wfmpre:yoff?')) # reference position (level)

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
#pl.step(scaled_time, scaled_wave)
pl.plot(scaled_time, scaled_wave)
pl.title('channel 1') # plot label
pl.xlabel('time (seconds)') # x label
pl.ylabel('voltage (volts)') # y label
print("\nlook for plot window...")
pl.show()

print("\nend of demonstration")

