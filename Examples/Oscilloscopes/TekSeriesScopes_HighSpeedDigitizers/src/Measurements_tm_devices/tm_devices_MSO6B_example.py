# This is an introductory python script originally written with pycharm IDE.  This shows how to use tm_devices
# for a relatively realistic short automation routine.  Its goal is to find the maximum peak to peak
# value of a signal on CH1 for a period of three seconds for 10 separate periods.

# to use this script please create a folder under "C" drive called "Test"

# This program uses tm_devices.  see https://pypi.org/project/tm-devices/ for more details.
# Device Manager interacts with pyvisa (and if a third party VISA is installed pyvisa interacts
# with that).  It has the routines that control instruments.
from tm_devices import DeviceManager

# Now we import the specific drivers that control the individual instrument, in this case a B version 6-series
from tm_devices.drivers import MSO6B
# Import time so we can use time.sleep()
import time
# Import Numpy (https://pypi.org/project/numpy/) to use numpy's array tools
import numpy as np

# set up initial values, including the numpy array.
i = 0
NumberOfRuns = 10
MaxPKtoPK = np.zeros(NumberOfRuns)

#  Set up and connect to scope and check its idn string to ensure we connected. verbose in the DeviceManager
#  means you can see all commands going to instrument and all responses to queries which is useful for debug, or
#  not. Here we chose "false" so that we do not print those out.
with DeviceManager(verbose=False) as device_manager:
    scope: MSO6B = device_manager.add_scope("MSO68B-B025464", connection_type="USB" )
    print(scope.idn_string)

    # default the oscilloscope so that it is in a standard condition
    scope.reset()

    # Run Autoset to get the signal set up on screen. Followed by OPC query to ensure it completes.
    scope.commands.autoset.write("EXEC")
    scope.commands.opc.query()
    # Set up horizontal record length to 1 million points.
    scope.commands.horizontal.mode.write("MANual")
    scope.commands.horizontal.recordlength.write(1e6)
    # Ad Meas1 as a PK2PK measurement and display all stats in the badge
    # Then add a second Risetime measurement using a different method within tm_devices.
    scope.add_new_measurement("MEAS1", "PK2PK", "CH1")
    scope.commands.measurement.meas[1].displaystat.enable.write("ON")
    scope.commands.measurement.addmeas.write("RISETIME")
    scope.commands.measurement.meas[2].source.write("CH1")

    # stop the scope
    scope.commands.acquire.state.write("OFF")
    # This loop first clear the previous measurement values, starts the scope and runs it for 3 seconds, stops the
    # scope. and then add the Maximum peak to peak measurement value to the numpy array.
    while i < NumberOfRuns:
        scope.commands.clear.write()
        scope.commands.acquire.state.write("ON")
        time.sleep(3)
        scope.commands.acquire.state.write("OFF")
        MaxPKtoPK[i] = scope.commands.measurement.meas[1].results.allacqs.maximum.query()
        i = i+1
    # Create the output file in the folder "Test" and use a numpy command to save the data into it.
    filename = "C:\\Test\\MaxAmp.txt"
    np.savetxt(filename, MaxPKtoPK)

