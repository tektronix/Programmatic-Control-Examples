#-------------------------------------------------------------------------------
# Author:      cball
#
# Created:     09/08/2017
# PyVisa 1.8,
# Python 2.7.5
#-------------------------------------------------------------------------------
import visa
  
instrument_id = "TCPIP::10.0.0.6::INSTR" #replace with your instrument identifier

#Connect to scope and print ID
rm = visa.ResourceManager()
rm.list_resources()
scope = rm.open_resource(instrument_id)
print scope.ask('*IDN?')

#Save image on scope harddrive
scope.write('SAVE:IMAGE \'c:/TEMP.PNG\'')
scope.ask("*OPC?")  #Make sure the image has been saved before trying to read the file

#Read file data over
scope.write('FILESYSTEM:READFILE \'c:/TEMP.PNG\'')
data = scope.read_raw()

#Save file to local PC
fid = open('my_image.png', 'wb')
fid.write(data)
fid.close()
