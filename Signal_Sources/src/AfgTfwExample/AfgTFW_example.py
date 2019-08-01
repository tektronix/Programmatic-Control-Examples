#-------------------------------------------------------------------------------
# Name:        AFG3000C - Passing a Waveform File into Internal Memory
# Purpose: This code is an example of how to send a AFG TFW file to editable memory on a AFG3000 generator
#
# Created using Python version 2.7
# Using Tekvisa v1.8
# Using Windows 7, Tekvisa version v4.1.0 or newer
# Created:     5/10/2016
# Copyright:   (c) Tektronix 2016
#-------------------------------------------------------------------------------

import visa, time, logging, os, struct, sys


#using PYVISA we can setup the AFG3000 to be configured over USB in this example
rm = visa.ResourceManager()
rm.list_resources()

instrumentdescriptor = 'USB::0x0699::0x0345::CU000001::INSTR' #example of your USB connected device
AFG3000 = rm.open_resource(instrumentdescriptor)

ID = AFG3000.ask('*IDN?')
print ID

AFG3000.write('*RST') #reset AFG

#Filename for TFW to be read in from the PC
filelocation = '"AFGWaveformfile.tfw"'
wfm_magic_name = "TEKAFG3000"
wfm_version_check = '20050114'


#This section is where we open the TFW file as a binary file for python
with open('AFGWaveformfile.tfw', 'rb') as f:

    file_size = f.seek(0,2) #size of file
    f.seek(0,0)

    #the header for TFW files is 512 bytes. So we'll read the sub sections to validate the waveform and get the file size
    header = f.read(512)

    #the first section is the 'magic section'
    binary_magic = header[:16]
    magic = struct.unpack( '16c', binary_magic)
    magic = ''.join(magic)
    print 'The Magic: ', magic

    #lets do a quick check to make sure the beginning of the TFW file is correct, more checks can be performed if needed
    #on version, thumbnail or comparing the size is correct.
    if magic[:10] == wfm_magic_name:
        print 'Checked 1: This is a valid AFG TFW file'
    else:
        print 'Checked 1: This is not a valid AFG TFW file'
        sys.exit()

    #This next section is the version information about the AFG3000. It should read back 20050114
    binary_version = header[16:16+4]
    version = struct.unpack('>i', binary_version)
    version = version[0]
    print 'Version: ',version

    #This next section is the length of the data, also called 'points'.
    binary_points = header[20:20+4]
    points = struct.unpack('>i', binary_points)
    points = points[0]
    print 'Data is length: ',points


    waveform_data = f.read()
    binwavefrom = struct.unpack('>'+str(points)+'H', waveform_data)


    #check data length to point size.
    if len(waveform_data) == points*2:  #make sure the points*2 bytes is what you compare s
        print 'Checked 2: This wfm data is a valid AFG TFW file'
    else:
        print 'Checked 2: This wfm data is not a valid AFG TFW file'
        sys.exit()



    #We can write the waveform data to the AFG after making sure its in big endian format
    AFG3000.write_binary_values('TRACE:DATA EMEMory,', binwavefrom, datatype='h', is_big_endian=True)


    #'copies' the Editable Memory to User1 memory location. note: there are 4 user memory locations
    AFG3000.write('data:copy user1, ememory')



    #setup output1
    AFG3000.write('source1:function user1') #sets the AFG source to user1 memory
    AFG3000.write('source1:Frequency 20E3') #set frequency to 20KHz
    AFG3000.write('source1:voltage:amplitude 2') #sets voltage of CH1 to 2 Volts
    AFG3000.write('output1:state ON') #turns on output 1


    #setup output2
    AFG3000.write('source2:function user1') #sets the AFG source to user1 memory
    AFG3000.write('source2:Frequency 20E3') #set frequency to 20KHz
    AFG3000.write('source2:voltage:amplitude 2') #sets voltage of CH1 to 2 Volts
    AFG3000.write('output2:state ON') #turns on output 2


