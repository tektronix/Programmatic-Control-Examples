# DPO70000SX Ultrasync Time-Sync Mode Control Example
This example demonstrates programatic control of a 4-stack of DPO70000SX instruments configured in the Ultrasync Time-Sync mode.  In this mode you can acquire on up to 16 time-synchronized channels, simultaneously.

This Example demonstrates:
* 

Original Author: Dave W. - Tektronix Applications

## Development Environment:
Python 3.11, PyVisa 1.14, NI-VISA 2023 Q4, Windows 10

## Compatible Instruments:
Script is designed for use with TekConnect Models of DPO70000SX Series Oscilloscopes (DPO73304SX and below).</br>
It can be used with ATI Models of DPO70000SX Series Oscilloscopes (DPO75002SX and above) with some modification.  (Comment out lines that access CH2 and CH4.)

## Compatible Interfaces:
* USB
* Ethernet

## Changelog:
### 2024-02-22:
Original Revision


<!-- markdown-link-check-disable -->
Resources
---------
* DPO70000SX Series Programmer's Manual: https://www.tek.com/en/oscilloscope/dpo70000-mso70000-manual/dpo70000sx-mso-dpo70000dx-mso-dpo70000c-dpo7000c-mso5000-b-1
* Python: https://www.python.org/
* PyVISA: https://pyvisa.readthedocs.io
* NI-VISA: https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html
