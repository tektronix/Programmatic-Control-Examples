import visa

#open scope
rm = visa.ResourceManager()
scope = rm.open_resource(<visa resource string>)
print(scope.query('*idn?'))
scope.timeout = 10000

scope.write('*rst') # reset
scope.query('*opc?') # sync
scope.write('autoset EXECUTE') # autoset
scope.query('*opc?') # sync

frameSize = scope.query('horizontal:acqlength?') #get frame length
numFrames = 10
scope.write('horizontal:fastframe:count {}'.format(numFrames)) #set number of frames
scope.write('horizontal:fastframe:state 1') #turn on fast frame

#acquire a set of frames and then stop acquiring
scope.write('acquire:state 0')
scope.write('acquire:stopafter SEQUENCE')
scope.write('acquire:state 1')
scope.query('*opc?')

scope.write('save:waveform:fileformat SPREADSHEETCsv') #set format before data start/stop
scope.write('save:waveform:data:start 1') #ensure data range is good
scope.write('save:waveform:data:stop {}'.format(frameSize)) #ensure data range is good

for i in range(1, numFrames+1):
    scope.write('data:framestart {}'.format(i)) #controls starting frame
    scope.write('data:framestop {}'.format(i)) #controls ending frame
    filename = r'C:\<filelocation>\frame{}.csv'.format(i)
    scope.write('save:waveform CH1,"{}"'.format(filename))
    scope.query('*opc?') 

