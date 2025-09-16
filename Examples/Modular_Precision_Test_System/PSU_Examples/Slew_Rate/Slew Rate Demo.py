#########################################################################################
# This script toggles outputs with varying slewrates to demonstrate this feature. 
# This is best paired with a scope to capture the  effects. 
#########################################################################################

import pyvisa

# Configure Visa Connection
rm = pyvisa.ResourceManager()
inst = rm.open_resource('TCPIP0::192.168.0.2::5025::SOCKET')
inst.write_termination = "\n"    # for using the sockets based implementation
inst.read_termination = "\n"
#inst.send_end = True
inst.timeout = 10000

print(inst.query("*IDN?"))
inst.write("reset()") # Reset instrument

# Alais PSU, change to change slot/channel
module = "slot[2].psu[1]"

# Configure source i-limit, v-level
inst.write(f"{module}.source.limiti = 1")
inst.write(f"{module}.source.levelv = 5")

# Slew Rate of 1 v/s
inst.write(f"{module}.source.slewratev = 1")
inst.write(f"{module}.source.output = 1") # Output On
inst.write("delay(1)") 
inst.write(f"{module}.source.output = 0") # Output Off
inst.write("delay(1)") 

# Slew Rate of 10000 v/s
inst.write(f"{module}.source.slewratev = 10000")
inst.write(f"{module}.source.output = 1") # Output On
inst.write("delay(1)") 
inst.write(f"{module}.source.output = 0") # Output Off

inst.close() # Close instrument connection