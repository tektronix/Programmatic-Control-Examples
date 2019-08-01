# Curve Stream Example
Original attribution: Dave W. - Tektronix Applications

This example shows how to use the Curve Streaming feature of MSO/DPO5000/B, DPO7000/C, DSA70000/B/C/D, and MSO70000/C/DX, DPO70000/B/C/D/DX /SX Series Digital Oscilloscopes to stream curves from the oscilloscope to the hard drive in .CSV files. This example works with record length of any size supported by the scope. However, for recorded lengths approaching 1 million points or larger it is highly recommend that you modify the code to save the binary data directly to disk rather than convert it to .CSV as performance will become very slow due to the conversion time required to convert floating point numbers to text strings.

Resources
---------
Original Discussion:
https://forum.tek.com/viewtopic.php?f=580&t=138342
