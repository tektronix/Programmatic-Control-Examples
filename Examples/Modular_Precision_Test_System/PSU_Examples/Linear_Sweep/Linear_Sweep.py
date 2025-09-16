import pyvisa as visa
import matplotlib.pyplot as plt

rm = visa.ResourceManager()    # for purely pyvisa implementation pass '@py'
print(rm.list_resources())
mypsu = rm.open_resource("TCPIP0::192.168.0.2::5025::SOCKET")    
                                                                   
mypsu.write_termination = "\n"    # for using the sockets based implementation
mypsu.read_termination = "\n"
mypsu.send_end = True
mypsu.timeout = 10000

###############################################################################################
#    Example code below is intended to demonstrate how to take voltage and current readings
#    and increase voltage through trials

#    ***  slot[modSlot].psu[modChan] defines the module "modSlot" and channel "modChan" for 
#         which the function is being called   ***
###############################################################################################

def set_channel(modSlot, modChan, volt, curr):
    chan = f"slot[{modSlot}].psu[{modChan}]"

    mypsu.write(f"{chan}.source.levelv = {volt}")
    mypsu.write(f"{chan}.source.limiti = {curr}")

#    mypsu.write(f"{chan}.source.output = slot[{modSlot}].psu.ON")        ---Use when standalone function not nested in Sweep()

    voltVal = mypsu.query(f"print({chan}.measure.v())") # Aquire voltage/current measurements
    currVal = mypsu.query(f"print({chan}.measure.i())")

#    mypsu.write(f"{chan}.source.output = slot[{modSlot}].psu.OFF")       ---Use when standalone function not nested in Sweep()
    return([voltVal, currVal])

###############################################################################################
#   This function plots the data from the sweep

#   PARAMETERS  -
#               voltageReadings : list of voltage readings from sweep
#               currentReadings : list of current readings from sweep
###############################################################################################

def plot_results(voltageReadings, currentReadings):
    
    plt.scatter(voltageReadings, currentReadings)

    plt.xlabel("Voltage (V)")
    plt.ylabel("Current (A)")

    plt.show()

###############################################################################################
#    The example below will perform a linear voltage sweep 

#    PARAMETERS  -   
#                modSlot : Module for given DUT
#                modChan : Channel for given DUT
#                start : starting value of voltage sweep
#                stop :  stoping value of voltage sweep
#                step :  step increment size
#                setCurr : Programmed current limit
###############################################################################################

def Sweep(modSlot, modChan, start, stop, step, setCurr):
    # Alais psu
    chan = f"slot[{modSlot}].psu[{modChan}]"
    # Configure channel for test
    vals = set_channel(modSlot, modChan, 0, setCurr)
    mypsu.write(f"{chan}.source.output = slot[{modSlot}].psu.ON")
    
    # Create lists to contain readings
    voltageReadings = [0] * (int((stop - start) / step) + 1)
    currentReadings = [0] * (int((stop - start) / step) + 1)

    # Iterate through voltages in sweep, aquiring measurements along the way
    v = start
    print(f"Module {modSlot}/Channel {modChan}:")
    print(f" ")
    while (v <= stop):
        print("Set Voltage:", v, "Set Current:", setCurr)
        vals = set_channel(modSlot, modChan, v, setCurr)
        mypsu.write("delay(1)") # Constant delay of one second

        print(f"Voltage Reading: {float(vals[0]):.3f} Current Reading: {float(vals[1]):.3f}")
        print(f" ")

        #Add readings to lists for plotting
        voltageReadings[int((v - start) / step)] = float(vals[0])
        currentReadings[int((v - start) / step)] = float(vals[1])

        v += step

    mypsu.write(f"{chan}.source.output = slot[{modSlot}].psu.OFF")
    plot_results(voltageReadings, currentReadings)
    print("Done")

Sweep(2, 2, 0.5, 5, 0.5, 1) #UPDATE THIS LINE IF YOU WISH TO CHANGE THE SWEEP

mypsu.close()
rm.close()