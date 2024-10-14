
'''An example script for connecting to a scope, setting up the trigger and channels, acquiring a waveform,
   retrieving waveform data from a channel, and plotting the waveform data.

NOTES
- Please change the ADDRESS to your scope's IP address (ADDRESS)
- This program uses an MSO5B, (from tm_device.driver import MSO5B)
- MAKE SURE HSI is enable on the scope! On the scope: Utility > I/O > HIGH SPEED INTERFACE > High Speed Interface > (Toggle) "On"
- This example uses matplotlib, tm_devices, tm_data_types, and tekhsi

- IMPORTANT NOTE: TURN ON High Speed Interface on Scope!
Scope Path: Utility > I/O > High Speed Interface > High Speed Interface

'''

# Importing modules, packages, libraries etc.
# import time # ONLY for code line 58
import matplotlib.pyplot as plt
from tm_devices import DeviceManager                                    # https://pypi.org/project/tm-devices/
from tm_devices.drivers import MSO4B, MSO5, MSO5B, MSO6, MSO6B          # Importing Drivers for Tektronix MSO58B, https://pypi.org/project/tm-devices/
from tm_devices.drivers import DPO70K, DPO70KC, DPO70KD, DPO70KDX, DPO70KSX
from tm_devices.drivers import MSO70K, MSO70KC, MSO70KDX
from tm_data_types import AnalogWaveform                                # Importing Waveform Class, https://pypi.org/project/tm-data-types/ 
from tekhsi import TekHSIConnect                                        # Importing TekHSIConnect, https://pypi.org/project/TekHSI/ 

# Scope VISA, IP, Port Settings
ADDRESS = "xxxx.xxxx.xxxx.xxxx"                                                # Instrument IP Address

# TURN ON High Speed Interface on Scope!
# Path: Utility > I/O > High Speed Interface > High Speed Interface

with DeviceManager(verbose=False) as dm:                                # Create a DeviceManager Object (dm)

    MSO_scope: MSO5B = dm.add_scope(ADDRESS)                            # adding a scope object
    MSO_scope.visa_timeout = 5000                                       # 5000 ms VISA timeout        

    scope = MSO_scope.commands                                          # Aliasing

    print(scope.idn.query())                                            # printout scope ID

    # User input for connecting channel 2
    input('''
    ACTION
    Connect probe to Oscilloscope Channel 2 and the Probe Compensation Signal.
    Press Enter to continue....
    ''')
    
    print("Scope Setup, Acquire, Waveform transfer, and plotting....")

    scope.rst.write()                                                   # scope reset
    scope.opc.query()                                                   # OPC command

    scope.display.waveview1.ch[2].state.write("ON")                     # Turn on ch 2, turn off ch1
    scope.display.waveview1.ch[1].state.write("OFF")                    

    scope.trigger.a.type.write("EDGE")                                  # set edge trigger to ch2
    scope.trigger.a.edge.source.write("CH2")                            
    scope.opc.query()                                                   

    scope.autoset.write("EXECUTE")                                      # scope autoset
    scope.opc.query()                                                   
    # time.sleep(1)                                                     # optional delay
    scope.acquire.state.write("0")                                      # Setup single acquisition
    scope.acquire.stopafter.write("SEQUENCE")                           
    scope.acquire.state.write("1")                                      # single acquisition
    scope.opc.query()

    if int(scope.acquire.state.query()) !=1:                            # Checking that the scope is stopped
        with TekHSIConnect(f"{ADDRESS}:5000") as connection:            # Establish a tekhsi connection to the oscilloscope.
            with connection.access_data():                              # Begin accessing data from the oscilloscope with connection
                waveform: AnalogWaveform = connection.get_data("ch2")   # Retrieve the waveform data for channel 2 from the scope, waveform object

        hd = waveform.normalized_horizontal_values                      # Extract the normalized horizontal (time) values from waveform.
        vd = waveform.normalized_vertical_values                        # Extract the normalized vertical (voltage) values from waveform.

        # Plotting the waveform data
        _, ax = plt.subplots()                                          # Create a new figure and subplot
        ax.plot(hd, vd)                                                 # Plot the waveform
        ax.set(xlabel=waveform.x_axis_units,                            # plot axes labeling
               ylabel=waveform.y_axis_units, title="Simple Plot")
        plt.show()                                                      # Display plot

print("End of tm_devices simple plot example")