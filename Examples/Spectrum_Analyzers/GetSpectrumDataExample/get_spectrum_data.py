#RSA3000B Get Spectrum Data example
#built and tested using python 3.5.2 with an RSA3408B

import visa # http://github.com/hgrecco/pyvisa
import numpy # http://www.numpy.org/
import pylab # http://matplotlib.org/

visa_address = 'TCPIP::###.###.###.###'
#replace string with your instrument visa address; I used LAN for remote comm
rm = visa.ResourceManager()
sa = rm.open_resource(visa_address)

sa.timeout = 10000 #enough time for the scope to process some comamnds, like "inst:sel" window changes

print(sa.query('*idn?')) #check to see that we're connected to a correct, responding instrument

sa.write('*rst') #set to default
print(sa.query('*opc?'))

sa.write('inst:sel "SANORMAL"') #set to Spectrum Analyzer NORMAL display
print(sa.query('*opc?'))

sa.write('init:cont OFF') #"READ" commands capture a spectrum, so we turn acquisition off
print(sa.query('*opc?'))

myData = sa.query_binary_values('read:spectrum?', datatype='f') #without numpy

#same as...
#sa.write('read:spectrum?')
#myData = sa.read_raw()

#read_raw is due to the format of the spectrum data, described below and in the Programmer Manual
#<Num_digit><Num_byte><Data(1)><Data(2)>...<Data(n)>
#Where
#<Num_digit> is the number of digits in <Num_byte>.
#<Num_byte> is the number of bytes of the data that follow.
#<Data(n)> is the amplitude spectrum in dBm.
#4-byte little endian floating-point format specified in IEEE 488.2
#n: Max 400000 (= 800 points×500 frames)

#now do stuff with myData.

#with numpy
myData2 = sa.query_binary_values('read:spectrum?', datatype='f', container=numpy.array)

#save to CSV example using numpy.
myData2.tofile('C:\\file_location', sep='\r\n', format='%s')

#graph example using pylab and numpy.
pylab.plot(myData2)
pylab.show()
#note that horizontal values are indices, not freq. values.
#for Freq values, rescale based on Display:Spectrum: queries.


