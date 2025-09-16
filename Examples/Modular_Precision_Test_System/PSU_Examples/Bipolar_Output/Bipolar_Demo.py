import pyvisa
import time

# Configure Visa Connection
rm = pyvisa.ResourceManager()
inst = rm.open_resource('TCPIP0::192.168.0.2::5025::SOCKET')#TCPIP0::134.63.75.230::1394::SOCKET
inst.write_termination = "\n"    # for using the sockets based implementation
inst.read_termination = "\n"
inst.send_end = True
inst.timeout = 10000

print(inst.query("*IDN?"))
inst.write("reset()") # reset instrument

#UPDATE THESE FOR DIFFERENT SLOT/CHANNEL
slot = "slot[2]"
channel = "psu[2]"

# Configure Source limit and source level
inst.write(f"{slot}.{channel}.source.limiti = 1")
inst.write(f"{slot}.{channel}.source.levelv = 1.5")

inst.write(f"{slot}.{channel}.source.output = 1") # Output on

print(f"\nForward Bias Voltage at {float(inst.query(f"print({slot}.{channel}.measure.i())"))} A: {float(inst.query(f"print({slot}.{channel}.measure.v())"))} V") # Measure voltage output

time.sleep(2)

#UPDATE IF USING DIFFERENT DIODE
inst.write(f"{slot}.{channel}.source.limiti = 0.065")
inst.write(f"{slot}.{channel}.source.levelv = -25") # Change source voltage level

print(f"Reverse Bias Voltage at {float(inst.query(f"print({slot}.{channel}.measure.i())"))} A: {float(inst.query(f"print({slot}.{channel}.measure.v())"))} V") # Measure voltage output

time.sleep(2)

inst.write(f"{slot}.{channel}.source.output = 0") # Turn off output

inst.clear()
inst.close()