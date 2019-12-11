% VISA Control: RSA Mask Test
% Author: Morgan Allison
% Date Edited: 8/17
% This program sets up a default mask test and queries the frequencies 
% at which violations occured.
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


%% #################INITIALIZE VARIABLES#################
cf = 2.4453e9;
span = 40e6;

fprintf(inst, 'system:preset');
fprintf(inst, 'display:general:measview:new dpx');
fprintf(inst, 'spectrum:frequency:center %d', cf);
fprintf(inst, 'spectrum:frequency:span %d', span);

fprintf(inst, 'calculate:search:limit:match:beep on');
fprintf(inst, 'calculate:search:limit:match:sacquire off');
fprintf(inst, 'calculate:search:limit:match:sdata off');
fprintf(inst, 'calculate:search:limit:match:spicture off');
fprintf(inst, 'calculate:search:limit:match:strace off');
fprintf(inst, 'calculate:search:limit:operation omask');
fprintf(inst, 'calculate:search:limit:operation:feed "dpx", "Trace1"');
fprintf(inst, 'calculate:search:limit:state on');

%% #################ACQUIRE/PROCESS DATA#################
fprintf(inst, 'initiate:immediate');
query(inst, '*opc?');

if str2num(query(inst, 'calculate:search:limit:fail?')) == 1
    maskPoints = str2num(query(inst, 'calculate:search:limit:report:data?'));
    disp(maskPoints);
    fprintf('Mask Violations: %s\n', maskPoints(1));
    for i = 2:length(maskPoints)
        fprintf('Violation Range: %s\n', maskPoints(i));
    end
else
    fprintf('No mask violations have occurred.\n');
end
    
    
%% Close inst
fclose(inst);
delete(inst);
clear inst;