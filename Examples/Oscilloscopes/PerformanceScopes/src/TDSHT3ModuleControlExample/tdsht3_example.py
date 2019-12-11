#TDSHT3 example

#Compatible Instruments:  MSO/DPO7000/B/C, MSO/DPO70k

#Prerequisites:  DPOJET, TDSHT3 Application Software Packages

#Python 3.4:  https://www.python.org/download/releases/3.4.3/
#PyVisa 1.8:  https://pyvisa.readthedocs.io/en/stable/getting.html
#NI-VISA:  http://www.ni.com/download/ni-visa-16.0/6184/en/

#Date:  January 11, 2017

#Tektronix provides the following example "AS IS" with no support or warranty.
##############################################################################

import visa

import time

visa_address = 'TCPIP0::134.62.36.65::inst0::INSTR'

print('Open VISA connection...')

rm = visa.ResourceManager()
scope = rm.open_resource(visa_address)
scope.timeout = 1000

print(scope.query("*IDN?"))

print('Open TDSHT3 module...')
scope.write('APPLICATION:ACTIVATE "HDMI Compliance Test Software(1.4)"')

#application commands are non-blocking, so subsequent commands can generate timing errors
#delays may be balanced based on the network environment, but these values should be safe
time.sleep(15)

print('Recall default sestup...')
scope.write('VARIABLE:VALUE\s"setup","Default"')

time.sleep(20)

print('Set measurements...')
scope.write('VARIABLE:VALUE "measAdd","sourceClockDutyCycle"')
time.sleep(5)
scope.write('VARIABLE:VALUE "measAdd","sourceRiseTime"')
time.sleep(5)
scope.write('VARIABLE:VALUE "measAdd","sourceFallTime"')
time.sleep(5)
scope.write('VARIABLE:VALUE "measAdd","sourceClockJitter"')
time.sleep(5)
scope.write('VARIABLE:VALUE "measAdd","sourceInterPairSkew"')
time.sleep(5)

print('Run test...')
scope.write('VARIABLE:VALUE "sequencerState","Sequencing"')
time.sleep(80)

print('Set report location and save report...')
scope.write('VARIABLE:VALUE "reportFileChange","C:\\temp\\reports\\test2.mht"')
time.sleep(20)
scope.write('VARIABLE:VALUE "reportDetail","Save"')
time.sleep(5)

print('Close VISA connection...')
scope.close()
rm.close()


