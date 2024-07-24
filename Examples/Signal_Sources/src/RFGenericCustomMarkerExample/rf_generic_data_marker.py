# rf_generic_data_marker.py

"""
VISA: SourceXpress/AWG RF Generic Signal Data Markers
Author: Morgan Allison
Date created: 1/17
Date edited: 5/17
Imports a text file with desired data bits, creates a 2FSK signal
containing that data, assigns that data to Marker1 and Marker2 for the 
created waveform, and assigns that waveform + markers to Channel 1 
for playback.
The user MUST place the text file in the same directory as this script
and input the number of desired bits in the waveform. 
Currently the script requires that the number of bits in the waveform
be an integer multiple of the number of bits in the data file.

Windows 7 64-bit
Python 3.6.0 64-bit (Anaconda 4.3.0)
NumPy 1.11.2, PyVISA 1.8
Get Anaconda: http://continuum.io/downloads
Anaconda includes NumPy
Get PyVISA: pip install pyvisa
"""

import visa
import numpy as np
from os import getcwd

# Change this to connect to your AWG as needed
"""#################SEARCH/CONNECT#################"""
rm = visa.ResourceManager()
awg = rm.open_resource('GPIB8::1::INSTR')
awg.timeout = 25000
print(awg.ask('*idn?'))
awg.write('*rst')
awg.write('*cls')
awg.ask('*opc?')

# Waveform Setup
# ###############################INPUT USER PARAMETERS HERE
sampRate = 18e9
symRate = 10e6
centerFreq = 1e9
numSym = 128
fileName = getcwd() + '\\testpattern2.txt'

# ###############################INPUT USER PARAMETERS HERE

print('Creating Waveform Data.\n')

awg.write('wplugin:active "RF Generic Signal"')
awg.write('rfgsignal:reset')
awg.ask('*OPC?')

awg.write('rfgsignal:carrier1:frequency {}'.format(centerFreq))
awg.write('rfgsignal:carrier1:type dmodulation')
awg.write('rfgsignal:carrier1:data file')

# This is the file that contains the data bits and it is on the AWG.
# The VISA command requires that the fileName argument be in quotes
awg.write('rfgsignal:carrier1:data:file "{}"'.format(fileName))
awg.write('rfgsignal:carrier1:dmodulation:type fsk')
awg.write('rfgsignal:carrier1:dmodulation:fsk fsk2')
awg.write('rfgsignal:carrier1:dmodulation:fsk:pdev 50e6')
awg.write('rfgsignal:carrier1:dmodulation:srate {}'.format(symRate))
awg.write('rfgsignal:carrier1:filter:type rectangular')
# awg.write('rfgsignal:carrier1:filter:alpha 0.5')
awg.write('rfgsignal:compile:name "pattern_test"')

awg.write('rfgsignal:compile:sformat rf')
awg.write('rfgsignal:compile:srate:auto off')
awg.write('rfgsignal:compile:srate {}'.format(sampRate))

awg.write('rfgsignal:compile:wlength:type symbols')
awg.write('rfgsignal:compile:wlength {}'.format(numSym))
awg.write('rfgsignal:compile:wlength:auto off')

awg.write('rfgsignal:compile:rfchannel 1')
awg.write('rfgsignal:compile:fdrange on')
awg.write('rfgsignal:compile:play off')

print('Compiling Waveform\n')
awg.write('rfgsignal:compile')
awg.ask('*OPC?')

# Configuring Marker Data
print('Generating Marker Data From Text File.\n')
wfmName = awg.ask('wlist:name? 1').rstrip()
wlength = int(awg.ask('wlist:waveform:length? {}'.format(wfmName.rstrip())))

sampPerSym = int(sampRate/symRate)
with open(fileName) as f:
    raw = f.read().strip()
raw = raw.split('\n')
markerValues = [int(i) for i in raw]

numBits = len(markerValues)
markerData = np.zeros(wlength, dtype=np.uint8)
repeats = int(wlength/(sampPerSym*numBits))


# Marker creation
start = 0
stop = start + sampPerSym
for i in range(repeats):
    for j in range(numBits):
        if markerValues[j] == 0:
            markerData[start:stop] = 128
        elif markerValues[j] == 1:
            markerData[start:stop] = 64
        start = stop
        stop = start + sampPerSym

print('Samples per symbol: ', sampPerSym)
print('Marker Values: ', markerValues)
print('Number of bits: ', numBits)
print('Repeats: ', repeats)
print('Wfm length: ', wlength)
print('markerData length: ', len(markerData))

# Convert marker data to 8-bit format
stringArg = 'wlist:waveform:marker:data {}, 0, {}, '.format(wfmName, wlength) 

awg.write_binary_values(stringArg, markerData, datatype='B')

# AWG playback
print('Loading/playing waveform.\n')

awg.write('clock:srate {}'.format(sampRate))
awg.write('source1:dac:resolution 8')
awg.ask('*OPC?')

awg.write('output1 on')
awg.write('source1:rmode triggered')
awg.write('source1:tinput atrigger')
awg.write('awgcontrol:run:immediate')
awg.ask('*OPC?')

# Check for errors
error = awg.ask( 'SYST:ERR:ALL?')
print('Status: ', error)
awg.close()

