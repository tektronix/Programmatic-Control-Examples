%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%  2007 Tektronix RTSA Demo program
%
%  This program provides a simple example of VISA control of an RTSA61xx series
%  spectrum analyzer through MATLAB
%
%  To complete this demo you should have TEK VISA installed as well as MATLAB
%   with the intrument control toolbox.  The RTSA should have a simple antenna
%   connected to the RF input
%
%
%
%
%
%  
%  October 2007 Tektronix Inc. Version 2006.10.12.c
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function RTSA6100__Plot_Spectrum
warning off all
%5 MATLAB:Polynomial is not unique
% warning off MATLAB:degree >= number of data points

warning off MATLAB:polyfit:RepeatedPointsOrRescale
clc;            % Clear the command window
close           % Close all open figure windows
clear
format compact
global x
global y
global PeakNumber 
global P

%% 
%--------------------------------------------------------------------------
% User Setup
%--------------------------------------------------------------------------
% Change the IP addresses to match the IP address of your RSA before 
% running the demo.
RTSAIPAddr	= '192.168.1.113';  % Instrument TCP/IP address 
%
%
%--------------------------------------------------------------------------
%% Step 1: Open the VISA connection to the RSA
rtsa = visa( 'tek', ['TCPIP::' RTSAIPAddr '::INSTR'] );     % Setup VISA session with instrument
set( rtsa, 'InputBufferSize', 131072 );                 % Set input buffer, should be 4x number of trace points minimum
set( rtsa, 'Timeout', 50.0 );                       % Set long GPIB time-out in case of long sweeps
fopen( rtsa );

% Query the RSA for its identification and display the results.
% NOTE: This is using the MATLAB Instrument Control Toolbox version of the 
% query command.
[ strIDN, numChars, errMsg ] = query( rtsa, '*IDN?' );

%% Step 2: Setup the RSA using SCPI commands
% Preset the RSA and turn off continuous mode
fprintf( rtsa, '*RST');                             % Reset instrument
query ( rtsa, '*OPC?' );                            % Query OPC to confirm Reset is done
fprintf( rtsa, ':INIT:CONT off' );                  % Set single aquisition mode
fprintf( rtsa, ':SENS:SPEC:FREQ:STAR 88 MHz' );    % Set start frequency
fprintf( rtsa, ':SENS:SPEC:FREQ:STOP 108 MHz' );    % Set stop frequency
fprintf( rtsa, ':SENS:SPEC:BAND:RES 10kHz' );      % Set RBW
fprintf( rtsa, ':TRAC1:SPEC:FUNC AVER' );           % Setup trace averaging
fprintf( rtsa, ':TRAC1:SPEC:AVER:COUN 3' );         % Average 3 traces
fprintf( rtsa, ':INPUT:MLEVEL -30' );               % Set reference level to -30 dBm


%% Step 3:  Fetch Trace & Display

tic;                        % Start Timer
fprintf( rtsa, ':INIT' );       %Trigger an aquisition 
query( rtsa, '*OPC?');          % Query OPC to confirm operation complete
sw_time = toc;              % Calculate Elapsed Time
Start_Freq = str2double(query( rtsa, ':SENS:SPEC:FREQ:STAR?' ))/1e6;        % Get start frequency
Stop_Freq = str2double(query( rtsa, ':SENS:SPEC:FREQ:STOP?' ))/1e6;         % Get stop frequency
fprintf( rtsa, ':FETC:SPEC:TRAC1?' );                                       % Fetch the trace
y = ParseBinary32Bit_SCPI( rtsa );                                      % Convert the trace
x_range = size(y);                                  % Determine # of points
figure(1);clf
x=[1:1:x_range(2)];                     % Create a dummy vector same size as # of trace points
plot(x,y);      
ylim([ -120 0.0 ]);                             % Set power axis to 120 dB
xlim([ 0 x_range(2) ]);                         % Autoset the x axis for the graph based on # of trace points
grid on;
xlabel(['Start = ' num2str(Start_Freq) ' MHz               AQT = ' num2str(sw_time) ' sec.                     Stop = ' num2str(Stop_Freq) ' MHz ']);
ylabel ('Amplitude (dBm)');
title(strIDN);


%% Determine the Peak in the Trace
mean_pwr = mean(y);              % Calculate mean power within the span (not technically correct but works for now)
mn_pwr = mean_pwr + 6;            % Add 6 dB margin
P=findpeaks(x,y,0.9,mn_pwr,1,1);
figure(1);text(P(:, 2),P(:, 3),num2str(P(:,1)))  % Number the peaks found on the graph

'    Peak #   Position    Amplitude '
P                                  % Display table of peaks

return
%%