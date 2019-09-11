# TTR500 VNA Sweep Speed Calculator 2.0
Original Attribution: Alex Krauska - Tektronix 

This example will calculate a number of parameters for TTR500, including start/end frequency, number of points, IF bandwidth, Display update rate, Expected sweep rate, Actual sweep rate, Actual point rate, Group time and Group size.  

### Instrument settings
Outside of running this program the VNA needs to be calibrated, preferably at the maximum number of points(1001).  
The VNA also has to be set for Fast Sweep Mode, Display Updates on, Correction On.  
The point is to run with conditions actual customers would use to produce results.  
I use One Display channel on, with S11 Magnitude.  
Apply a full 2 port SOLT correction (excluding isolation).  
