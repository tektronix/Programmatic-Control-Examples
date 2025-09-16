"""

    ***********************************************************
    *** Copyright 2025 Tektronix, Inc.                      ***
    *** See www.tek.com/sample-license for licensing terms. ***
    *********************************************************** 

    Output_Sequence_Demo.py

    This script does output on and off sequencing using trigger models and sending individual TSP commands for a singular fully loaded MP5103 mainframe. 
"""

import pyvisa
import time

numberChannels = 6 # number of channels configured for output on/off sequence

# power supply alias names
chs = [None] * numberChannels
slots = [None] * (round(numberChannels / 2))
for i in range(numberChannels): # configures channels starting from slot 1 to 3
    chs[i] = f"slot[{int(i/2)+1}].psu[{(i%2) + 1}]"
    slots[int(i/2)] = f"slot[{int(i/2) + 1}]"


# enable channels (True = enabled, False = disabled)
enables = [
        True, # Channe1 1
        True, # Channel 2
        True, # Channel 3
        True, # Channel 4
        True, # Channel 5
        True  # Channel 6
    ] 

def configureOutputOnSequence(instrument, delays, vLevel):
    """
        configureOutputOnSequence configures a output on sequence for the enabled channels using a trigger model for each channel.

        :param instrument: PyVISA resource object
        :param delayChannels: List of delays before each channel turns on. Min: 0s, Max: 2^34s

        :return: None
    """ 
    
    for i in range(numberChannels):
        if (enables[i]):
            instrument.write(f"{chs[i]}.trigger.source.listv({{{vLevel[i]}}})") # set turn on voltage level
            instrument.write(f"{slots[int(i/2)]}.trigger.model.create(\"onCh{i+1}\")") # create trigger model
            instrument.write(f"{slots[int(i/2)]}.trigger.model.addblock.wait(\"onCh{i+1}\",\"Wait\", trigger.generator[1].EVENT_ID)") # wait until trigger signal received
            instrument.write(f"{slots[int(i/2)]}.trigger.model.addblock.delay.constant(\"onCh{i+1}\", \"delayTurnOn\", {delays[i]})") # delay before channel turn on
            instrument.write(f"{slots[int(i/2)]}.trigger.model.addblock.source.action.step(\"onCh{i+1}\", \"chOn\", {(i%2)+1})") # go to turn on voltage level

def outputsOn(instrument):
    """
        outputsOn turns on the output for on all the enabled channels using the configured output on sequence.

        :param instrument: PyVISA resource object
        :return: None
    """ 
    
    # turn on outputs to 0V then initiate trigger models
    for i in range(numberChannels):
        if(enables[i]):
            instrument.write(f"{chs[i]}.source.levelv = 0")
            instrument.write(f"{chs[i]}.source.output = 1")
            instrument.write(f"{slots[int(i/2)]}.trigger.model.initiate(\"onCh{i+1}\")")
    
    instrument.write("trigger.generator[1].assert()") # trigger all the trigger models simulatenously
    
    instrument.query("*OPC?") # wait until all outputs are on

def configureOutputOffSequence(instrument, delays):
    """
        configureOutputOffSequence configures a output off sequence for the enabled channels using a trigger model for each channel.

        :param instrument (PyVISA): PyVISA resource object
        :param delayChannels: List of delays before each channel turns off. Min: 0s, Max: 2^34s

        :return: None
    """ 
    for i in range(numberChannels):
        if (enables[i]):
            instrument.write(f"{slots[int(i/2)]}.trigger.model.create(\"offCh{i+1}\")") # create trigger model
            instrument.write(f"{slots[int(i/2)]}.trigger.model.addblock.wait(\"offCh{i+1}\",\"Wait\", trigger.generator[1].EVENT_ID)") # wait until trigger signal received
            instrument.write(f"{slots[int(i/2)]}.trigger.model.addblock.delay.constant(\"offCh{i+1}\", \"delayTurnOn\", {delays[i]})") # delay before channel turn on
            instrument.write(f"{slots[int(i/2)]}.trigger.model.addblock.source.output(\"offCh{i+1}\", \"chOff\", {(i%2)+1}, 0)") # turn off channel

