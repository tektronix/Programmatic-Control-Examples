% do .mdd driver creation and add to working path
makemid('tktds1k2k','C:\Program Files (x86)\IVI\Drivers\tktds1k2k\tktds1k2k.c')
addpath('C:\Program Files (x86)\IVI\Drivers\tktds1k2k')

% Create a device object. 
deviceObj = icdevice('tktds1k2k.mdd', 'USB0::0x0699::0x0368::QU100034::INSTR');

% Connect device object to hardware.
connect(deviceObj);

%%%% Execute device object function(s).%%%%
% Acquire waveform
groupObj = get(deviceObj, 'Waveformacquisitionlowlevelacquisition');
invoke(groupObj, 'initiateacquisition');

% Transfer waveform
groupObj = get(deviceObj, 'Waveformacquisition');
waveform = invoke(groupObj, 'readwaveform', 'ch1', 2500, 10000, zeros(1, 2500));

% Use waveform
plot(waveform)