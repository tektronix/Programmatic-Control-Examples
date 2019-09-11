# -*- coding: utf-8 -*-
"""
Alex Krauska, Tektronix, Beaverton
Outside of running this program the VNA needs to be calibrated, 
preferably at the maximum number of points(1001).
The VNA also has to be set for Fast Sweep Mode, Display Updates on, Correction On.
The point is to run with conditions actual customers would use to produce results.
I use One Display channel on, with S11 Magnitude.
Apply a full 2 port SOLT correction (excluding isolation).
I added Data transfers
Added data conversion
"""

import numpy as np
import visa
import time

trys=10
point_list=(51,201)
#point_list=(51,1001)
bw_list=(300,500,1000,3000,10000,50000,70000,100000,500000)
#bw_list=(10000,50000)
data=np.zeros(shape=(np.max(point_list)+10,trys),dtype=np.complex)
#point_list=(51,201)
#bw_list=(1000,300000)
#Set the following parameter true for slow sweeps
Slow_test=False
Slow_speed=1.0  #If we are peforming slow sweeps this is the time period(sec)
rm=visa.ResourceManager()
vna=rm.open_resource('GPIB8::1::INSTR',query_delay=0, timeout=5000000)
#GPIB8::1::INSTR  is the TTR506 address'
#'USBInstrument1' is the address for the E5063A
#'USB0::0x0957::0x1709::MY54100859::0::INSTR'
#'USB0::0x2A8D::0x5D01::MY54100890::0::INSTR'
# run just an OPC to make sure all prior pending operations are complete.
ready=vna.query('*OPC?')
idn = vna.query('*IDN?')
fields = idn.split(',')
company = fields[1]
model = fields[0]
serialNumber = fields[2]
swVersion = fields[3]
vna.write(':DISPlay:ENABle OFF')
vna.write(':SENSE:CORR:STAT ON')
Disp_Upd=int(vna.query(':DISPlay:ENABle?'))
Corr_En=int(vna.query(':SENS:CORR:STAT?'))
print ('{0} , {1} , {2} , {3} '.format(company,model,serialNumber,swVersion))
print('start (MHz):, end (MHz):, npts:, IFbw (kHz):,  Display Update:, Correction:, Expected Sweep Rate (sec/sweep), Actual Sweep Rate (sec/sweep), Actual Point Rate (sec/point), Group Time (sec), Group Size')
for N_pts in point_list:
    vna.write(':SENSE:SWE:POIN {0};'.format(N_pts))
    for bw in bw_list:
        vna.write(':SENSe:BAND:RESolution {0};'.format(bw))
        Fstart=float(vna.query(':SENSE:FREQUENCY:START?'))
        Fend=float(vna.query(':SENSE:FREQUENCY:STOP?'))
        Npts=int(vna.query(':SENSE:SWE:POIN?'))
        IFbw=float(vna.query(':SENSe:BAND:RESolution?'))
        VNA_Sweep_time=float(vna.query(':SENSe:SWEep:TIME:DATA?'))
# next four commands force a really slow 10 second sweep time
# to validate triggering that we can observe. 
        if Slow_test==True:
            #print('This is a controlled sweep test of {0} seconds per sweep'.format(Slow_speed))
            vna.write(':SENSe:SWEep:TIME:DATA {0};'.format(Slow_speed))
            vna.write(':SENSe:SWEep:TIME:AUTO OFF;')
        else:
            vna.write(':SENSe:SWEep:TIME:AUTO ON;')
        vna.write(':INIT1:CONT OFF;')
        vna.write(':TRIG:SOUR BUS;')
        ready=vna.query('*OPC?')
#for Python 2.7: start_time=time.clock()
        start_time=time.perf_counter()
        for count in range(trys):
    #print(' trying #{0} of {1}'.format(count,trys))
            vna.write(':INIT:IMM;')
            vna.write(':TRIG:SEQ:SING;')
            ready=vna.query('*OPC?')
            #E5063 returns +1\n, TTR506 returns 1
#for Python 2.7: end_time=time.clock()
            #ready=vna.query('*OPC?')
            #
            textdata =vna.query('CALC1:DATA:SDAT?')
            values=textdata.split(',')
            for idx in range(len(values) //2):
                data[idx,count]=float(values[2*idx])+1j*float(values[2*idx+1])
            #print('Npts ={0}, Data chars={1}, Data values{2}'.format(Npts, len(textdata),len(values)))
        end_time=time.perf_counter()
        if float(ready)==1.:
            Group_time=(end_time-start_time)
            Sweep_rate=Group_time/trys
            print('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}'.format( Fstart/1e6,Fend/1e6, Npts, IFbw/1e3, Disp_Upd, Corr_En,VNA_Sweep_time,Sweep_rate,Sweep_rate/Npts,Group_time,trys )) 
        else:
            print('VNA was not ready at end of run')
#end=time.clock()
#times[count]=end-start
vna.close()
