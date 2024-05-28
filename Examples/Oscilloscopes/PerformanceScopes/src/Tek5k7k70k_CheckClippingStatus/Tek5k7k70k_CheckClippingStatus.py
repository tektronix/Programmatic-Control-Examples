# Title:
#   Check Clipping Status - 5k 7k 70k Series
#
# Description:
#   This script provides a function for checking the clipping status of a channel on
#   a MSO/DPO5000/B, DPO7000/C, MSO/DPO70000/B/C/D/DX, or DPO70000SX Series oscilloscope.
#
# Author: David Wyban
# Created:  2024-05-28
#
# Development Environment:
#    Python 3.11, PyVisa 1.14, NI-VISA 2023 Q4, Windows 10
# 
# Compatible Instruments:
#     MSO/DPO5000/B Series Oscilloscopes
#     DPO7000/C Series Oscilloscopes
#     MSO/DPO5000/B/C/D/DX Series Oscilloscopes
#     DPO70000SX Series Oscilloscopes
#
# Compatible Interfaces:
#     USB
#     Ethernet
#
# Tektronix provides the following example "AS IS" with no support or warranty.
#
#-------------------------------------------------------------------------------

from enum import Enum
import pyvisa as visa # https://pyvisa.readthedocs.io/en/latest/

class ClippingStatus(Enum):
	NotClipping = 0
	Both = 1
	Positive = 2
	Negative = 3


def Tek5k7k70k_CheckClipping(vi : visa.resources.MessageBasedResource, channel : str = 'CH1') -> tuple[bool, ClippingStatus]:
    '''Returns True if the signal is clipping and False if it is not.'''
    
    # Setup status model so that measurement warnings will output to event status queue
    vi.write('DESE 16') # Enables execution errors to be reported in the event status register and queue
    vi.write('*ESE 16') # Enables execution errors to be reported in the status byte register
    
    vi.write('*CLS')
    vi.write(f':MEASU:IMM:TYPE PK2PK;SOUR1 {channel};')
    measVal = vi.query('MEASU:IMM:VAL?')
    esr = int(vi.query('*ESR?'))

    if esr != 0:
        eventMessages = vi.query('ALLEV?').strip()
        print(eventMessages)
        eventParts = eventMessages.split(',')
        
        errCode = int(eventParts[0])
        if errCode == 547:
            return True, ClippingStatus.Both
        if errCode == 548:
            return True, ClippingStatus.Positive
        if errCode == 549:
            return True, ClippingStatus.Negative
        
    return False, ClippingStatus.NotClipping


def CheckClippingExample():
    rm = visa.ResourceManager()
    scope : visa.resources.MessageBasedResource = rm.open_resource('TCPIP::192.168.1.103::inst0::INSTR')
    print(scope.query('*IDN?'))
    
    print('Checking Clipping Status...')
    isClipping = Tek5k7k70k_CheckClipping(scope, 'CH1')
    print(f'Clipping?: {isClipping}')

    scope.close()
    rm.close()

# Only run the example if this script is the main script being run
if __name__ == '__main__':
	CheckClippingExample()