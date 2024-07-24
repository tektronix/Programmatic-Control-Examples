#-------------------------------------------------------------------------------
# Name:
#     DPO70000SX Ultrasync Time-Sync 4-stack Control Example
# Purpose:
#     This example demonstrates programatic control of a 4-stack of 
#     DPO70000SX instruments configured in the Ultrasync Time-Sync mode.
#
# Created:  2024-02-16
#
# Development Environment:
#    Python 3.11, PyVisa 1.14, NI-VISA 2023 Q4, Windows 10
#
# Compatible Instruments:
#     TekConnect Only Models of DPO70000SX Series Oscilloscopes
#      Can be used with ATI Models of DPO70000SX Series Oscilloscopes with some
#      modification.
#
# Compatible Interfaces:  USB, Ethernet
#
# Tektronix provides the following example "AS IS" with no support or warranty.
#
#-------------------------------------------------------------------------------

import pyvisa as visa # https://pyvisa.readthedocs.org/en/stable/
from datetime import datetime
import time
import msvcrt
import os


# Script User Setup
# =================

masterRsrcAddr = 'TCPIP0::192.168.1.10::inst0::INSTR'
extBRsrcAddr =   'TCPIP0::192.168.1.11::inst0::INSTR'
extCRsrcAddr =   'TCPIP0::192.168.1.12::inst0::INSTR'
extDRsrcAddr =   'TCPIP0::192.168.1.13::inst0::INSTR'
defaultTimeout = 15000

localDataFolder = '.\\'  # Folder where to save data on PC running this script. 
# '.\\' will save to same folder this script is located

sampleRate = 50e9
recordLen = 1e6
horizontalPosition = 20.0 # 20%

trigSource = 'AUX'
trigSlope = 'RISE'      # RISe|FALL|EITHER
trigLevel = 200e-3

vertScales = {
    'master' : { 'ch1' : 50e-3, 'ch2' : 50e-3, 'ch3' : 50e-3, 'ch4' : 50e-3},
    'extB'   : { 'ch1' : 50e-3, 'ch2' : 50e-3, 'ch3' : 50e-3, 'ch4' : 50e-3},
    'extC'   : { 'ch1' : 50e-3, 'ch2' : 50e-3, 'ch3' : 50e-3, 'ch4' : 50e-3},
    'extD'   : { 'ch1' : 50e-3, 'ch2' : 50e-3, 'ch3' : 50e-3, 'ch4' : 50e-3},
}
# =================



class ConsoleLog:
    # Simple class for printing messages to the console and logging them to a file
    logfile = None

    def __init__(self, logFilePath : str) -> None:
        self.logfile = open(logFileName, 'w')
        self.Write('Log File Opened')
    
    def Write(self, msg : str, endl='\n'):
        # Prints messages to the console and writes them to the console log
        timestampStr = datetime.now().strftime("%Y-%m-%d %H:%M:%S - ")
        print(timestampStr + str(msg), end=endl)
        self.logfile.write(timestampStr + str(msg) + endl)
    
    def Close(self) -> None:
        if self.logfile != None:
            self.logfile.close()


def WaitOperationComplete(vi : visa.resources.MessageBasedResource, timeoutms : int = None):
    # Waits for any operations that will raise the OPC flag to complete before returning
    # Use timeout to set how long to wait.  If timeout is None then current timeout value for the VISA session will be used.
    temp = None
    if timeoutms != None:
        temp = vi.timeout
        vi.timeout = timeoutms

    vi.query('*OPC?')
    
    if timeoutms != None:
        vi.timeout = temp

def ErrorQuery(vi : visa.resources.MessageBasedResource):
    return vi.query('*ESR?;ALLEV?;')

def SetRunState(vi : visa.resources.MessageBasedResource, run : bool):
    # Sets the scope into the Running or the Stopped states
    state = 'RUN' if run==True else 'STOP'
    vi.write(f'ACQ:STATE {state}')

