# Max Reading Rate Example - Tek DMM4020 - Python3
Original attribution: Dave W. - Tektronix Applications

To achieve the maximum sample rate of 100 readings per second on the DMM4020 you will need to write a program or script to control the instrument and read back the data at this rate. Getting this speed is very simple requiring only the following two commands.

RATE F
PRINT 1

RATE F sets the DMM to the fast reading rate mode. PRINT 1 sets the DMM into print-only mode at the fastest rate. After sending these commands, the DMM will send back unsolicited readings on the remote interface as fast as possible. You will need your program to just read them continuously. To stop the DMM from sending readings back, send the command PRINT 0.

Note: To get the fastest reading rates you will want to set the BAUD rate of the RS-232 port to 19200 (over the default 9600). You will also want to configure the DMM to a fixed measurement range as auto-ranging will slow down the reading rate if the range needs to change between readings.

Below is a Python script that will get readings back from the DMM as fast as possible. Using this script I have been able to achieve a reading rate of over 112 readings per second.

Here is some example output from the script:
```
TEKTRONIX, DMM4020, 1028011, 2.5 D2.0
+0.5021E+0
+0.5021E+0
+0.5021E+0
+0.5021E+0
...
+0.5022E+0
+0.5022E+0
+0.5022E+0
+0.5022E+0
+0.5022E+0
Number of Readings: 500

Elapsed Time: 4.459887981414795

Readings/sec: 112.11043911497228
+0.5022E+0
+0.5021E+0
=>
```

Resources
---------
https://forum.tek.com/viewtopic.php?f=580&t=138561
