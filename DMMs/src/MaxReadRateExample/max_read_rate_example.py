#-------------------------------------------------------------------------------
# Name:  DMM4020 Max Reading Rate
# Purpose:  This example demonstrates how to achieve the maximum reading rate on
# the DMM4020
#
# Created:  2016-03-28
#
# Development Environment: Python 3.4.4, PyVisa 1.8, NI-VISA 2015.5, Windows 8.1
#
# Compatible Instruments: DMM4020
#
# Compatible Interfaces:  RS-232
#
# Tektronix provides the following example "AS IS" with no support or warranty.
#
#-------------------------------------------------------------------------------

import time, warnings
import visa

# Serial Port Settings
baudRate = 19200
flowCtrl = visa.constants.VI_ASRL_FLOW_NONE

# Set the number of readings to take
numrdgs = 500

rm = visa.ResourceManager()
lib = rm.visalib
dmm = rm.open_resource('ASRL1::INSTR')

lib.set_attribute(dmm.session, visa.constants.VI_ATTR_ASRL_FLOW_CNTRL, flowCtrl)
lib.set_attribute(dmm.session, visa.constants.VI_ATTR_ASRL_BAUD, baudRate)

# The first command sent after connecting results in a command error on my unit
# (perhaps because it has a CAL Error) so just send a terminator, read back the
# response and then continue from there.
dmm.query("")

print(dmm.query("*IDN?").strip())
# Need to perform an extra read after all commands since unit will return
# "=>\r\n" or "?>\r\n" after every command.
dmm.read()

dmm.write("RATE F")
dmm.read()
dmm.write("PRINT 1")
dmm.read()

start_time = time.time()
for i in range(0, numrdgs):
    print(dmm.read().strip())

elapsed_time = time.time() - start_time

dmm.write("PRINT 0")

print("Number of Readings: {0}\r\n\
Elapsed Time: {1}\r\n\
Readings/sec: {2}".format(numrdgs, elapsed_time, numrdgs/elapsed_time))

# After sending PRINT 0, dmm will output two more readings before stoping.
print(dmm.read().strip())
print(dmm.read().strip())
print(dmm.read())

dmm.close()
rm.close()

