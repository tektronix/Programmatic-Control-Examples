# Python3 MDO3AFG,MDO4AFG Send Arb
# https://www.tek.com/sample-license

# make a prbs7 and upload it to the MDO3000 series or 
# MDO4000 series built-in arb

import re
import time
import visa # https://github.com/pyvisa/pyvisa

visa_address = 'USB0::0x0699::0x0408::C011373::INSTR'

# create prbs7
# generator function: https://docs.python.org/3/tutorial/classes.html#generators
def prbs7(state):
    '''x^7 + x^6 + 1'''
    while True:
        bit_out = (state >> 6) & 1
        state = ((state << 1) + (((state >> 6) & 1) ^ ((state >> 5) & 1))) & 0b1111111
        yield bit_out
prbs7_str = str()
print('generating 127 bits (1 cycle) prbs7 from seed 0b1111111 ...')
t = prbs7(0b1111111)
for b in range(127):
    prbs7_str += str(next(t))
# add commas between bits, excluding end bit
prbs7_str = re.sub(r'([01])(?!$)', r'\1,', prbs7_str)
print('{:s}\n'.format(prbs7_str))
# normalize to 1,-1 (i.e. replace '0' with '-1') for afg full-scale
prbs7_str = prbs7_str.replace('0', '-1')

# instrument communication
rm = visa.ResourceManager()
scope = rm.open_resource(visa_address)
scope.timeout = 10000 # ms
scope.encoding = 'latin_1'
scope.read_termination = '\n'
scope.write_termination = None
scope.write('*cls') # clear ESR
scope.write('header OFF')

print('connected to instrument ...')
print(scope.query('*idn?'))

input(r"""
ACTION:
Connect AFG output to oscilloscope Channel 1.
Press Enter to continue...
""")

# reset oscilloscope for demonstration
scope.write('*rst') # reset
t1 = time.perf_counter()
r = scope.query('*opc?') # sync
t2 = time.perf_counter()
print('reset time: {}\n'.format(t2 - t1))

# configure afg
print('configuring afg ...')
t1 = time.perf_counter()
scope.write('afg:arbitrary:emem:points:encdg ASCII')
scope.write('afg:arbitrary:emem:points {}'.format(prbs7_str))
scope.write('afg:function ARBITRARY')
scope.write('afg:output:load:impedance HIGHZ')
scope.write('afg:highlevel 3.3')
scope.write('afg:lowlevel 0')
scope.write('afg:period 127e-6') # 127 us / 127 bits = 1 us per bit (1 Mbps)
scope.write('afg:output:state ON')
t2 = time.perf_counter()
print('afg setup time: {}\n'.format(t2 - t1))

# configure acquisition
print('configuring acquisition ...')
t1 = time.perf_counter()
scope.write('horizontal:scale 40e-6')
scope.write('ch1:scale 0.5')
scope.write('ch1:position -3.25')
scope.write('trigger:a:type PULSE')
scope.write('trigger:a:pulse:class TIMEOUT')
scope.write('trigger:a:timeout:time 6e-6')
t2 = time.perf_counter()
print('acquisition setup time: {}\n'.format(t2 - t1))

# error checking
r = int(scope.query('*esr?'))
print('event status register: 0b{:08b}'.format(r))
r = scope.query('allev?').strip()
print('all event messages: {}\n'.format(r))

print("end of demonstration")
