% VISA Control: RSA Trace Transfer
% Author: Morgan Allison
% Date Edited: 8/17
% This program transfers the Amplitude vs Time trace from the RSA to the 
% computer and plots the results. 
% Windows 7 64-bit, TekVISA 4.0.4
% Matlab r2017a with ICT
% Download SignalVu-PC programmer manual: http://www.tek.com/node/1828803
% Download RSA5100B programmer manual: 
% http://www.tek.com/spectrum-analyzer/inst5000-manual-7
% Download SignalVu programmer manual: 
% http://www.tek.com/oscilloscope/dpo70000-mso70000-manual-22
% Tested on RSA306B/RSA507A with SignalVu-PC 3.10.0030, 
% DPO77002SX with SignalVu 3.9.0051


%% #################SEARCH/CONNECT#################
visaBrand = 'tek';
% instAddress = 'TCPIP::192.168.1.10::INSTR';
instAddress = 'GPIB8::1::INSTR';
buf = 50000;
inst = visa(visaBrand, instAddress);
set(inst, 'InputBuffer', buf);
set(inst, 'OutputBuffer', buf);
fopen(inst);
inst.timeout = 15;

instID = query(inst,'*idn?');
fprintf('Connected to %s\n',instID);

if contains(instID, 'MSO') || contains(instID, 'DPO')
    % IMPORTANT: make sure SignalVu is already running if you're using a scope.
    % The application:activate command gives focus to SignalVu.
    % *OPC? does not respond to application:activate, so there's no good 
    % way to synchronize this command
    sampleRate = 50e9;

    disp('Activating SignalVu');
    fprintf(inst, 'application:activate "SignalVu Vector Signal Analysis Software"');
    fprintf(inst, 'sense:signalvu:acquisition:control:sample:rate off');
    fprintf(inst, 'sense:signalvu:acquisition:digitizer:sample:rate %d', sampleRate);
end

% preset, clear buffer, and stop acquisition
fprintf(inst, 'system:preset');
fprintf(inst, '*cls');
fprintf(inst, 'abort');


%% #################CONFIGURE INSTRUMENT#################%% 
% configure acquisition parameters
cf = 2.4453e9;
span = 40e6;
refLevel = 0;

fprintf(inst, 'spectrum:frequency:center %d', cf);
fprintf(inst, 'spectrum:frequency:span %d', span);
fprintf(inst, 'input:rlevel %d', refLevel);

fprintf(inst, 'initiate:continuous off');
fprintf(inst, 'trigger:status off');

%% #################ACQUIRE/PROCESS DATA#################%% 
% start acquisition THIS MUST BE DONE
% it is an overlapping command, so *OPC? MUST be sent for synchronization
fprintf(inst, 'initiate:immediate');
query(inst, '*opc?');

fprintf(inst, 'fetch:spectrum:trace?');
spectrum = binblockread(inst, 'float');

% generate the frequency vector for plotting
fMin = cf - span / 2;
fMax = cf + span / 2;
freq = linspace(fMin, fMax, length(spectrum));

%% #################PLOTS#################%% 
figure(1);
whitebg(1,'k');
plot((freq/1e9), spectrum, 'y')
title('Spectrum')
xlabel('Frequency (GHz)')
ylabel('Amplitude (dBm)')
xlim([fMin / 1e9, fMax / 1e9])
ylim([refLevel - 100, refLevel])

%% Close instrument
fclose(inst);
delete(inst);
clear inst;