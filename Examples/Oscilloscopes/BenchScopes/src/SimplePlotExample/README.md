# TBS Simple Plot
Original Attribution: Carl M - Tektronix Applications

Slight modification of the Python: [MDO Simple Plot](./../../../MidrangeScopes/src/SimplePlotExample) to accommodate TDS2k, TPS2k and TBS1k series oscilloscopes.

This code example provides meaningful output (i.e. a scaled waveform plot) as simply as possible without bad practices. It is useful for testing the installation and configuration of a Python environment for development of remote instrument control code. It demonstrates best practice event status checking, command synchronization, waveform acquisition, waveform data transfer, waveform scaling, and waveform plotting using Python 3.5 and PyVISA v1.8 and Matplotlib v1.5.1. Default setup and auto-set are compromises for convenience. Because the exercised features are fairly universal to Tektronix oscilloscopes, this example should work across a wide range of models without any modification.

Resources
---------
Original Discussion:
https://forum.tek.com/viewtopic.php?f=580&t=138685


