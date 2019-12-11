# Python3 PPG Simple
# https://www.tek.com/sample-license

# basic PPG communication and control

import time # std module
import visa # http://github.com/pyvisa/pyvisa

visa_address = 'USB::0x0699::0x3132::9211157::INSTR'

# instrument communication
rm = visa.ResourceManager()
ppg = rm.open_resource(visa_address)
ppg.timeout = 30000 # ms
ppg.encoding = 'latin_1'
ppg.write_termination = None

# clear messages by reading all
r = ppg.query('system:error?')
i = 0
while r != '0, No error\n':
    r = ppg.query('system:error?')
    i += 1
print('messages cleared: {}'.format(i))

r = ppg.query('*idn?')
print(r.strip())

# reset
print('recalling default setup...')
t1 = time.perf_counter()
ppg.write('*rst')
r = ppg.query('system:error?')
t2 = time.perf_counter()
print('reset time: {} s'.format(t2-t1))

# simple setup
print('configuring example setup...')
t3 = time.perf_counter()
ppg.write('source:frequency 20e9')
ppg.write('digital1:pattern:type PRBS')
ppg.write('digital1:pattern:plength 15')
ppg.write('source:voltage1 300e-3')
ppg.write('output:clock:divider 2')
ppg.write('output1:state ON')
r = ppg.query('system:error?')
t4 = time.perf_counter()
print('setup time: {} s'.format(t4-t3))

# print status
print('status: {}'.format(r.strip()))
while r != '0, No error\n':
    r = ppg.query('system:error?')
    print(r.strip())

