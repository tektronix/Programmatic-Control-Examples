# AFG3000 MATLAB ICT Send Waveform 1
Original Attribution: Carl M - Tektronix Applications

Use the table view of the samples on the instrument to verify the individual samples.

Example MATLAB Command Window output:
```
>> AFG3000_MATLAB_ICT_Send_Waveform_1
connected to...
TEKTRONIX,AFG2021,C010334,SCPI:99.0 FV:1.1.9

clearing event status register & flushing messages
 esr value: 0
 msg: 0,"No error"

writing: "data:define EMEM,12"
 esr value: 0
 msg: 0,"No error"

writing bytes (hex)...
64 61 74 61 20 45 4D 45 4D 2C 23 32 32 34 1F FF 
2F FF 3B B5 3F FE 3B B5 2F FF 1F FF 10 00 04 49 
00 00 04 49 0F FF 
 esr value: 0
 msg: 0,"No error"

disconnecting...

done
```

NI IO Trace correlation to AFG2021 display:
![afg2k_trace_data](https://forum.tek.com/download/file.php?id=24723)

Resources
---------
Original Discussion:
https://forum.tek.com/viewtopic.php?f=569&t=133567#p282128
