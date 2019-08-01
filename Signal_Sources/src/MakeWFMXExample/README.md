# Make WFMX (ElementTree API)
Original Attribution: Carl M - Tektronix Applications

This is a proof-of-concept example for user created WFMX files. WFMX is the native waveform container for the Tektronix AWG70000 and AWG5200 series arbitrary waveform generators and SourceXpress arbitrary waveform generator software. The Tektronix WFMX structure is extensible but not complex. It starts with an XML header followed by binary data. Python has many built-in tools for XML processing: https://docs.python.org/3/library/xml.html This example demonstrates of the ElementTree API to create a functional WFMX XML header. [Numpy](http://www.numpy.org/) is used for creation of simplistic example vectors.

Related: [Make SEQX (ElementTree API)](./../MakeSEQXExample)

Resources
---------
Original Discussion: https://forum.tek.com/viewtopic.php?f=580&t=140605
