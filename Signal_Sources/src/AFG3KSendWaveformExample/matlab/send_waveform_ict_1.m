%% AFG3000 MATLAB ICT Send Waveform 1
% Date: 11-18-2008
% ==================
% Send 14 bit waveform data to an AFG3000.
% 
% PREREQUISITE EXAMPLES
% ==================
% MATLAB ICT Control 1 (Hello World)
% ==================
%
% COMPATIBILITY
% ==================
% AFG3000, AFG3000B
% ==================
%
% TESTED & DEVELOPED
% ==================
% Microsoft Windows XP SP2
% TekVISA 3.3.2.7
% MATLAB Version 7.6.0.324 (R2008a)
% Instrument Control Toolbox Version 2.6
% GPIB: National Instruments PCMCIA-GPIB (ni488k.sys v2.6.0f0)
% AFG3252 FW 3.0.1
% ==================
%
% Tektronix provides the following example "AS IS" without any guarantees
% or support.  This example is for instructional guidance only.
 
%% variables
visa_vendor = 'tek';
visa_address = 'GPIB0::3::INSTR';
% example waveform: sine wave using 12 sample points, integers between 0 to
% 16382 (range of AFG).  hex notation is easier to verify later
% (note: max value of afg3000 is '3FFE' not '3FFF')
wave = {'2000' '2FFF' '3BB6' '3FFE' '3BB6' '2FFF' '2000' '1000' '0449' ...
    '0000' '0449' '1000'};
wave = hex2dec(wave);
 
%% pre-processing
% encode variable 'wave' into binary waveform data for AFG.  This is 
% the same as AWG5000B but marker bits are ignored.  see AWG5000B series 
% programmer manual for bit definitions.
binblock = zeros(2 * length(wave), 1);
binblock(2:2:end) = bitand(wave, 255);
binblock(1:2:end) = bitshift(wave, -8);
binblock = binblock';
 
% build binary block header
bytes = num2str(length(binblock));
header = ['#' num2str(length(bytes)) bytes];
 
%% instrument communication
afg = visa(visa_vendor, visa_address);
fopen(afg);
fwrite(afg, '*rst;');
fwrite(afg, '*cls;');
 
% clear edit memory and set to 12 samples
fwrite(afg, ':trace:define ememory, 12;');
 
% send the data to edit memory
fwrite(afg, [':trace ememory,' header binblock ';'], 'uint8');
 
% set channel 1 to arb function found in edit memory
fwrite(afg, ':source1:function ememory;');
 
% turn on channel 1
fwrite(afg, ':output1 on;');
 
% gracefully disconnect
fclose(afg);
delete(afg);
clear afg;

