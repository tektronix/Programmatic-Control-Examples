#-------------------------------------------------------------------------------
# Name:  Save Hardcopy to PC using PyVisa for MSO/DPO/MDO 2K 3K 4K Series Scopes
# Purpose:  This example demonstrates how to save a hard copy screen image from
#   the scope to the PC.
#
# Created:  2016-05-23
#
# Development Environment: Python 3.4, PyVisa 1.8, NI-VISA 2015, Windows 8.1
#
# Compatible Instruments: MSO/DPO/MDO 2000, 3000 & 4000 Series Oscilliscopes
#
# Compatible Interfaces:  USB, Ethernet, GPIB
#
# Tektronix provides the following example "AS IS" with no support or warranty.
#
#-------------------------------------------------------------------------------

from datetime import datetime # std library
import visa # https://pyvisa.readthedocs.org/en/stable/

# Modify the following lines to configure this script for your instrument
#==============================================
visaResourceAddr = 'MDO3104'
fileSaveLocation = r'C:\Temp\\' # Folder on your PC where to save image
#==============================================

rm = visa.ResourceManager()
scope = rm.open_resource(visaResourceAddr)

print(scope.query('*IDN?'))

scope.write("SAVe:IMAGe:FILEFormat PNG")
scope.write("SAVe:IMAGe:INKSaver OFF")
scope.write("HARDCopy STARt")
imgData = scope.read_raw()

# Generate a filename based on the current Date & Time
dt = datetime.now()
fileName = dt.strftime("%Y%m%d_%H%M%S.png")

imgFile = open(fileSaveLocation + fileName, "wb")
imgFile.write(imgData)
imgFile.close()

scope.close()
rm.close()


