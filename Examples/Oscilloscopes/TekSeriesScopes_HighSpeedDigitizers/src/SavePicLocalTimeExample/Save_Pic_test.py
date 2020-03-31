''' 
Author: FAE team Americas and COE (US, AU)
Python 3 64-bit 
NumPy 1.11.2, MatPlotLib 2.0.0, PyVISA 1.11
To get PyVISA: pip install pyvisa
Tested on MSO5/MSO6 (FW 1.24)
NI-VISA was used on PC.

This is a script that uses PyVISA to connect to an MSO5 or MSO6 series oscilloscope.
It will enable CH1, single trigger, and then transfer an inverted picture to a file location
on a remote PC. 
'''

# import the following modules
import pyvisa # This allows high level VISA communications
import time # This allows you to "sleep" from time to time
import numpy as np # numpy allows easier array manipulation

"""#################SEARCH/CONNECT#################"""
# The first commented out lines enable direct connection to a scope.
#rm = pyvisa.ResourceManager() 
#print(rm.list_resources())
# Open the scope resource on the USB port
#scope = rm.open_resource("USB::0x0699::0x0522::C010909::INSTR")
# Alternatively open the scope resource on the ethernet port
#scope = rm.open_resource("TCPIP::10.233.17.14::inst0::INSTR")

# This section looks at all the resources connected to the Visa Resource Manager
# and allows you to connect to the one you want based on its name.

idns_retry = True
while idns_retry:
    rm = pyvisa.ResourceManager()
    dev_addrs = rm.list_resources()
    devs = [rm.open_resource(ele) for ele in dev_addrs]
    idns = [ele.query('*IDN?') for ele in devs]
   
    if len(idns) == 0:
        print('No instruments detected. Check NI MAX to debug.',end='')
        tmp1 = input('Press r to reattempt connection. Any other key exits program.')
        if tmp1 != 'r':    
            exit(0)
    else:
        idns_retry = False

print('Please select acquisition target number from the following devices (select number, press Enter):')
for i,idn in enumerate(idns):
    print('  '+str(i+1)+') '+idn)
while True:
    selection = input('>')
    Devnum = int(selection)-1
    if int(selection)-1 in list(range(len(idns))):
        # this connects to the scope.
        scope = devs[Devnum]
        break
    else:
        print('Invalid selection. Please try again.')

time.sleep(1)
# Visa timout setting so that queries don't crash
scope.timeout = 12000

# Identify the oscillosocpe
print (scope.query("*IDN?"))


def Clear_Scope_Error_Register():
    # This function clears the error register of the oscilloscope
    ESR = scope.query('*ESR?')
    print("Error Status Register, ESR, is ",ESR)
    print(scope.query('allev?'))

def Transfer_picture(number):
# Function to trigger, Get a number of screen capture and send to PC
    print("Saving Screen captures to PC.")
    Totaltime = 0
    for i in range (0,number):
        #Trigger oscilloscope
        start_time=time.time()
        scope.write("ACQuire:STATE RUN")
        scope.query("*OPC?")
        # Save the screen image locally based on which screen shot it is
        # If the MSO5/6 oscilloscope has windows installed, you cannot save to the root C:
        # due to windows restrictions on saving to the root.
        strnumber=str(i)
        # Get the start time for saving the screen shot.
        
        scope.write('SAVe:IMAGe "C:\\MyScreenFrame'+strnumber+'.png"')
        scope.query("*OPC?")
        # Read the screen shot into the Visa Buffer
        scope.write('FILESYSTEM:READFILE "C:\\MyScreenFrame'+strnumber+'.png"')

        # Read the data from the visa buffer and check for errors
        try:
            raw_data =scope.read_raw()
        except pyvisa.VisaIOError as e:
            print("There was a visa error with the following message: {0} ".format(repr(e)))
            print("Oscilloscope Error Status Register is: "+str(scope.query("*ESR?")))
            print(scope.query("ALLEV?"))
            
        # Create the file on the local PC, here it is a folder on "C:" called test.
        fid=open("C:\\test\\MyScreenFrame"+strnumber+".png", 'wb')
        # The command below actually moves the data from the buffer to the PC
        fid.write(raw_data)
        #close the file
        fid.close()
        # Figure out how long the screen shot took to transfer
        endtime=time.time()-start_time
        print(str(endtime), " seconds")
        Totaltime = endtime + Totaltime
        #Delete files from local disk as it has been saved.
        scope.write('FILESYSTEM:DELETE "C:\\MyScreenFrame'+strnumber+'.png"')
    # Print out to the console what the seconds were total nad average.    
    print(str(Totaltime)," seconds total.")
    print(str(Totaltime/(i+1)), " seconds average.")


Clear_Scope_Error_Register()

# default setup of the oscillosscope
scope.write("*RST")
# OPC query to wait for reset to finish
scope.query("*OPC?")

"""#################INITIALIZE Oscilloscope#################"""

# Turn on needed channels
print("Turning on channels")
scope.write("DISplay:WAVEView1:CH1:STATE 1")

#Autoset the channel and wait to complete
scope.write("AUTOSet EXECute")
scope.query("*OPC?")

# Set up the oscilloscope so that it will be in single trigger mode, and send command to invert saved screen shots
scope.write("ACQUIRE:STOPAFTER SEQUENCE")
scope.write('SAVe:IMAGe:COMPosition INVErted')
scope.write("TRIGger:A:MODe NORMal")


print("How many pictures do you want to save?")

runtimes = int(input('>'))

Transfer_picture(runtimes)
Clear_Scope_Error_Register()

#Clean up the Visa
scope.close()
