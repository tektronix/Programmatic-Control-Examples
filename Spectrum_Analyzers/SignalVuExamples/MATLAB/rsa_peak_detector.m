% VISA Control: RSA Peak Detector
% Author: Morgan Allison
% Date Edited: 8/17
% This program tracks the peak frequency 10 times, writes the results
% to a csv file, and creates a scatter plot of the results.
% Windows 7 64-bit, TekVISA 4.0.4
% Matlab r2017a with ICT
% Download SignalVu-PC programmer manual: http://www.tek.com/node/1828803
% Download RSA5100B programmer manual: 
% http://www.tek.com/spectrum-analyzer/inst5000-manual-7
% Tested on RSA306B/RSA507A with SignalVu-PC 3.10.0030


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

% preset, clear buffer, and stop acquisition
fprintf(inst, 'system:preset');
fprintf(inst, '*cls');
fprintf(inst, 'abort');


%%  #################CONFIGURE INSTRUMENT#################
% configure acquisition parameters
freq = 2e9;
span = 40e6;
rbw = 100;
refLevel = -50;

fprintf(inst, 'spectrum:frequency:center %d', freq);
fprintf(inst, 'spectrum:frequency:span %d', span);
fprintf(inst, 'spectrum:bandwidth %d', rbw);
fprintf(inst, 'input:rlevel %d', refLevel);

actualFreq = query(inst, 'spectrum:frequency:center?');
actualSpan = query(inst, 'spectrum:frequency:span?');
actualRbw = query(inst, 'spectrum:bandwidth?');
actualRefLevel = query(inst, 'input:rlevel?');

fprintf('CF: %s Hz\n', actualFreq);
fprintf('Span: %s Hz\n', actualSpan);
fprintf('RBW: %s Hz\n', actualRbw);
fprintf('Reference Level: %s\n\n', actualRefLevel);


fprintf(inst, 'trigger:status off');
fprintf(inst, 'initiate:continuous off');

%%  #################ACQUIRE/PROCESS DATA#################
fprintf(inst, 'calculate:marker:add');
file = fopen('C:\users\mallison\documents\matlab\peak_detector.csv', 'w+');
fprintf(file, 'Frequency, Amplitude\n');

peakFreq = 0;
peakAmp = 0;
for i = 1:10
    fprintf(inst, 'initiate:immediate');
    query(inst, '*opc?');
    
    fprintf(inst, 'calculate:spectrum:marker0:maximum');
    peakFreq = str2double(query(inst, 'calculate:spectrum:marker0:X?'));
    peakAmp = str2double(query(inst, 'calculate:spectrum:marker0:Y?'));
    disp(peakFreq)
    disp(peakAmp)
    fprintf(file, '%d, %d\n', peakFreq, peakAmp);
end

fclose(file);
% csvwrite('peak_detector.csv', csvMatrix);

scatter(peakFreq, peakAmp)
title('Scatter Plot of Amplitude vs Frequency')
xlabel('Frequency (Hz)')
ylabel('Amplitude (dBm)')
xlim([(freq - span / 2), (freq + span / 2)])
ylim([(refLevel - 100), refLevel])


%% Close inst
fclose(inst);
delete(inst);
clear inst;