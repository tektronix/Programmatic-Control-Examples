# Get simple measurement using tm_devices
Original Attribution: Gayland P - Tektronix Applications

This is a simple example using Tektronix tm_devices tools to connect to an oscilloscope by USB connection. This program finds the maximum peak to peak voltage value on a signal connected to Channel 1 of a 6 Series B oscilloscope. It runs the oscilloscope 10 times for 3 seconds at a time and publishes the results to a file in a C:\\Test directory. Very minor changes would be needed to use this script with a 5 Series, 4 series, or other 6 series oscilloscopes.

For a description of tm_devices please go to https://pypi.org/project/tm-devices.

This script uses numpy arrays, and assumes that the user has a version of VISA loaded on their PC that supports USB control of instrumentation, such as TekVISA, or NI-VISA.
