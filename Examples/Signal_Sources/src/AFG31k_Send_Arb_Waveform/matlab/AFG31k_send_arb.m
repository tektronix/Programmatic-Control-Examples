% AFG31000 MATLAB ICT Send Waveform 1
%{ 

The data following the binary block header is unsigned 16-bit integer 
values, most significant byte first (big-endian). Bits 15 and 16 are 
ignored as the AFG has 14-bits of dynamic range. The key concept is the 
digital values are unit-less. Value 0 is the minimum output and value 16382 
is the maximum output. Amplitude (and offset, and timing) are applied at 
run-time based on the AFG settings.

MATLAB R2018b
Instrument Control Toolbox v3.14 
NI-VISA v19.5
AFG31000

	***********************************************************
    *** Copyright 2023 Tektronix, Inc.                      ***
    *** See www.tek.com/sample-license for licensing terms. ***
    ***********************************************************
	
Tektronix provides the following example "AS IS" without any guarantees
or support.  This example is for instructional guidance only.
%}

% constants
visa_vendor = 'ni';
visa_descriptor = 'USB0::0x0699::0x035A::QU000025::INSTR';
record_length = 131072; % max number of sample points 2^17 allowed in EMEM
buffer = 2 * record_length + 20; % allot for header information
% calculations

% dampened oscillation waveform
sample = 0:(record_length - 1);
vector = sin(40 * pi * sample / length(sample)).*exp(-4*sample/length(sample));

% normalize to dac values
m = 16382 / (max(vector) - min(vector));
b = -m * min(vector);
dac_values = uint16(m * vector + b);
dac_bytes = typecast(swapbytes(dac_values), 'uint8');

% binary-block header
bbh = sprintf('%u', length(dac_bytes)) ;
bbh = sprintf('#%u%s', length(bbh), bbh);

% instrument communication
afg = visa(visa_vendor, visa_descriptor, 'InputBuffer', buffer, ...
    'OutputBuffer', buffer);
fopen(afg);
fprintf('connected to...\n')
r = query(afg, '*idn?');
fprintf(r);
fprintf('\n')

fprintf('clearing event status register & flushing messages\n')
fwrite(afg, '*cls');
r = query(afg, '*esr?');
fprintf(' esr value: %s', r);
r = query(afg, 'system:error?');
fprintf(' msg: %s', r);
fprintf('\n')

fwrite(afg, cmd);
r = query(afg, '*esr?');
fprintf(' esr value: %s', r);
r = query(afg, 'system:error?');
fprintf(' msg: %s', r);
fprintf('\n')

cmd = ['data EMEM1,' bbh dac_bytes];    % Change to EMEM2 for channel 2 arb

%%% Only for displaying 2-Byte values
% fprintf('writing bytes (hex)...\n');
% for r = 1:length(cmd)
%     fprintf('%02X ', cmd(r));
%     if (mod(r,16) == 0)
%         fprintf('\n')
%     end
% end
fprintf('\n')
fwrite(afg, cmd);
r = query(afg, '*esr?');
fprintf(' esr value: %s', r);
r = query(afg, 'system:error?');
fprintf(' msg: %s', r);
fprintf('\n')


%  writes sample waveform to tfwx file
fwrite(afg,'MMEMory:STORe:TRACe EMEMory1,"M:/decay_sample.tfwx"');
%  imports the newly created sample waveform into waveform list
fwrite(afg,'WLISt:WAVeform:IMPort "M:/decay_sample.tfwx"');
%  adds the sample waveform to the sequence list
fwrite(afg,'SEQuence:ELEM1:WAVeform1 "M:/decay_sample.tfwx"');

fprintf('disconnecting...\n\n')
fclose(afg);
delete(afg);

fprintf('done\n')