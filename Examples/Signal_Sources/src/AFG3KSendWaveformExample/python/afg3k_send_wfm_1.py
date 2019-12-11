# afg3k_send_wfm_1.py
#
# date: 01-27-2017
#
# demonstrate 'data:define' and 'data' remote programmatic commands for the
# AFG3000 series and AFG2000 series.
#
# The data following the binary block header is unsigned 16-bit integer
# values, most significant byte first (big-endian). Bits 15 and 16 are
# ignored as the AFG has 14-bits of dynamic range. The key concept is the
# digital values are unit-less. Value 0 is the minimum output and value 16382
# is the maximum output. Amplitude (and offset, and timing) are applied at
# run-time based on the AFG settings.
#
# Python v3.6.0 32-bit
# numpy v1.12.0
# pyvisa v1.8
# NI-VISA v15.5
# AFG2021 v1.1.9
#
# Tektronix provides the following example "AS IS" without any guarantees
# or support.  This example is for instructional guidance only.

import numpy as np # http://www.numpy.org/
import visa # https://pyvisa.readthedocs.io/en/stable/

# variables
visa_descriptor = 'tcpip::134.62.36.59::instr'
record_length = 12

# calculations
# example arbitrary function: 1-cycle sine
sample = np.arange(record_length)
vector = np.sin(2 * np.pi * sample / len(sample))

# normalize to dac values
m = 16382 / (vector.max() - vector.min())
b = -m * vector.min()
dac_values = (m * vector + b)
np.around(dac_values, out=dac_values)
dac_values = dac_values.astype(np.uint16)

print('digital sample values...')
for i in dac_values:
    print(' 0x{:04x}'.format(i))

# instrument communication
rm = visa.ResourceManager()
afg = rm.open_resource(visa_descriptor)
afg.write_termination = None
afg.read_termination = '\n'
afg.timeout = 10000 # ms

r = afg.query('*idn?')
print('connected to...\n{}'.format(r))

print('clearing event status register & flushing messages')
afg.write('*cls')
r = afg.query('*esr?')
print(' esr value: 0b{:08b}'.format(int(r)))
r = afg.query('system:error?')
print(' msg: {}'.format(r))

cmd = 'data:define EMEM,{:d}'.format(record_length)
print('writing: "{}"'.format(cmd))
afg.write(cmd)
r = afg.query('*esr?')
print(' esr value: 0b{:08b}'.format(int(r)))
r = afg.query('system:error?')
print(' msg: {}'.format(r))

afg.write_binary_values('data EMEM,',
                        dac_values,
                        datatype='h',
                        is_big_endian=True)
r = afg.query('*esr?')
print(' esr value: 0b{:08b}'.format(int(r)))
r = afg.query('system:error?')
print(' msg: {}'.format(r))

print('disconnecting...')
afg.close()

print('done')
