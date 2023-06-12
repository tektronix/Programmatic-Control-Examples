# Save on Trigger Example
Original attribution: Chris B - Tektronix Applications

As a recent learning project, I have written a Save on Trigger program that is compatible with Tektronix TDS2000B/C, TDS3000B/C, DPO/MSO2000/3000/4000 series scopes. Data is saved as Image files, or .CSV waveform files (viewable in Wavestar) directly to the PC running the Save on trigger application. This has been written with Python 2.7, and uses PyVISA 1.3. Due to complications with PyVISA not properly releasing my COM ports when a program completes (or crashes), I have decided to only code support for Ethernet, USB or GPIB connections.

Currently there are two parts of this program. SaveonTrig.py is the launcher, and used to loop the main program, as well as trap errors that would cause the program crash (typically issues with the VISAs resource list). SoTmain.py contains all the code that handles setting up the scope, capturing the selected data types and saving a log of the session.

<!-- markdown-link-check-disable -->
Resources
--------
Original Discussion:
https://forum.tek.com/viewtopic.php?f=580&t=136170
