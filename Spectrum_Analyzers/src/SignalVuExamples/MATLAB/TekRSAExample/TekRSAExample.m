%% MATLAB script to transfer acquired IQ waveforms from Tektronix Spectrum Analyzer 
% This example illustrates the use of MATLAB to set up a Tektronix
% Spectrum Analyzer for acquisition and then transfer the acquired
% I/Q data to MATLAB. Tektronix VISA will be used for communicating with
% your instrument, please ensure that it is installed.
%
% Copyright 2014 The MathWorks, Inc.

% Clear MATLAB workspace of any previous instrument connections
instrreset;

% Create VISA connection
% Change VISA Address to that of your instrument
visaAddress = 'TCPIP0::172.28.16.187::inst0::INSTR';
myRSA = visa('tek', visaAddress);
recordTime = 0.01; %seconds
myRSA.InputBufferSize = recordTime*12.5e6; %12.5 MHz sampling rate
myRSA.Timeout = 15; % set timeout to 15 seconds
myRSA.ByteOrder = 'littleEndian'; % Instrument returns data in littleEndian format

% Open the connection to the RSA
fopen(myRSA);

% Reset the instrument to a known state
fprintf(myRSA,'*RST;*CLS');

% Abort any existing measurements
fprintf(myRSA,'ABOR');
fprintf(myRSA,'TRIG:SEQ:STAT 0');
fprintf(myRSA,'INIT:CONT OFF');

% Analyzer settings
bandwidth       = 10e6;         % bandwidth in Hz
centerFrequency = 1000e6;       % center frequency in Hz
frequencySpan   = 10e6;         % frequency span in Hz
refLevel        = -30;          % analyzer reference level in dBm
inputAtten      = -20;          % Internal attenuation in dB

% Set up parameters for measurement
% Mode Length
fprintf(myRSA, 'SENS:ACQ:MODE LENGTH');
% Acquisition time in seconds
fprintf(myRSA, ['SENS:ACQ:SEC ' num2str(recordTime)]);
% Acquisition bandwidth
fprintf(myRSA, ['SENS:ACQ:BAND ' num2str(bandwidth)]);
% Option to decimate acquired data
fprintf(myRSA, 'SENS:IQVT:MAXT NEV');
% Frequency Span
fprintf(myRSA, ['SENS:IQVT:FREQ:SPAN ' num2str(frequencySpan)]);
% Center Frequency
fprintf(myRSA, ['SENS:IQVT:FREQ:CENT '...
    num2str(centerFrequency)]);

% Set up preamp
fprintf(myRSA, 'SENS:DPSA:CLE:RES');
fprintf(myRSA, 'INPUT:RF:GAIN:STATE ON');
fprintf(myRSA, 'INPUT:RF:ATTENUATION:AUTO OFF');
fprintf(myRSA, ['INPUT:RF:ATTENUATION ' num2str(inputAtten)]);
fprintf(myRSA, ['INPUT:RLEVEL ' num2str(refLevel)]);

% Select IQ Measurement and the related display for it
fprintf(myRSA,'DISPl:GEN:MEAS:NEW IQVT');
fprintf(myRSA,'DISPl:GEN:MEAS:SELect IQVT');
fprintf(myRSA,'DISPl:IQVT:X:SCAL:AUTO');
fprintf(myRSA,'DISPl:IQVT:Y:SCAL:AUTO');
fprintf(myRSA,'DISPl:GEN:MEAS:DEL SPECT');

% Display the spectrum view also
fprintf(myRSA,'DISP:GEN:MEAS:NEW DPSA');

% Make meaurement
fprintf(myRSA,'SENS:IQVT:CLE:RES');
fprintf(myRSA,'INITIATE:IMMEDIATE');
disp('Making measurement...');

% Wait till the instrument completes making the measurement
operationComplete = query(myRSA,'*OPC?');
while ~isequal(str2double(operationComplete),1)
    operationComplete = query(myRSA,'*OPC?');
end

% Get number of IDs
IDdetails        = query(myRSA,'FETC:RFIN:REC:IDS?');
[beginID,remain] = strtok(IDdetails,',');
endID            = strtok(remain,',');

if isempty(endID)
    IDdetails        = query(myRSA,'FETC:RFIN:REC:IDS?');
    [beginID,remain] = strtok(IDdetails,',');
    endID            = strtok(remain,',');
end

% If there are more than one ID, warn
if ~isequal(str2double(beginID),str2double(endID))
    warning(sprintf(['Unexpected number of IDs in this acquisition. ', ...
        'IDdetails: %s.\nData only being returned for first ID.'],IDdetails));
    beginID = '1';
end

% Get the header. For details of the header fields, refer to page 2-488 of
% the PDF file:
% http://www2.tek.com/cmsreplive/marep/17272/077024902web_2010.06.21.11.36.16_17272_EN.pdf
remain = query(myRSA,['FETC:RFIN:IQ:HEAD? ' beginID]);
if length(remain)<10
    remain = query(myRSA,['FETC:RFIN:IQ:HEAD? ' beginID]);
end
for i = 1:9
    [headerField{i},remain] = strtok(remain,',');
end

% Display info to user indicating MATLAB is busy
disp(sprintf('Signal sampled at %d Hz. Transferring %d points to MATLAB.', ...
    str2double(headerField{2}),str2double(headerField{3}))); %#ok

% Increase timeout as transferring data can take time. This can be done
% only when the connection is closed. 
fclose(myRSA);
myRSA.Timeout = 300;
fopen(myRSA);
 
% The firmware crashes if we try and retrieve a lot of data in one go so we
% get data from the instrument in smaller chunks
maxSafeSamples = myRSA.InputBufferSize/8; % total buffer size/(8 bytes per IQ
                                          % Sample)  (single precision data type)
maxSamples     = str2double(headerField{3});
if maxSamples <= maxSafeSamples
    fprintf(myRSA,['FETC:RFIN:IQ? 1,0,' num2str(maxSamples)]);
    data = binblockread(myRSA,'single');
else
    remainingData = maxSamples;
    startSamples  = 0;
    data          = single(zeros(1,maxSamples*2));
    while remainingData>0
        % Choose the data to be transferred 
        fprintf(myRSA,['FETC:RFIN:IQ? 1,' num2str(startSamples) ',' ...
            num2str(startSamples+maxSafeSamples - 1)]);
        % Transfer the selected data
        data((startSamples*2+1):(startSamples+maxSafeSamples)*2) = ...
            binblockread(myRSA,'single');
        startSamples    = startSamples + maxSafeSamples;
        remainingData   = remainingData - maxSafeSamples;
        if remainingData < maxSafeSamples
            maxSafeSamples = remainingData;
        end        
    end
end

% Extract I and Q components from the data variable. The 'data' variable
% has I and Q data interleaved.
Idata = data(1:2:end);
Qdata = data(2:2:end);

% I and Q data can now be combined to create a complex data representation
receivedData = (complex(data(1:2:end),data(2:2:end)));

% Plot the absolute value of the acquired IQ data and add axis labels
plot(abs(receivedData)); 
xlabel('Sample Index'); 
ylabel('Volts');
title('Waveform Acquired from Tektronix Oscilloscope');
grid on;

%% Clean up connections    
fclose(myRSA); 
clear myRSA;

% This script provides an example of communicating with Tektronix
% instruments using text based commands. To learn about other options to
% communicate with instruments from MATLAB visit the following page:
% https://www.mathworks.com/products/instrument
%
% To learn more about Tektronix instruments supported by MATLAB, visit the
% following links:
% https://www.mathworks.com/tektronix
% http://www.tek.com/technology/using-matlab-tektronix-instruments