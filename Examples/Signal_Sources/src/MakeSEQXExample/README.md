# Make SEQX Example (ElementTree API)
Original Attribution: Carl M - Tektronix Applications

The Tektronix SEQX is a zip archive that contains 1 or more sequences (SML files) and optionally WFMX waveforms. This is intended to provide all channel assets (waveforms/sequences) defining a signal into a single file. SML files are an XML file that describes a sequence. Referenced assets are automatically loaded if available. Assets missing from the SEQX file will be replaced with assets currently loaded (from waveform list or sequence list). Assets missing from both will be reassigned to Empty. While you can pack many waveforms and sequences into a single SEQX file, a healthy habit is to only build SEQX files with one primary SML file and include only referenced assets.

Python has built-in tools for XML files and ZIP archives:
* https://docs.python.org/3/library/xml.html
* https://docs.python.org/3/library/zipfile.html
This example demonstrates of the ElementTree API and zipfile module to create a functioning SEXQ file. Numpy is used for creation of simplistic example vectors.

See also: [Make WFMX (ElementTree API)](./../MakeWFMXExample)
<!-- markdown-link-check-disable -->
Resources
---------
Original Discussion: https://forum.tek.com/viewtopic.php?t=140633