def StartAcquiring(vi : visa.resources.MessageBasedResource, waitUntilFirstAcqComplete : bool = False, waitTimeoutSec : float = 10.0):
    # Functionally equivalent to pressing the Run/Stop button on the front panel to start acquisitions
    # Can optionally block function call from returning until at least one acqusition is made by setting
    # waitUntilFirstAcqComplete to True.  waitTimeout sets how long to wait.
    vi.write('ACQ:STOPAFTER RUNSTOP')
    SetRunState(vi, True)
    acqState = int(vi.query('ACQ:STATE?'))
    while acqState != 1:
        time.sleep(0.2)
        acqState = int(vi.query('ACQ:STATE?'))
    
    if waitUntilFirstAcqComplete == True:
        tWaitStart = time.perf_counter()
        acqCount = int(master.query('ACQ:NUMACQ?'))
        while acqCount < 1:
            if time.perf_counter() - tWaitStart > waitTimeoutSec:
                break
            time.sleep(0.1)
            acqCount = int(master.query('ACQ:NUMACQ?'))

def StopAcquiring(vi : visa.resources.MessageBasedResource):
    # Functionally equivalent to pressing the Run/Stop button on the front panel to stop acquisitions
    SetRunState(vi, False)
    acqState = int(vi.query('ACQ:STATE?'))
    while acqState != 0:
        time.sleep(0.2)
        acqState = int(vi.query('ACQ:STATE?'))
    WaitOperationComplete(vi)

def WaitTriggerReady(vi : visa.resources.MessageBasedResource, timeoutSec : float = 10.0) -> bool:
    # Function returns when the trigger is ready

    # Check that scope is in run state
    if int(vi.query('ACQ:STATE?')) != 1:
        return False
    
    trigReady = 0
    tWaitStart = time.perf_counter()
    trigReady = int(master.query('TRIG:A:READY?'))
    while trigReady != 1:
        if time.perf_counter() - tWaitStart > timeoutSec:
            break
        time.sleep(0.1)
        trigReady = int(master.query('TRIG:A:READY?'))
    
    if trigReady == 1:
        return True
    
    return False

# These Single Sequence functions are the equivalent of pressing the Single button on the front panel
def InitiateSingleSequnce(vi : visa.resources.MessageBasedResource):
    # Starts a Single Sequence and returns
    vi.write('ACQ:STOPAFTER SEQ')
    vi.write('ACQ:STATE RUN')

def ExcuteSingleSequence(vi : visa.resources.MessageBasedResource, timeoutms : int):
    # Starts a Single Sequence and waits until the scope has triggered and the acquisition is complete before returning.
    temp = vi.timeout
    vi.timeout = timeoutms
    vi.write('ACQ:STOPAFTER SEQ')
    vi.write('ACQ:STATE RUN')
    vi.query('*OPC?')
    vi.timeout = temp


def InitializeStack(vi : visa.resources.MessageBasedResource):
    # Performs a Default Setup on the stack and waits for it to complete before returning. This should only be called on the Master.
    master.write('*CLS')
    vi.write('*RST')
    vi.query('*OPC?')

def SetVerticalScale(vi : visa.resources.MessageBasedResource, channel : str, scale : float):
    # Sets the vertical scale of the channel.  'channel' should be the name of the channel i.e. "CH1", "MATH1", "REF1", etc.
    vi.write(f'{channel}:SCALE {scale}')

def SetupChannels(vi : visa.resources.MessageBasedResource, ch1Scale : float, ch2Scale : float, ch3Scale : float, ch4Scale : float):
    # Turns on all the channels on the scope and sets the vertical scale of each
    vi.write(':SEL:CH1 ON;CH2 ON;CH3 ON;CH4 ON;')  # Turn all the channels on
    SetVerticalScale(vi, 'CH1', ch1Scale)
    SetVerticalScale(vi, 'CH2', ch2Scale)
    SetVerticalScale(vi, 'CH3', ch3Scale)
    SetVerticalScale(vi, 'CH4', ch4Scale)
    vi.write('*WAI')

def SetupHorizontal(vi : visa.resources.MessageBasedResource, sampleRate : float, recordLength : float, horizontalPos : float = 50):
    # Configures the horizontal settings of the stack. Should only be called on the Master.
    
    vi.write('HOR:MODE MAN;*WAI;')
    time.sleep(2) # Horizontal commands must trickle down to extensions so pace these commands
    vi.write(f'HOR:MODE:SAMPLERATE {sampleRate};*WAI;')
    time.sleep(2)
    vi.write(f'HOR:MODE:RECORDLENGTH {recordLength};*WAI;')
    time.sleep(2)
    vi.write(f'HOR:POS {horizontalPos};*WAI;')
    time.sleep(2)

