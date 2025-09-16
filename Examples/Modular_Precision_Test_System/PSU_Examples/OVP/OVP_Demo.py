""" Demo Code """
import pyvisa as visa
import time

rm = visa.ResourceManager()    # for purely pyvisa implementation pass '@py'
print(rm.list_resources())
mypsu = rm.open_resource("TCPIP0::192.168.0.2::5025::SOCKET")    
                                                                    
mypsu.write_termination = "\n"    # for using the sockets based implementation
mypsu.read_termination = "\n"
mypsu.send_end = True
mypsu.timeout = 10000

#UPDATE THIS TO CHANGE SLOT/CHANNEL
chan = "slot[2].psu[1]"

v_start = 5.0
v_end = 20
i_start = 1
i_end = 2
ovp_level = 12
ocp_level = 5.5

mypsu.write("reset()")

#Configure Channel"
mypsu.write(f"{chan}.source.levelv = {v_start}")
mypsu.write(f"{chan}.source.limiti = {i_start}")

#Configure Protect
mypsu.write(f"{chan}.source.protect.levelv = {ovp_level}")
mypsu.write(f"{chan}.source.protect.leveli = {ocp_level}")

#delay
time.sleep(2.5)

#turn output on
mypsu.write(f"{chan}.source.output = 1")

#Configure Channel to higher level"
mypsu.write(f"{chan}.source.levelv = {v_end}")
mypsu.write(f"{chan}.source.limiti = {i_end}")

mypsu.close()
rm.close()


