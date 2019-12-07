% VISA Control: RSA AvT Transfer
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


%% #################CONFIGURE INSTRUMENT#################
freq = 1e9;
span = 40e6;
refLevel = 0;

% set up spectrum acquisition parameters
fprintf(inst, 'spectrum:frequency:center %d', freq);
fprintf(inst, 'spectrum:frequency:span %d', span);
fprintf(inst, 'input:rlevel %d', refLevel);

% open new displays
fprintf(inst, 'display:ddemod:measview:new conste'); % constellation
fprintf(inst, 'display:ddemod:measview:new stable'); % symbol table
fprintf(inst, 'display:ddemod:measview:new evm'); % EVM vs Time

% turn off trigger and disable continuous capture (enable single shot mode)
fprintf(inst, 'trigger:status off');
fprintf(inst, 'initiate:continuous off');

% configure digital demodulation (QPSK, 1 MSym/s, RRC/RC filters, alpha 0.3)
symRate = 10e6;
alpha = 0.3;

fprintf(inst, 'sense:ddemod:modulation:type qpsk');
fprintf(inst, 'sense:ddemod:srate %d', symRate);
fprintf(inst, 'sense:ddemod:filter:measurement off');
fprintf(inst, 'sense:ddemod:filter:reference rcosine');
fprintf(inst, 'sense:ddemod:filter:alpha %d', alpha);
fprintf(inst, 'sense:ddemod:symbol:points one');
% fprintf(inst, 'sense:ddemod:analysis:length 20000');
% fprintf(query(inst, 'sense:acquisition:samples?'));


%% #################ACQUIRE/PROCESS DATA#################
% start acquisition
fprintf(inst, 'initiate:immediate');
inst.timeout = 100;
% wait for acquisition to finish
query(inst, '*opc?');

% query results from the constellation display (details in programmer manual)
results = str2num(query(inst, 'fetch:conste:results?'));

% print out the results
% see Python's format spec docs for more details: https://goo.gl/YmjGzV
fprintf('EVM (RMS): %2.3f%%, EVM (peak): %2.3f%%, Symbol: %4.0f\n', results);

% get EVM vs time data
fprintf(inst, 'fetch:evm:trace?');
evmVsTime = binblockread(inst, 'float');

plot(evmVsTime)
title('EVM vs Symbol #')
xlabel('Symbol')
ylabel('EVM (%)')

%% Close instrument
fclose(inst);
delete(inst);
clear inst;