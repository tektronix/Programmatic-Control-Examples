# demo: creating SEQX files
# for Tektronix AWG70000A and AWG5200 series

# SEQX structure
# a zip file, compression optional
# folder, Sequence, SML files (minamum 1 file)
# folder, Waveforms, WFMX files (optional) 

# SML file: an XML file that contains seqence data

# demo seqence
# idle waveform, repeat inf, TrigA: goto 2
# positive pulse, once, goto 3
# idle waveform, repeat inf, TrigA: goto 3
# negative pulse, once, goto 1

import zipfile
import xml.etree.ElementTree as ET
import numpy as np # http://www.numpy.org/

# make waveforms for demo sequence
# see https://forum.tek.com/viewtopic.php?t=140605
idle_wfm = np.zeros(2400, dtype=np.single)
pos_pulse = idle_wfm
pos_pulse[0:10] = 1
neg_pulse = idle_wfm
neg_pulse[0:10] = -1
df = ET.Element('DataFile')
dsc = ET.SubElement(df, 'DataSetsCollection')
dss = ET.SubElement(dsc, 'DataSets')
dss.attrib = {'version': '1'}
dd = ET.SubElement(dss, 'DataDescription')
ET.SubElement(dd, 'NumberSamples').text = '2400'
su = ET.SubElement(df, 'Setup')
with open(r'C:\temp\idle.wfmx', 'wb') as f:
    f.write(ET.tostring(df))
    m = memoryview(idle_wfm)
    f.write(m)
with open(r'C:\temp\pos_pulse.wfmx', 'wb') as f:
    f.write(ET.tostring(df))
    m = memoryview(pos_pulse)
    f.write(m)
with open(r'C:\temp\neg_pulse.wfmx', 'wb') as f:
    f.write(ET.tostring(df))
    m = memoryview(neg_pulse)
    f.write(m)


# sml file
df = ET.Element('DataFile')
df.attrib = {'offset': '000000000', 'version': '0.1'}
dsc = ET.SubElement(df, 'DataSetsCollection')
dss = ET.SubElement(dsc, 'DataSets')
dss.attrib = {'version': '1'}
dd = ET.SubElement(dss, 'DataDescription')
ET.SubElement(dd, 'SequenceName').text = 'demo sequence'
ET.SubElement(dd, 'RecSampleRate').text = '10000000000'
steps = ET.SubElement(dd, 'Steps')
steps.attrib = {'StepCount': '4', 'TrackCount': '1'}

s = ET.SubElement(steps, 'Step')
ET.SubElement(s, 'StepNumber').text = '1'
ET.SubElement(s, 'Repeat').text = 'Infinite'
ET.SubElement(s, 'EventJumpInput').text = 'TrigA'
assets = ET.SubElement(s, 'Assets')
a = ET.SubElement(assets, 'Asset')
ET.SubElement(a, 'AssetName').text = 'idle' # name of WFMX file w/o extention
ET.SubElement(a, 'AssetType').text = 'Waveform'

s = ET.SubElement(steps, 'Step')
ET.SubElement(s, 'StepNumber').text = '2'
assets = ET.SubElement(s, 'Assets')
a = ET.SubElement(assets, 'Asset')
ET.SubElement(a, 'AssetName').text = 'pos_pulse' 
ET.SubElement(a, 'AssetType').text = 'Waveform'

s = ET.SubElement(steps, 'Step')
ET.SubElement(s, 'StepNumber').text = '3'
ET.SubElement(s, 'Repeat').text = 'Infinite'
ET.SubElement(s, 'EventJumpInput').text = 'TrigA'
assets = ET.SubElement(s, 'Assets')
a = ET.SubElement(assets, 'Asset')
ET.SubElement(a, 'AssetName').text = 'idle' 
ET.SubElement(a, 'AssetType').text = 'Waveform'

s = ET.SubElement(steps, 'Step')
ET.SubElement(s, 'StepNumber').text = '4'
ET.SubElement(s, 'GoTo').text = 'First'
assets = ET.SubElement(s, 'Assets')
a = ET.SubElement(assets, 'Asset')
ET.SubElement(a, 'AssetName').text = 'neg_pulse' 
ET.SubElement(a, 'AssetType').text = 'Waveform'

su = ET.SubElement(df, 'Setup')

# update size
actual_size = len(ET.tostring(df))
if actual_size > 999999999:
    raise Exception("sequence files cannot exceed 999,999,999 bytes")
df.attrib['offset'] = '{:09d}'.format(actual_size)

# write to file
with zipfile.ZipFile(r'C:\temp\my_seq.seqx', mode='w') as zo:
    zo.writestr('Sequences/main.sml', ET.tostring(df))
    zo.write(r'C:\temp\idle.wfmx', 'Waveforms/idle.wfmx')
    zo.write(r'C:\temp\pos_pulse.wfmx', 'Waveforms/pos_pulse.wfmx')
    zo.write(r'C:\temp\neg_pulse.wfmx', 'Waveforms/neg_pulse.wfmx')
    
