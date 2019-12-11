"""
VISA: RSA Spectrum Trace Transfer
Author: Morgan Allison
Date created: Unknown
Date edited: 5/17
This program transfers the Spectrum trace from the RSA to the 
computer and plots the results.
Windows 7 64-bit, TekVISA 4.0.4
Python 3.6.0 64-bit (Anaconda 4.3.0)
NumPy 1.11.2, MatPlotLib 2.0.0, PyVISA 1.8
To get PyVISA: pip install pyvisa
Download Anaconda: http://continuum.io/downloads
Anaconda includes MatPlotLib
Download SignalVu-PC programmer manual: http://www.tek.com/node/1828803
Download RSA5100B programmer manual: 
http://www.tek.com/spectrum-analyzer/inst5000-manual-7
Tested on RSA306B, RSA507A, and RSA5126B
"""

import visa
import numpy as np
import matplotlib.pyplot as plt

"""#################SEARCH/CONNECT#################"""
rm = visa.ResourceManager()
rsa = rm.open_resource('GPIB8::1::INSTR')
rsa.timeout = 10000
rsa.encoding = 'latin_1'
rsa.write_termination = None
rsa.read_termination = '\n'
print(rsa.query('*idn?'))
rsa.write('*rst')
rsa.write('*cls')
rsa.write('abort')

"""#################CONFIGURE INSTRUMENT#################"""
# configure acquisition parameters
cf = 2.4453e9
span = 40e6
refLevel = 0
rsa.write('spectrum:frequency:center {}'.format(cf))
rsa.write('spectrum:frequency:span {}'.format(span))
rsa.write('input:rlevel {}'.format(refLevel))

rsa.write('initiate:continuous off')
rsa.write('trigger:status off')

"""#################ACQUIRE/PROCESS DATA#################"""
# start acquisition THIS MUST BE DONE
# it is an overlapping command, so *OPC? MUST be sent for synchronization
rsa.write('initiate:immediate')
rsa.query('*opc?')

spectrum = rsa.query_binary_values('fetch:spectrum:trace?', datatype='f',
                                   container=np.array)

# generate the frequency vector for plotting
fMin = cf - span / 2
fMax = cf + span / 2
freq = np.linspace(fMin, fMax, len(spectrum))

"""#################PLOTS#################"""
fig = plt.figure(1, figsize=(15, 8))
ax = fig.add_subplot(111, facecolor='k')
ax.plot(freq / 1e9, spectrum, 'y')
ax.set_title('Spectrum')
ax.set_xlabel('Frequency (GHz)')
ax.set_ylabel('Amplitude (dBm)')
ax.set_xlim(fMin / 1e9, fMax / 1e9)
ax.set_ylim(refLevel - 100, refLevel)
plt.show()

rsa.close()
