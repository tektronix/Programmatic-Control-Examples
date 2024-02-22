#-------------------------------------------------------------------------------
# Name:  Save Hardcopy to PC using PyVisa for MSO/DPO 5K 7K & 70K Series Scopes
# Purpose:  This example demonstrates how to save a hard copy screen image from
#   the scope to the PC.
#
# Development Environment: Python 3.4, PyVisa 1.8, NI-VISA 2015, Windows 8.1
#
# Compatible Instruments: MSO/DPO 5000(B), 7000(C) & 70000(B)(C)(D)(DX)(SX) Series Oscilliscopes
#
# Compatible Interfaces:  USB, Ethernet
#
# Changelog:
#   2024-02-22:
#     Updated temporary file path for screenshot to be compatible with Windows 10 security settings
#
#   2016-05-23:
#     Original Revision
#
# Tektronix provides the following example "AS IS" with no support or warranty.
#
#-------------------------------------------------------------------------------

from datetime import datetime # std library
import visa # https://pyvisa.readthedocs.org/en/stable/

# Modify the following lines to configure this script for your instrument
#==============================================
visaResourceAddr = 'TCPIP::192.168.1.100::inst0:INSTR'
fileSaveLocation = 'C:\\Users\\Public\\Pictures\\' # Folder on your PC where to save image
#==============================================

rm = visa.ResourceManager()
scope = rm.open_resource(visaResourceAddr)

print(scope.query('*IDN?'))

scope.write("HARDCopy:PORT FILE;")
scope.write("EXPort:FORMat PNG")

# Set where the file will be saved on the scope's hard drive.  This is not
# where it will be saved on your PC.
tempFilePath = "\"C:\\Users\\Tek_local_admin\\Pictures\\Temp.png\""
scope.write("HARDCopy:FILEName " + tempFilePath)

scope.write("HARDCopy STARt")

# Read the image file from the scope's hard drive
scope.write("FILESystem:READFile " + tempFilePath)
imgData = scope.read_raw()

# Generate a filename based on the current Date & Time
dt = datetime.now()
fileName = dt.strftime("%Y%m%d_%H%M%S.png")

# Save the transfered image to the hard drive of your PC
imgFile = open(fileSaveLocation + fileName, "wb")
imgFile.write(imgData)
imgFile.close()

# Delete the image file from the scope's hard drive.
scope.write("FILESystem:DELEte " + tempFilePath)

scope.close()
rm.close()

