#-------------------------------------------------------------------------------
# Name:  Save Hardcopy to PC using PyVisa for TDS, TPS, TBS 1K-2K Series Scopes
# Purpose:  This example demonstrates how to save a hard copy screen image from
#   the scope to the PC.
#
# Created:  2015-09-17
#
# Development Environment: Python 3.4, PyVisa 1.8, NI-VISA 2015, Windows 8.1
#
# Compatible Instruments: TBS1000B, TBS1000, TDS200, TDS1000/2000,
#   TDS1000B/2000B, TDS1000C-EDU/TDS2000C, TDS2024C, TPS2000/TPS2000B Series
#
# Compatible Interfaces:  GPIB, USB, RS-232
#
# Tektronix provides the following example "AS IS" with no support or warranty.
#
#-------------------------------------------------------------------------------

import time # std library
import warnings # std visa libraries
import visa # https://pyvisa.readthedocs.org/en/stable/

vc = visa.constants # Alias for easier reading

# Modify the following lines to configure this script for your instrument
#==============================================
visaResourceAddr = 'TDS2024C'
fileSaveLocation = r'C:\Temp\HardCopy.bmp'
bufferSize = 1024

# Serial Port Settings
baudRate = 9600
flowCtrl = vc.VI_ASRL_FLOW_RTS_CTS
#flowCtrl = vc.VI_ASRL_FLOW_NONE
#==============================================

# Open session to instrument
rm = visa.ResourceManager()
lib = rm.visalib
scope = rm.open_resource(visaResourceAddr)
scope.timeout = 5000

# Some settings depend on which interface is being used
interface = lib.get_attribute(scope.session, vc.VI_ATTR_INTF_TYPE)[0]
port = ''
if interface == vc.VI_INTF_ASRL:
    lib.set_attribute(scope.session, vc.VI_ATTR_ASRL_FLOW_CNTRL, flowCtrl)
    lib.set_attribute(scope.session, vc.VI_ATTR_ASRL_BAUD, baudRate)
    port = 'RS232'
    startDelaySec = 5
elif interface == vc.VI_INTF_USB:
    port = 'USB'
    startDelaySec = 3
elif interface == vc.VI_INTF_GPIB:
    port = 'GPIB'
    startDelaySec = 5

print(scope.query("*IDN?"))
scope.write("HARDCOPY:FORMAT BMP")
scope.write("HARDCOPY:LAYOUT PORTRait")
scope.write("HARDCOPY:PORT " + port)
scope.write("HARDCOPY STARt")

print("Starting Transfer in: ", end = "")
for x in range(0, startDelaySec):
    print(str.format("{0}...", startDelaySec - x), end = "")
    time.sleep(1)
print("Now!")

# If using RS-232 then need to disable end on termination character while reading the image data
if lib.get_attribute(scope.session, vc.VI_ATTR_INTF_TYPE)[0] == vc.VI_INTF_ASRL:
    lib.set_attribute(scope.session, vc.VI_ATTR_ASRL_END_IN, 0)

# Read the BMP header bytes and extract the file size
warnings.filterwarnings("ignore", category=Warning) #The read will produce a VI_SUCCESS_MAX_CNT warning so suppress
imgBytes = lib.read(scope.session, 14)[0]
lengthBytes = imgBytes[2:6]
fileSize = int.from_bytes(lengthBytes, byteorder='little', signed=False)
bytesLeft = fileSize - 14

# Read the rest of the image
while bytesLeft > 0:
    imgBytes = imgBytes + lib.read(scope.session, bufferSize)[0]
    bytesLeft = bytesLeft - bufferSize

    if bytesLeft < bufferSize:
        imgBytes = imgBytes + lib.read(scope.session, bytesLeft)[0]
        bytesLeft = 0

# Re-enable end on termination character for RS-232
if lib.get_attribute(scope.session, vc.VI_ATTR_INTF_TYPE)[0] == vc.VI_INTF_ASRL:
    lib.set_attribute(scope.session, vc.VI_ATTR_ASRL_END_IN, 1)

# Save the bytes to a file
imgFile = open(fileSaveLocation, "wb")
imgFile.write(imgBytes)
imgFile.close()

print("Transfer Complere!")
print("Image saved to " + fileSaveLocation)

scope.close()
rm.close()

