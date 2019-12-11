"""
VISA: DPX Trace Selector
Author: Morgan Allison
Date created: Unknown
Date edited: 5/17
This program opens up a split DPX display and allows the user to select
the available traces. The trace numbers in the VISA commands are interpreted
in the comments below
Windows 7 64-bit
Python 3.6.0 64-bit (Anaconda 4.3.0)
PyVISA 1.8 (pip install pyvisa)
To get Anaconda: http://continuum.io/downloads
Tested on RSA5126B firmware v3.9.0031
"""

import visa

"""#################SEARCH/CONNECT#################"""
rm = visa.ResourceManager()
rsa = rm.open_resource('TCPIP::192.168.1.9::INSTR')
rsa.timeout = 10000
rsa.encoding = 'latin_1'
rsa.write_termination = None
rsa.read_termination = '\n'
print(rsa.query('*idn?'))
rsa.write('*cls')
rsa.write('abort')
rsa.write('system:preset')

"""#################INITIALIZE VARIABLES#################"""
# configure acquisition parameters
cf = 2.4453e9
span = 40e6

"""#################CONFIGURE INSTRUMENT#################"""
# configure DPX measurement
rsa.write('display:general:measview:new DPX')
rsa.write('sense:dpx:plot split')
rsa.write('spectrum:frequency:center {}'.format(cf))
rsa.write('spectrum:frequency:span {}'.format(span))

"""#################ACQUIRE/PROCESS DATA#################"""
rsa.write('initiate:immediate')
rsa.query('*opc?')
rsa.write('trace1:dpx 1')  # Trace 1
rsa.write('trace2:dpx 1')  # Trace 2
rsa.write('trace3:dpx 1')  # Trace 3
rsa.write('trace4:dpx 0')  # Math
rsa.write('trace5:dpx 1')  # Bitmap
rsa.write('trace6:dpx 1')  # DPXogram
rsa.write('trace7:dpx 1')  # DPXogram Line

rsa.close()
