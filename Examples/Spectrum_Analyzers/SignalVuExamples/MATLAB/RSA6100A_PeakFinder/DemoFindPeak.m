% A simple self-contained demonstration of the findpeak function (line 48)
% applied to noisy synthetic data set consisting of a random number of narrow 
% peaks.  Each time you run this, a different set of peaks is generated.
% The 4 adjustable parameters (in lines 40 - 43) are:
% SlopeThreshold - Slope of the smoothed third-derivative that is taken 
%    to indicate a peak. Larger values will neglect small features.
% AmpThreshold - Any peaks with height less than AmpThreshold are ignored.
% SmoothWidth - Width of smooth functions applied to data before slope is
%    measured. Larger values will neglect small features. A reasonable value is 
%    about equal to 1/2 the width of the peaks.
% FitWidth - The number of points around the "top part" of the (unsmoothed)
%    peak that are taken to determine the peak height, positions, and width.
%    A reasonable value is about equal to 1/2 the width of the peaks.
% Tom O'Haver (toh@umd.edu). Version 1.6 October 26, 2006

format compact
figure(1);clf

% Generate synthetic signal 
increment=.2; % Increment between adjacent values of x.
x=[1:increment:400];
% For each simulated peak, enter the amplitude, position, and width below
amp=randn(1,38);  % Amplitudes of the peaks
pos=[10:10:380];   % Positions of the peaks
wid=5.*ones(size(pos));   % Widths of the peaks
Noise=.01;
% A = matrix containing one of the unit-amplidude peak in each of its srow
A = zeros(length(pos),length(x));
for k=1:length(pos)
  if amp(k)>0, A(k,:)=gaussian(x,pos(k),wid(k)); end; % Or you can use any other peak function
end
z=amp*A;  % Multiplies each row by the corresponding amplitude and adds them up
y=z+Noise.*randn(size(z)); % Add random noise

figure(1);plot(x,y,'r')  % Graph the signal in red
title('Detected peaks are numbered. Peak table is printed in Command Window')

% Initial values of variable parameters
WidthPoints=mean(wid)/increment; % Average number of points in half-width of peaks
SlopeThreshold=0.5*WidthPoints^-2; % Formula for estimating value of SlopeThreshold
AmpThreshold=0.05*max(y);
SmoothWidth=round(WidthPoints/2);  % SmoothWidth should be roughly equal to 1/2 the peak width (in points)
FitWidth=round(WidthPoints/2); % FitWidth should be roughly equal to 1/2 the peak widths(in points)

% Lavel the x-axis with the parameter values
xlabel(['SlopeThresh. = ' num2str(SlopeThreshold) '    AmpThresh. = ' num2str(AmpThreshold) '    SmoothWidth = ' num2str(SmoothWidth) '    FitWidth = ' num2str(FitWidth) ])

% Find the peaks
start=cputime;
P=findpeaks(x,y,SlopeThreshold,AmpThreshold,SmoothWidth,FitWidth);
ElapsedTime=cputime-start

% Display results
'    Peak #   Position    Height    Width'
P  % Display table of peaks
figure(1);text(P(:, 2),P(:, 3),num2str(P(:,1)))  % Number the peaks found on the graph