def outputsOff(instrument):
    """
        outputsOn turns on the output for on all the enabled channels using the configured output off sequence.

        :param instrument: PyVISA resource object
        :return: None
    """
    
    # Initiate output off seqeuence trigger models
    for i in range(numberChannels):
        if (enables[i]):
            instrument.write(f"{slots[int(i/2)]}.trigger.model.initiate(\"offCh{i+1}\")")

    instrument.write("trigger.generator[1].assert()") # trigger all the trigger models simulatenously

    instrument.query("*OPC?") # wait until all outputs are off

def cleanUpOutputSequence(instrument): 
    """
        cleanUpOutputSequence deletes any configured trigger models used for output sequencing.

        :param instrument: PyVISA resource object
        :return: None
    """
    for i in range(numberChannels):
        if(enables[i]):
            instrument.write(f"{slots[int(i/2)]}.trigger.model.delete(\"onCh{i+1}\")")
            instrument.write(f"{slots[int(i/2)]}.trigger.model.delete(\"offCh{i+1}\")")

def errorCheck(instrument):
    """
        cleakErrors prints any errors present in the error queue.

        :param instrument: PyVISA resource object
        :return: None
    """
    
    errorCount = int(float(instrument.query("print(errorqueue.count)"))) # get number of errors
    if(errorCount > 0):
        print(f"Error Queue Count: {errorCount}")
        for i in range(0, errorCount): # print all errors
            print(instrument.query(f"print({i}, errorqueue.next())"))
    
def main():
    
    resourceString = "TCPIP0::134.63.75.188::5025::SOCKET" # instrument resource string
        
    # configure VISA connection
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource(resourceString)
    instrument.timeout = 10000 # instrument timeout time
    if "SOCKET" in resourceString:
        instrument.write_termination = "\n"
        instrument.read_termination = "\n"
        instrument.send_end = True
    
    # voltage level for each channel
    vLevel = [
        5, # Channe1 1
        5, # Channel 2
        5, # Channel 3
        5, # Channel 4
        5, # Channel 5
        5  # Channel 6
    ] 

     # current limit for each chanel    
    iLimit = [
        5, # Channe1 1
        5, # Channel 2
        5, # Channel 3
        5, # Channel 4
        5, # Channel 5
        5  # Channel 6
    ]
    
     # slew rate for each channel in V/s
    slewRate = [
        10000, # Channe1 1
        10000, # Channel 2
        10000, # Channel 3
        10000, # Channel 4
        10000, # Channel 5
        10000  # Channel 6
    ]
      
    # set current limit and slew rate
    for i in range(numberChannels):
        if(enables[i]):
            instrument.write(f"{chs[i]}.source.limiti = {iLimit[i]}")
            instrument.write(f"{chs[i]}.source.slewratev = {slewRate[i]}")

    # output sequence channel on delays in seconds
    onDelays = [
        0.000, # Channe1 1
        0.005, # Channel 2
        0.010, # Channel 3
        0.015, # Channel 4
        0.020, # Channel 5
        0.025  # Channel 6
    ] 

    # output sequence channel off delays in seconds
    offDelays = [
        0.025, # Channe1 1
        0.020, # Channel 2
        0.015, # Channel 3
        0.010, # Channel 4
        0.005, # Channel 5
        0.000  # Channel 6
    ] 
    
    instrument.timeout = 1000+1000*max(instrument.timeout/1000, max(onDelays), max(offDelays)) # set the timeout to 1 second greater than the highest on/off delay

    # cofigure output sequence
    configureOutputOnSequence(instrument, onDelays, vLevel) # configure output on sequence
    configureOutputOffSequence(instrument, offDelays) # configure output off sequence
    
    outputsOn(instrument) # turn outputs on using output on sequence
    
    # run any tests while device is powered
    minOnTime = 0.005 # minimum time between channel turn on sequence and off sequence
    time.sleep(minOnTime)
    
    outputsOff(instrument)  # turn outputs off using output off sequence
    
    cleanUpOutputSequence(instrument) # clean up output sequence information stored on instrument
    
    errorCheck(instrument) # check for errors generated

    instrument.clear() # clear connection
    instrument.close() # close VISA session
    rm.close() # close resource manager session

main() # run main program