def SetupEdgeTrigger(vi : visa.resources.MessageBasedResource, trigSource : str, trigSlope : str, trigLevel : float, trigMode : str = 'AUTO'):
    # Configures the trigger settings.  Should only be called on the Master.  Only the Master can be used to trigger in Time-sync mode
    vi.write(f'TRIG:A:TYPE EDGE')
    vi.write(f'TRIG:A:EDGE:SOURCE {trigSource}')
    vi.write(f'TRIG:A:EDGE:SLOPE:AUX {trigSlope}')
    vi.write(f'TRIG:A:LEVEL {trigLevel}')
    vi.write(f'TRIG:A:MODE {trigMode}')
    vi.write('*WAI')

def TakeScreenshot(vi : visa.resources.MessageBasedResource, localFolderPath : str, pngFileName : str):
    # Takes a screenshot and transfers it to the local PC.  pngFileName should include the extension ".png"
    vi.write("HARDCOPY:PORT FILE")
    vi.write("HARDCopy:PALETTE COLOR")
    vi.write("EXPORT:FORMAT PNG")
    vi.write("HARDCopy:FILEName \"C:\\Users\\Tek_local_admin\\Pictures\\Temp.png\"")
    vi.write("HARDCopy STARt")
    vi.query('*OPC?')
    vi.write("FILESystem:READFile \"C:\\Users\\Tek_local_admin\\Pictures\\Temp.png\"")
    imgData = vi.read_raw()
    # Save the transfered image to the hard drive of your PC
    imgFile = open(localFolderPath + pngFileName, "wb")
    imgFile.write(imgData)
    imgFile.close()

    # Delete the image file from the scope's hard drive.
    vi.write("FILESystem:DELEte \"C:\\Users\\Tek_local_admin\\Pictures\\Temp.png\"")
    return

def SaveAllWfmsToDisk(vi : visa.resources.MessageBasedResource, remoteFilePath, filename, waitComplete : bool = True):
    # Saves all waveforms on screen to the scope's local disk.
    # "remoteFilePath" specifies the folder on the scope where the files should be saved.
    # "filename" should NOT include the extention i.e. DO NOT include ".wfm"
    # waitComplete will determine if the function will wait for the save operation to complete before returning
    vi.write(f'SAVE:WAVEFORM ALL,"{remoteFilePath + filename}"')

    if waitComplete:
        vi.query('*OPC?')

def FetchFile(vi : visa.resources.MessageBasedResource, remoteFileFolder : str, fileName : str, localFolderPath : str):
    # Fetches a file from the scope and saves it to the local PC
    vi.write(f'FILESystem:READFile \"{remoteFileFolder}{fileName}\"')
    fileData = vi.read_raw(2 * 1024 * 1024)

    # Save the transfered file to the hard drive of your PC
    file = open(localFolderPath + fileName, "wb")
    file.write(fileData)
    file.close()

def DeleteFile(vi : visa.resources.MessageBasedResource, remoteFileFolder : str, fileName : str):
    # Deletes a file from the hard drive of the scope
    vi.write(f'FILESystem:DELEte \"{remoteFileFolder}{fileName}\"')

def WaitForPressAnyKey():
    return msvcrt.getch()


#=========================================================
# Main Script Starts Here
#=========================================================
tScriptStart = datetime.now()

saveDataPath = localDataFolder + tScriptStart.strftime("%Y-%m-%d_%H%M%S\\")
pathExists = os.path.exists(saveDataPath)
if not pathExists:
    os.makedirs(saveDataPath)

logFileName = saveDataPath + tScriptStart.strftime("%Y-%m-%d_%H%M%S_Test_Log.txt")
log = ConsoleLog(logFileName)
log.Write('Script Started')

