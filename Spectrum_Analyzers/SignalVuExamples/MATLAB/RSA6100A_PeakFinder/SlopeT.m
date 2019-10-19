function findpeakslider1(n,h)
% Changes SlopeThreshold when the SlopeThreshold slider is moved.
global x
global y
global SlopeThreshold 
global AmpThreshold  
global SmoothWidth
global FitWidth
global P
global PeakNumber

SlopeThreshold=10^n;
if PeakNumber==0,
    P=findpeakslidersRedraw(x,y,SlopeThreshold,AmpThreshold,SmoothWidth,FitWidth);
else
    RedrawPeak
end