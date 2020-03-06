import time # std library
import warnings # std visa libraries
import visa # https://pyvisa.readthedocs.org/en/stable/

vc = visa.constants # Alias for easier reading

# Modify the following lines to configure this script for your instrument
#==============================================
visaResourceAddr = 'MSO58-PQ100007'
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
scope.write("DATA:START 1")
scope.write("DATA:STOP 1000")
scope.write("DATA:ENCDG ASCII")
scope.write("ACQUIRE:STOP")
scope.query(":CURVE?")
