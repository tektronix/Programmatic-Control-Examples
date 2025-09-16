import pyvisa

# Configure Visa Connection
rm = pyvisa.ResourceManager()
inst = rm.open_resource('TCPIP0::192.168.0.2::5025::SOCKET')#TCPIP0::134.63.75.230::1394::SOCKET
inst.write_termination = "\n"    # for using the sockets based implementation
inst.read_termination = "\n"
#inst.send_end = True
inst.timeout = 10000

print(inst.query("*IDN?"))
inst.write("reset()") # reset instrument

#CHANGE THESE FOR NEW SLOT/CHANNEL
slot = 2
channel = 2

# Configure source limit, level, OCP level, and OCP enable
inst.write(f"slot[{slot}].psu[{channel}].source.limiti = 350e-3")
inst.write(f"slot[{slot}].psu[{channel}].source.levelv = 15")
inst.write(f"slot[{slot}].psu[{channel}].source.protect.leveli = 500e-3")
inst.write(f"slot[{slot}].psu[{channel}].source.protect.enablei = slot[{slot}].psu[{channel}].ENABLE")

inst.write(f"slot[{slot}].psu[{channel}].source.output = 1") # Output On

# Wait while output is on
outputOn = inst.query(f"print(slot[{slot}].psu[{channel}].source.output)")
while(outputOn == 'ON'):
    outputOn = inst.query(f"print(slot[{slot}].psu[{channel}].source.output)")

print(f"\nOCP Tripped: {inst.query(f"print(slot[{slot}].psu[{channel}].source.protect.trippedi)")}") # OCP Tripped query


inst.close()