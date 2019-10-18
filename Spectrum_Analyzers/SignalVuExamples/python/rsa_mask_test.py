"""
VISA Control: RSA Mask Test Query
Author: Morgan Allison
Date Created: 5/17
Date Edited: 5/17
Sets up a default mask test and queries the frequencies at which violations
occured.
Windows 7 64-bit, NI-VISA 5.4/TekVISA4.0.4
Python 3.6.0 64-bit (Anaconda 4.3.0)
To get Anaconda: http://continuum.io/downloads
PyVISA 1.8 (pip install pyvisa)
Tested on RSA5126B with firmware 3.9.0031
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

cf = 2.4453e9
span = 40e6

rsa.write('system:preset')
rsa.write('display:general:measview:new dpx')
rsa.write('spectrum:frequency:center {}'.format(cf))
rsa.write('spectrum:frequency:span {}'.format(span))

rsa.write('calculate:search:limit:match:beep on')
rsa.write('calculate:search:limit:match:sacquire off')
rsa.write('calculate:search:limit:match:sdata off')
rsa.write('calculate:search:limit:match:spicture off')
rsa.write('calculate:search:limit:match:strace off')
rsa.write('calculate:search:limit:operation omask')
rsa.write('calculate:search:limit:operation:feed "dpx", "Trace1"')
rsa.write('calculate:search:limit:state on')

rsa.write('initiate:immediate')
rsa.query('*opc?')

if int(rsa.query('calculate:search:limit:fail?').strip()) == 1:
    maskPoints = rsa.query('calculate:search:limit:report:data?')
    # print(maskPoints)
    maskPoints = [m.replace('"', '') for m in maskPoints.strip().split(',"')]
    print('Mask Violations: {}'.format(maskPoints[0]))
    for m in maskPoints[1:]:
        print('Violation Range: {}'.format(m))
else:
    print('No mask violations have occurred.')
