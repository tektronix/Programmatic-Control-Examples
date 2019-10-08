% A self-contained interactive demonstration of FindPeakSliders applied 
% to a data set containing four simple peaks with increasing peak height 
% and peak width. Use this to understand the difference between the 
% variables SlopeThreshold (SlopeT), which discriminates on the basis 
% of peak width, and AmpThreshold (AmpT), which discriminates on the 
% basis of peak amplitude. Peak number and the estimated position, height, 
% and width of each peak is returned in the matrix P.
% Tom O'Haver (toh@umd.edu). Version 1.6 October 26, 2006
warning off MATLAB:polyfit:RepeatedPointsOrRescale
format compact
close
clear
global x
global y
global SlopeThreshold 
global AmpThreshold  
global SmoothWidth
global FitWidth
global PeakNumber 
global P
figure(1);clf

% Simulate data set
increment=1;
x=[1:increment:400];
% For each simulated peak, enter the amplitude, position, and width below
amp=[2 3 4 5];  % Amplitudes of the peaks
pos=[50 125 200 300];   % Positions of the peaks
wid=[20 40 60 80];   % Widths of the peaks
Noise=.04;
% A = matrix containing one of the unit-amplidude peak in each of its srow
A = zeros(length(pos),length(x));
for k=1:length(pos)
  if amp(k)>0, A(k,:)=gaussian(x,pos(k),wid(k)); end; % Or you can use any other peak function
end
z=amp*A;  % Multiplies each row by the corresponding amplitude and adds them up
y=z+Noise.*randn(size(z));

% Call the interactive findpeaks script
FindPeakSliders;

%Print out peak table in Matlab Command window
P