# Curve Stream Example
Original attribution: Dave W. - Tektronix Applications

This example shows how to use the Curve Streaming feature of MSO/DPO5000/B, DPO7000/C, DSA70000/B/C/D, and MSO70000/C/DX, DPO70000/B/C/D/DX /SX Series Digital Oscilloscopes to stream curves from the oscilloscope to the hard drive in text (.csv) or binary (.dat) files. This example works with record length of any size supported by the scope. However, for recorded lengths approaching 1 million points or larger it is highly recommend that you save the data in binary (.dat) format rather than text (.csv) as performance will become very slow due to the conversion time required to convert floating point numbers to text strings.

Resources
---------
Original Discussion:
https://forum.tek.com/viewtopic.php?f=580&t=138342


One Example, Two Versions
-------------------------
Within this directory you will find two versions of the example.
* *CurvestreamExample-NI-VISA*
  * Contains the original example as posted on the Tektronix forums.
  * This version is deprecated and kept only for reference.  Please use the IVI-VISA.NET</nolink> version.
* *CurvestreamExample-IVI-VISA<nolink/>.NET*
  * An updated version of the example that uses the IVI standard VISA<nolink/>.NET library.

Since the time when the Curvestream Example was originally created, NI has deprecated the NI VisaNS library and recommends using the IVI standard VISA<nolink/>.NET library.  For users of this example program, use of the VISA<nolink/>.NET version of the example is recommended.
