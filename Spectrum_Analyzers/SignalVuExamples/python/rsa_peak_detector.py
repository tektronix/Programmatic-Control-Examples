"""
VISA: Peak Detector
Author: Morgan Allison
Date created: Unknown
Date edited: 2/17
This program tracks the peak frequency 10 times, writes the results
to a csv file, and creates a scatter plot of the results.
Windows 7 64-bit, TekVISA 4.0.4
Python 3.6.0 64-bit (Anaconda 4.3.0)
MatPlotLib 2.0.0, PyVISA 1.8
To get PyVISA: pip install pyvisa
Download Anaconda: http://continuum.io/downloads
Anaconda includes MatPlotLib
Download SignalVu-PC programmer manual: http://www.tek.com/node/1828803
Download RSA5100B programmer manual: 
http://www.tek.com/spectrum-analyzer/inst5000-manual-7
Tested on RSA306B, RSA507A, RSA5126B
"""

import visa
from csv import writer
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
freq = 2e9
span = 40e6
rbw = 100
refLevel = -50

rsa.write('spectrum:frequency:center {}'.format(freq))
rsa.write('spectrum:frequency:span {}'.format(span))
rsa.write('spectrum:bandwidth {}'.format(rbw))
rsa.write('input:rlevel {}'.format(refLevel))

actualFreq = float(rsa.query('spectrum:frequency:center?'))
actualSpan = float(rsa.query('spectrum:frequency:span?'))
actualRbw = float(rsa.query('spectrum:bandwidth?'))
actualRefLevel = float(rsa.query('input:rlevel?'))

print('CF: {} Hz'.format(actualFreq))
print('Span: {} Hz'.format(actualSpan))
print('RBW: {} Hz'.format(actualRbw))
print('Reference Level: {}'.format(actualRefLevel))
print()  # just some whitespace

rsa.write('trigger:status off')
rsa.write('initiate:continuous off')

"""#################ACQUIRE/PROCESS DATA#################"""
rsa.write('calculate:marker:add')
peakFreq = []
peakAmp = []
with open('peak_detector.csv', 'w') as f:
    w = writer(f, lineterminator='\n')  # by default the csv module uses \r\n
    w.writerow(['Frequency', 'Amplitude'])  # header row
    # acquisition and measurement loop
    for i in range(10):
        rsa.write('initiate:immediate')
        rsa.query('*opc?')

        rsa.write('calculate:spectrum:marker0:maximum')
        peakFreq.append(float(rsa.query('calculate:spectrum:marker0:X?')))
        peakAmp.append(float(rsa.query('calculate:spectrum:marker0:Y?')))
        w.writerow([peakFreq[i], peakAmp[i]])

plt.scatter(peakFreq, peakAmp)
plt.title('Scatter Plot of Amplitude vs Frequency')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude (dBm)')
plt.xlim((freq - span / 2), (freq + span / 2))
plt.ylim(refLevel, refLevel - 100)
plt.show()

rsa.close()
