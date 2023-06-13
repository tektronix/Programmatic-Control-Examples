#-------------------------------------------------------------------------------
# Name:  Fetch Waveform Data for MSO/DPO 5K 7K & 70K Series Scopes
# Purpose:  This example demonstrates how to fetch waveform data from MSO/DSA/DPO
# 5K, 7K & 70K Series Scopes, convert the raw data into floating point values and
# then save it to disk in a binary format.
#
# Created:  2021-01-03
#
# Development Environment: Python 3.7, PyVisa 1.11, NI-VISA 18.5, Windows 10
#
# Compatible Instruments:
#       MSO/DPO 5000(B) Series Oscilloscopes
#       DPO7000(C) Series Oscilloscopes
#       MSO/DSA/DPO 70000(B)(C)(DX)(SX) Series Oscilloscopes
#
# Compatible Interfaces:  USB, Ethernet
#
# Tektronix provides the following example "AS IS" with no support or warranty.
#
#-------------------------------------------------------------------------------

import pyvisa as visa # https://pyvisa.readthedocs.io/en/latest/
import numpy as np # https://numpy.org/

# Modify the following line with the VISA resource address of your instrument
visaResourceAddr = 'TCPIP0::<ip address>::inst0::INSTR'

rm = visa.ResourceManager()
scope = rm.open_resource(visaResourceAddr)

print(scope.query('*IDN?'))
scope.write("HEADER 0")
scope.write("DATA:SOUR CH1")
scope.write("DAT:ENC SRI")   # Signed Binary Format, LSB order
scope.write("DAT:WIDTH 1")

scope.write("DAT:START 1")
scope.write("DAT:STOP 1e10") # Set data stop to max
recordLength = int(scope.query("WFMO:NR_P?"))  # Query how many points are actually available
scope.write("DAT:STOP {0}".format(recordLength)) # Set data stop to match points available

# Fetch horizontal scaling factors
xinc = float(scope.query("WFMO:XINCR?"))
xzero = float(scope.query("WFMO:XZERO?"))
pt_off = int(scope.query("WFMO:PT_OFF?"))

# Fetch vertical scaling factors
ymult = float(scope.query("WFMO:YMULT?"))
yzero = float(scope.query("WFMO:YZERO?"))
yoff = float(scope.query("WFMO:YOFF?"))

# Fetch waveform data
scope.write("curve?")

# Data is sent back with ieee defined header.  ie. #41000<binary data bytes>\n
# PyVISA read_binary_values() method will automatically read and parse the ieee block header so you don't have to.
rawData = scope.read_binary_values(datatype='b', is_big_endian=False, container=np.ndarray, header_fmt='ieee', expect_termination=True)
dataLen = len(rawData)

# Create numpy arrays of floating point values for the X and Y axis
t0 = (-pt_off * xinc) + xzero
xvalues = np.ndarray(dataLen, np.float)
yvalues = np.ndarray(dataLen, np.float)
for i in range(0,dataLen):
    xvalues[i] = t0 + xinc * i # Create timestamp for the data point
    yvalues[i] = float(rawData[i] - yoff) * ymult + yzero # Convert raw ADC value into a floating point value

# Save data to disk in binary format.  Can be read back from file using np.load()
xvalues.dump(r"./xvalues_numpy_array.dat")
yvalues.dump(r"./yvalues_numpy_array.dat")

scope.close()
rm.close()
