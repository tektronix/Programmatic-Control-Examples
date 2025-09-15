"""

    ***********************************************************
    *** Copyright 2025 Tektronix, Inc.                      ***
    *** See www.tek.com/sample-license for licensing terms. ***
    *********************************************************** 

    Output_Sequence_TSP_Functions_Demo.py

    This script does output on and off sequencing using trigger models and TSP functions for a singular fully loaded MP5103 mainframe.
"""

import pyvisa
import time

numberChannels = 6 # number of channels configured for outut on/off sequence

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

def sendOutputSequenceFunctions(instrument):
    """
        sendOutputSequenceFunctions sends a TSP script that contains TSP functions to call for output sequencing.
        Note: This function is only required to be called once when configuring the test for the first time.

        :param instrument: PyVISA resource object
        :return: None
    """ 
    
    instrument.write(
        """loadscript outputSequence
        
        function configureOutputOnSequence(enables, slots, chs, delays, vLevel)

            -- configure channel trigger models
            for i = 1, table.getn(enables), 1 do
                if enables[i] then
                    chs[i].trigger.source.listv({vLevel[i]}) -- set turn on voltage level
                    slots[math.ceil(i/2)].trigger.model.delete("onCh"..i)
                    slots[math.ceil(i/2)].trigger.model.create("onCh"..i)
                    slots[math.ceil(i/2)].trigger.model.addblock.wait("onCh"..i,"Wait", trigger.generator[1].EVENT_ID) -- wait for trigger event
                    slots[math.ceil(i/2)].trigger.model.addblock.delay.constant("onCh"..i, "delayTurnOn", delays[i]) -- delay before turn on
                    slots[math.ceil(i/2)].trigger.model.addblock.source.action.step("onCh"..i, "chOn", 2-math.mod(i,2)) -- go to turn on voltage level
                end
            end
        end

        -- Turns all channels on
        function outputsOn(enables, slots, chs)

            -- turn on outputs to 0V then initiate trigger models
            for i = 1, table.getn(enables), 1 do
                if enables[i] then
                    chs[i].source.levelv = 0 
                    chs[i].source.output = 1
                    slots[math.ceil(i/2)].trigger.model.initiate("onCh"..i)
                end
            end

            trigger.generator[1].assert() -- trigger all configured channels to begin output on sequencing
        end
        
        -- Configure output off sequence
        function configureOutputOffSequence(enables, slots, delays)

            -- configure channel trigger models
            for i = 1, table.getn(enables), 1 do
                if enables[i] then
                    slots[math.ceil(i/2)].trigger.model.delete("offCh"..i)
                    slots[math.ceil(i/2)].trigger.model.create("offCh"..i)
                    slots[math.ceil(i/2)].trigger.model.addblock.wait("offCh"..i,"Wait", trigger.generator[1].EVENT_ID) -- wait for trigger event
                    slots[math.ceil(i/2)].trigger.model.addblock.delay.constant("offCh"..i, "delayTurnOn", delays[i]) -- delay before turn off
                    slots[math.ceil(i/2)].trigger.model.addblock.source.output("offCh"..i, "chOff", 2-math.mod(i,2), 0) -- turn off channel
                end
            end
        end

        -- Turns all channels off
        function outputsOff(enables, slots)

            -- initiate trigger models
            for i = 1, table.getn(enables), 1 do
                if enables[i] then
                    slots[math.ceil(i/2)].trigger.model.initiate("offCh"..i)
                end
            end

            trigger.generator[1].assert() -- trigger all configured channels to begin output off sequencing
        end

        -- Deletes any configured trigger models used for output sequencing.
        function cleanUpOutputSequence(enables, slots)

            -- delete trigger models
            for i = 1, table.getn(enables), 1 do
                if enables[i] then
                    slots[math.ceil(i/2)].trigger.model.delete("onCh"..i)
                    slots[math.ceil(i/2)].trigger.model.delete("offCh"..i)
                end
            end
        end
        endscript
        outputSequence.run()""")
    
def configureOutputOnSequence(instrument, delays, vLevel):
    """
        configureOutputOnSequence configures a output on sequence for the enabled channels using a trigger model for each channel.

        :param instrument: PyVISA resource object
        :param delayChannels: List of delays before each channel turns on. Min: 0s, Max: 2^34s

        :return: None
    """ 
    
    instrument.write(f"configureOutputOnSequence({pythonListToLua(enables)}, {pythonListToLua(slots)}, {pythonListToLua(chs)}, {pythonListToLua(delays)}, {pythonListToLua(vLevel)})") # configure output on sequence

def outputsOn(instrument):
    """
        outputsOn turns on the output for on all the enabled channels using the configured output on sequence.

        :param instrument: PyVISA resource object
        :return: None
    """ 
    
    instrument.write(f"outputsOn({pythonListToLua(enables)}, {pythonListToLua(slots)}, {pythonListToLua(chs)})") # turn outputs on in configured sequence
    
    instrument.query("*OPC?") # wait until all outputs are on

def configureOutputOffSequence(instrument, delays):
    """
        configureOutputOffSequence configures a output off sequence for the enabled channels using a trigger model for each channel.

        :param instrument (PyVISA): PyVISA resource object
        :param delayChannels: List of delays before each channel turns off. Min: 0s, Max: 2^34s

        :return: None
    """ 
    
    instrument.write(f"configureOutputOffSequence({pythonListToLua(enables)}, {pythonListToLua(slots)}, {pythonListToLua(delays)})") # configure output off sequence
    
def outputsOff(instrument):
    """
        outputsOn turns on the output for on all the enabled channels using the configured output off sequence.

        :param instrument: PyVISA resource object
        :return: None
    """

    instrument.write(f"outputsOff({pythonListToLua(enables)}, {pythonListToLua(slots)}, {pythonListToLua(chs)})") # turn outputs off in configured sequence
    
    instrument.query("*OPC?") # wait until all outputs are off

def cleanUpOutputSequence(instrument): 
    """
        cleanUpOutputSequence deletes any configured trigger models used for output sequencing.

        :param instrument: PyVISA resource object
        :return: None
    """
    
    instrument.write(f"cleanUpOutputSequence({pythonListToLua(enables)}, {pythonListToLua(slots)})") # delete trigger models once test completed

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
            
def pythonListToLua(pythonList):
    """
            pythonListToLua converts a python list to a lua list

            :param pythonList: Python list
            :return: string containing lua list
    """
    
    def pythonToLua(element):
        """
                pythonToLua converts a python list element to equivalent lua list element

                :param pythonList: Python list
                :return: string for one element in lua list
        """
        if element is True:
            return "true"
        elif element is False:
            return "false"
        else:
            return str(element)

    # Join elements into a comma-separated string
    return "{" + ", ".join(pythonToLua(element) for element in pythonList) + "}"

def main():
    
    resourceString = "TCPIP0::192.168.0.2::5025::SOCKET" # instrument resource string
        
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
    
    instrument.timeout = 1000+1000*max(instrument.timeout/1000, max(onDelays), max(offDelays)) # set the timeout to 1 second greater than the highest delay
    
    # cofigure output sequence
    sendOutputSequenceFunctions(instrument) # configure TSP functions for output sequencing
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
