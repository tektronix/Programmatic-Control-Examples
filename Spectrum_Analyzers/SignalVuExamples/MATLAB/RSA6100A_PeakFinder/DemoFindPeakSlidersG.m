% Interactive demo of findpeaks function with peak-zoom feature. 
% You can adjust the 5 sliders to determine what
% values of the parameters give the most reliable peak detection. 
% The 5 parameters are:
% SlopeThreshold - Slope of the smoothed third-derivative that is taken 
%  to indicate a peak. Larger values will neglect small features.
% AmpThreshold - Any peaks with height less than AmpThreshold are ignored.
% SmoothWidth - Width of smooth functions applied to data before slope is
%   measured. Larger values will neglect small features. A reasonable value is 
%   about equal to 1/2 of the width of the peaks.
% FitWidth - The number of points around the "top part" of the (unsmoothed)
%   peak that are taken to determine the peak height, positions, and width.
%   A reasonable value is about equal to 1/2 of the width of the peaks.
% Peak - This slider zooms in on any one of the detected peaks, and shows
%   the fitted top of the peak (FitWidth) as a blue curve. To see all the
%   peaks, set the Peaks slider to zero (all the way down).
% Tom O'Haver (toh@umd.edu). Version 1.6 October 26, 2006

warning off MATLAB:polyfit:RepeatedPointsOrRescale
format compact
clear
close
global x
global y
global SlopeThreshold 
global AmpThreshold  
global SmoothWidth
global FitWidth
global PeakNumber
global P
figure(1)

% Simulate data set
increment=5;
x=[1:increment:4000];
% For each simulated peak, enter the amplitude, position, and width below
amp=randn(1,39);  % Amplitudes of the peaks
pos=[200:100:4000];   % Positions of the peaks
wid=60.*ones(size(pos));   % Widths of the peaks
Noise=.01;
% A = matrix containing one of the unit-amplidude peak in each of its srow
A = zeros(length(pos),length(x));
for k=1:length(pos)
  if amp(k)>0, A(k,:)=gaussian(x,pos(k),wid(k)); end; % Or you can use any other peak function
end
z=amp*A;  % Multiplies each row by the corresponding amplitude and adds them up
y=z+Noise.*randn(size(z));
y=y+lorentzian(x,0,4000); % Adds background signal

% Call the interactive findpeaks script
FindPeakSlidersG;

%Print out peak table in Matlab Command window
P