try:
    # Connect to instruments in stack
    rm = visa.ResourceManager()
    log.Write('Opening connections to scopes in stack')
    master : visa.resources.MessageBasedResource = rm.open_resource(masterRsrcAddr)
    master.timeout = defaultTimeout
    log.Write('Master: ' + master.query('*IDN?').strip())

    extB : visa.resources.MessageBasedResource = rm.open_resource(extBRsrcAddr)
    log.Write('ExtenB: ' + extB.query('*IDN?').strip())
    extB.timeout = defaultTimeout

    extC : visa.resources.MessageBasedResource = rm.open_resource(extCRsrcAddr)
    log.Write('ExtenC: ' + extC.query('*IDN?').strip())
    extC.timeout = defaultTimeout

    extD : visa.resources.MessageBasedResource = rm.open_resource(extDRsrcAddr)
    log.Write('ExtenD: ' + extD.query('*IDN?').strip())
    extD.timeout = defaultTimeout


    log.Write('Resetting Stack...')
    InitializeStack(master)
    log.Write('Reset Done')

    log.Write('Setting up stack...')
    StopAcquiring(master)

    SetupChannels(master, vertScales['master']['ch1'], vertScales['master']['ch2'], vertScales['master']['ch3'], vertScales['master']['ch4'])
    SetupChannels(extB, vertScales['extB']['ch1'], vertScales['extB']['ch2'], vertScales['extB']['ch3'], vertScales['extB']['ch4'])
    SetupChannels(extC, vertScales['extC']['ch1'], vertScales['extC']['ch2'], vertScales['extC']['ch3'], vertScales['extC']['ch4'])
    SetupChannels(extD, vertScales['extD']['ch1'], vertScales['extD']['ch2'], vertScales['extD']['ch3'], vertScales['extD']['ch4'])
    
    SetupHorizontal(master, sampleRate, recordLen, horizontalPosition)
    SetupEdgeTrigger(master, trigSource, trigSlope, trigLevel)

    
    log.Write('Setting up stack done')

    log.Write('Starting free-running acqusitions')
    StartAcquiring(master, True)
    log.Write('Free-running acqusitions started')
    

    print('\r\nPress any key to initiate a Single Sequence...')
    WaitForPressAnyKey()
    StopAcquiring(master)
    time.sleep(0.2)
    log.Write('Initiating Single Sequence...')
    InitiateSingleSequnce(master)
    time.sleep(0.2)
    WaitTriggerReady(master)
    log.Write('Single Sequence Initiated. Scope ready for trigger event.')
    WaitOperationComplete(master, 600000)  # Will wait 60 seconds before timing out
    timeAcqComplete = datetime.now()
    log.Write('Single Sequence Complete')


    remoteFolder = 'C:\\Users\\Tek_Local_Admin\\Tektronix\\TekScope\\Waveforms\\'
    baseFileName = timeAcqComplete.strftime("%Y-%m-%d_%H%M%S")

    log.Write('Saving waveforms to .wfm files on scopes')
    SaveAllWfmsToDisk(master, remoteFolder, baseFileName + '_Master_', False)
    SaveAllWfmsToDisk(extB, remoteFolder, baseFileName + '_ExtB_', False)
    SaveAllWfmsToDisk(extC, remoteFolder, baseFileName + '_ExtC_', False)
    SaveAllWfmsToDisk(extD, remoteFolder, baseFileName + '_ExtD_', False)

    # We didn't wait for each scope to complete before instructing the next scope to save so wait for the scopes to finish now
    WaitOperationComplete(master)
    WaitOperationComplete(extB)
    WaitOperationComplete(extC)
    WaitOperationComplete(extD)
    log.Write('Saving waveforms to .wfm files on scopes complete')
    

    log.Write('Fetching screenshots from scopes')
    TakeScreenshot(master, saveDataPath, baseFileName + '_Master_Screenshot.png')
    log.Write('Fetching screenshots from Master complete')
    TakeScreenshot(extB, saveDataPath, baseFileName + '_ExtB_Screenshot.png')
    log.Write('Fetching screenshots from Extension B complete')
    TakeScreenshot(extC, saveDataPath, baseFileName + '_ExtC_Screenshot.png')
    log.Write('Fetching screenshots from Extension C complete')
    TakeScreenshot(extD, saveDataPath, baseFileName + '_ExtD_Screenshot.png')
    log.Write('Fetching screenshots from Extension D complete')

    remoteFilePathBase = remoteFolder + baseFileName
    log.Write('Fetching .wfm files from scopes')
    FetchFile(master, remoteFolder, baseFileName + '_Master_CH1.wfm', saveDataPath)
    FetchFile(master, remoteFolder, baseFileName + '_Master_CH2.wfm', saveDataPath)
    FetchFile(master, remoteFolder, baseFileName + '_Master_CH3.wfm', saveDataPath)
    FetchFile(master, remoteFolder, baseFileName + '_Master_CH4.wfm', saveDataPath)
    log.Write('Fetching .wfm files from Master complete')

    FetchFile(extB, remoteFolder, baseFileName + '_ExtB_CH1.wfm', saveDataPath)
    FetchFile(extB, remoteFolder, baseFileName + '_ExtB_CH2.wfm', saveDataPath)
    FetchFile(extB, remoteFolder, baseFileName + '_ExtB_CH3.wfm', saveDataPath)
    FetchFile(extB, remoteFolder, baseFileName + '_ExtB_CH4.wfm', saveDataPath)
    log.Write('Fetching .wfm files from Extension B complete')

    FetchFile(extC, remoteFolder, baseFileName + '_ExtC_CH1.wfm', saveDataPath)
    FetchFile(extC, remoteFolder, baseFileName + '_ExtC_CH2.wfm', saveDataPath)
    FetchFile(extC, remoteFolder, baseFileName + '_ExtC_CH3.wfm', saveDataPath)
    FetchFile(extC, remoteFolder, baseFileName + '_ExtC_CH4.wfm', saveDataPath)
    log.Write('Fetching .wfm files from Extension C complete')

    FetchFile(extD, remoteFolder, baseFileName + '_ExtD_CH1.wfm', saveDataPath)
    FetchFile(extD, remoteFolder, baseFileName + '_ExtD_CH2.wfm', saveDataPath)
    FetchFile(extD, remoteFolder, baseFileName + '_ExtD_CH3.wfm', saveDataPath)
    FetchFile(extD, remoteFolder, baseFileName + '_ExtD_CH4.wfm', saveDataPath)
    log.Write('Fetching .wfm files from Extension D complete')


    print('Do you want to delete .wfm files from scopes?')
    userInput = input('Enter \'Y\' to delete .wfms from scopes, anything else to skip deletion: ')
    if userInput == 'Y':
        log.Write('Deleting .wfm files on scopes')
        DeleteFile(master, remoteFolder, baseFileName + '_Master_CH1.wfm')
        DeleteFile(master, remoteFolder, baseFileName + '_Master_CH2.wfm')
        DeleteFile(master, remoteFolder, baseFileName + '_Master_CH3.wfm')
        DeleteFile(master, remoteFolder, baseFileName + '_Master_CH4.wfm')
        log.Write('Deleting .wfm files on Master complete')

        DeleteFile(extB, remoteFolder, baseFileName + '_ExtB_CH1.wfm')
        DeleteFile(extB, remoteFolder, baseFileName + '_ExtB_CH2.wfm')
        DeleteFile(extB, remoteFolder, baseFileName + '_ExtB_CH3.wfm')
        DeleteFile(extB, remoteFolder, baseFileName + '_ExtB_CH4.wfm')
        log.Write('Deleting .wfm files on Extension B complete')

        DeleteFile(extC, remoteFolder, baseFileName + '_ExtC_CH1.wfm')
        DeleteFile(extC, remoteFolder, baseFileName + '_ExtC_CH2.wfm')
        DeleteFile(extC, remoteFolder, baseFileName + '_ExtC_CH3.wfm')
        DeleteFile(extC, remoteFolder, baseFileName + '_ExtC_CH4.wfm')
        log.Write('Deleting .wfm files on Extension C complete')

        DeleteFile(extD, remoteFolder, baseFileName + '_ExtD_CH1.wfm')
        DeleteFile(extD, remoteFolder, baseFileName + '_ExtD_CH2.wfm')
        DeleteFile(extD, remoteFolder, baseFileName + '_ExtD_CH3.wfm')
        DeleteFile(extD, remoteFolder, baseFileName + '_ExtD_CH4.wfm')
        log.Write('Deleting .wfm files on Extension D complete')
    
    log.Write(ErrorQuery(master))

except Exception as e:
    log.Write('Script Terminated early due to exception.')
    log.Write(e)
finally:        
    tScriptEnd = datetime.now()
    totalTime = tScriptEnd-tScriptStart
    log.Write('Script Ended')
    log.Write(f'Total Time: {totalTime}')
    log.Close()
    if master is not None:
        master.close()
    if extB is not None:
        extB.close()
    if extD is not None:
        extD.close()
    if extD is not None:
        extD.close()
    if rm is not None:
        rm.close()
