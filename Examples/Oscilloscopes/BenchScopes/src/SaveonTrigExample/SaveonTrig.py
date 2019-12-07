"""
Launch program for main SaveonTrig script

This module is used to loop the SoTmain application
when desired and provide more information
about how to use the program.  Built using
python 2.7 (http://www.python.org/)
pyvisa 1.3 (http://pypi.python.org/pypi/PyVISA/1.3)
"""
import SoTmain

print "Welcome to the save on Trigger Data Logging Application"
print "This program is compatible with TDS2000B/C, TDS3000B/C" 
print "and DPO2000/3000/4000 series Oscilloscopes with a TCPIP" 
print "or USB connection. NI-VISA or TekVISA must be installed. \n"
while True:
    try:
        SoTmain.main()
    except:
        print "An unexpected error occured"
    print "\n\nWould you like to start another capture" \
          + " session? (Y/N)"
    Doagain = str(raw_input(""))
    if ('Y' not in Doagain) and ('y' not in Doagain):
        print "Good Bye!"
        break
a = raw_input("Press ENTER to exit")
