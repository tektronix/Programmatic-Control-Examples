# DPO2K Get Waveform Example
Original Attribution: Jeffrey M - Tektronix Applications

This code pulls a single, completed acquisition off of an MSO/DPO2000/B and plots it. It is adapted from existing DPO scripts on this forum. The DPO2k CURVe? query has some particular quirks that warrant a separate solution. These commands are fully explained in the programmer's manual (especially Appendix B), but the commands DATa:COMPosition SINGULAR_YT and DATa:RESOlution FULL are necessary to produce a standard CURVe? response.

Resources
---------
Original Discussion:
https://forum.tek.com/viewtopic.php?f=580&t=139853
