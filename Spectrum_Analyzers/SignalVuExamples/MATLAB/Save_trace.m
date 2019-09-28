% Create VISA connection
% Change VISA Address to that of your instrument
visaAddress = 'GPIB8::1::INSTR';
myRSA = visa('tek', visaAddress);
recordTime = 0.01; %seconds
myRSA.InputBufferSize = recordTime*12.5e6; %12.5 MHz sampling rate
myRSA.Timeout = 15; % set timeout to 15 seconds

% Open the connection to the RSA
fopen(myRSA);

% Reset the instrument to a known state
fprintf(myRSA,'*RST;*CLS');

% Ask for instrument ID
ID=query(myRSA,'*idn?');

% Save spectrum
fprintf(myRSA,'FETCH:SPECTRUM:TRACE1?');
spectrum = binblockread(myRSA,'single'); 

fclose(myRSA); 
clear myRSA;