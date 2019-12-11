% Interactive findpeaks script with peak-zoom feature, 
% for pre-defined data in x,y. 
% Load a typical data set into the vectors x,y, then run this 
% m-file and adjust the 5 sliders to determine what values of the 
% parameters give the most reliable peak detection. Peak number and 
% position, height, and width of each peak is returned in the matrix P. 
% The 5 parameters are:
% SlopeThreshold (SlopeT) - Slope of the smoothed third-derivative that is  
%   taken to indicate a peak. Larger values will neglect small features.
% AmpThreshold (AmpT) - Any peaks with height less than this value are ignored.
% SmoothWidth - Width of smooth functions applied to data before slope is
%   measured. Larger values will neglect small features. The best value is 
%   about equal to the half-width of the peaks.
% FitWidth - The number of points around the "top part" of the (unsmoothed)
%   peak that are taken to determine the peak height, positions, and width.
%   The best value is about equal to the half-width of the peaks.
% Peak - This slider zooms in on any one of the detected peaks, and shows
%   the fitted top of the peak (FitWidth) as a blue curve. To see all the
%   peaks, set the Peaks slider to zero (all the way down).

% Note: If the slider ranges are not appropriate for your data, change 
%       them in lines 61-66.

% Tom O'Haver (toh@umd.edu). Version 1.5 October 18, 2006

warning off MATLAB:polyfit:RepeatedPointsOrRescale
format compact

global x
global y
global SlopeThreshold 
global AmpThreshold  
global SmoothWidth
global FitWidth
global PeakNumber
global P
close
figure(1)


% Graph the signal in red
h=figure(1);
plot(x,y,'m') 
h2=gca;axis([x(1) x(length(x)) min(y) max(y)]);
title('Vary the sliders to see how the parameters effect peak finding performance')

% Initial values of variable parameters
WidthPoints=10;  % Average number of points in half-width of peaks (CHANGE TO FIT YOUR SIGNAL)
SlopeThreshold=WidthPoints^-2;
AmpThreshold=0.1*max(y);
SmoothWidth=WidthPoints/2;  % SmoothWidth should be roughly equal to 1/2 the peak width (in points)
FitWidth=WidthPoints/2; % FitWidth should be roughly equal to 1/2 the peak widths(in points)
if FitWidth<3,FitWidth=3;end
PeakNumber=0;

% Find and number the peaks on the graph
warning off MATLAB:polyfit:RepeatedPointsOrRescale
P=findpeaks(x,y,SlopeThreshold,AmpThreshold,SmoothWidth,FitWidth);
xlabel(['SlopeT = ' num2str(SlopeThreshold) '    AmpT = ' num2str(AmpThreshold) '    SmoothWidth = ' num2str(SmoothWidth) '    FitWidth = ' num2str(FitWidth) ])
text(P(:, 2),P(:, 3),num2str(P(:,1)))  % Number the peaks found on the graph

% Maximum ranges of the sliders (change as needed)
SlopeMax=100;
SlopeMin=10^-6;
AmpMax=max(y);
AmpMin=min(y);
SmoothWidthMax=100;
FitWidthMax=100;
MaxPeaks=40;

% Draw the sliders

rtslid(h,@SlopeT,h2,1,'Scale',[log10(SlopeMin) log10(SlopeMax)],'Def',log10(SlopeThreshold),'Back',[0.9 0.9 0.9],'Label','SlopeT','Position',[0.03 0.5 0.03 0.35]);
rtslid(h,@AmpT,h2,0,'Scale',[AmpMin AmpMax],'Def',AmpThreshold,'Back',[0.9 0.9 0.9],'Label','AmpT','Position',[0.03 0.04 0.03 0.35]);
rtslid(h,@BG,h2,0,'Scale',[0 1],'Def',0,'Back',[0.9 0.9 0.9],'Label','BG','Position',[0.94 0.9 0.03 0.04]);
rtslid(h,@Smooth,h2,0,'Scale',[0 2],'Def',log10(SmoothWidth),'Back',[0.9 0.9 0.9],'Label','Smooth','Position',[0.94 0.32 0.03 0.2]);
rtslid(h,@Fit,h2,0,'Scale',[log10(3) log10(FitWidthMax)],'Def',log10(FitWidth),'Back',[0.9 0.9 0.9],'Label','Fit','Position',[0.94 0.04 0.03 0.2]);
rtslid(h,@Peak,h2,0,'Scale',[0 MaxPeaks],'Def',0,'Back',[0.9 0.9 0.9],'Label','Peak','Position',[0.94 0.6 0.03 0.22]);
