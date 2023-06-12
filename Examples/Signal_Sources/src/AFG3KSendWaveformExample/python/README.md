# afg3k afg2k send wfm
Original Attribution: Carl M - Tektronix Applications

A port of the MATLAB example [AFG3000 MATLAB ICT Send Waveform 1](./../matlab/)
should work in python 2 as well

Example shell output:
```
digital sample values...
 0x1fff
 0x2ffe
 0x3bb5
 0x3ffe
 0x3bb5
 0x2ffe
 0x1fff
 0x1000
 0x0449
 0x0000
 0x0449
 0x0fff
connected to...
TEKTRONIX,AFG2021,C010334,SCPI:99.0 FV:1.1.9
clearing event status register & flushing messages
 esr value: 0b00000000
 msg: 0,"No error"
writing: "data:define EMEM,12"
 esr value: 0b00000000
 msg: 0,"No error"
 esr value: 0b00000000
 msg: 0,"No error"
disconnecting...
done
```
<!-- markdown-link-check-disable -->
NI IO Trace and AFG2021 display verification:
![AFG](https://forum.tek.com/download/file.php?id=24724)


Resources
---------
Original Discussion:
https://forum.tek.com/viewtopic.php?f=580&t=139206
