# demo: creating WFMX files
# for Tektronix AWG70000 and AWG5200 series
# and SourceXpress software

# WFMX structure
# XML header (required)
# single precision vector 1 (required)
# single precision vector 2 (optional)
# unsigned 8-bit integer marker vector (optional)

# marker encoding
# marker 1 = bit 0
# marker 2 = bit 1
# marker 3 = bit 2
# marker 4 = bit 3

import xml.etree.ElementTree as ET
import datetime
import numpy as np # http://www.numpy.org/

# example vectors
idle_wfm = np.zeros(2400, dtype=np.single)
s = np.arange(5000, dtype=np.single)
inphase = np.sin(2 * np.pi * s / 5000 * 8)
quadrature = np.cos(2 * np.pi * s / 5000 * 8)
m1 = np.array([1, 1, 1, 1, 0, 0, 0, 0], dtype=np.uint8)
m1 = np.tile(m1, 625)
m2 = np.roll(m1, 1)
m3 = np.roll(m1, 2)
m4 = np.roll(m1, 3)

# create XML header
# require structure for WFMX header
df = ET.Element('DataFile')
dsc = ET.SubElement(df, 'DataSetsCollection')
dss = ET.SubElement(dsc, 'DataSets')
dss.attrib = {'version': '1'}
dd = ET.SubElement(dss, 'DataDescription')
ns = ET.SubElement(dd, 'NumberSamples')
ns.text = '2400'
su = ET.SubElement(df, 'Setup')

# optional parts of WFMX header
mi = ET.SubElement(dd, 'MarkersIncluded') # optional, default 'false'
mi.text = 'false' # has marker vector
ts = ET.SubElement(dd, 'Timestamp')
ts.text = datetime.datetime.now().isoformat()
ps = ET.SubElement(dss, 'ProductSpecific') # optional 
sf = ET.SubElement(ps, 'SignalFormat') # optional, default 'real'
sf.text = 'Real' # 'IQ' for complex
rsr = ET.SubElement(ps, 'RecSamplingRate') # optional
rsr.attrib = {'units': 'Hz'}
rsr.text = '1230400000'
ra = ET.SubElement(ps, 'RecAmplitude') # optional
ra.attrib = {'units': 'Volts'}
ra.text = '0.487'
ro = ET.SubElement(ps, 'RecOffset') # optional
ro.attrib = {'units': 'Volts'}
ro.text = '0.123'

# write an idle waveform
with open('my idle waveform.wfmx', 'wb') as f:
    f.write(ET.tostring(df)) # write xml header
    f.write(idle_wfm.tobytes()) # write vector 1 bytes

# write a complex waveform
# update xml header for complex format
ns.text = '5000'
sf.text = 'IQ'
with open('my complex waveform.wfmx', 'wb') as f:
    f.write(ET.tostring(df)) # write xml header
    f.write(memoryview(inphase)) # write vector 1 bytes
    f.write(memoryview(quadrature)) # write vector 2 bytes

# write waveform with a marker vector
# pack markers
mAll = ((m1 & 0b1) << 0) + ((m2 & 0b1) << 1) + ((m3 & 0b1) << 2) + ((m4 & 0b1) << 3)
# update header with new infos
mi.text = 'true'
sf.text = 'Real'
with open('my sine with markers.wfmx', 'wb') as f:
    f.write(ET.tostring(df)) # write xml header
    f.write(memoryview(inphase)) # write vector 1 bytes
    f.write(memoryview(mAll)) # write marker vector

# write a complex with markers
sf.text = 'IQ'
with open('my complex with markers.wfmx', 'wb') as f:
    f.write(ET.tostring(df)) # write xml header
    f.write(memoryview(inphase)) # write vector 1 bytes
    f.write(memoryview(quadrature)) # write vector 2 bytes
    f.write(memoryview(mAll)) # write marker vector

