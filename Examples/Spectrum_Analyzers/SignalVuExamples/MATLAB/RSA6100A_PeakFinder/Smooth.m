function findpeakslider4(n,h)
% Changes SmoothWidth when the SmoothWidth slider is moved.
global x
global y
global SlopeThreshold 
global AmpThreshold  
global SmoothWidth
global FitWidth
global P
global PeakNumber
SmoothWidth=round(10^n);
if PeakNumber==0,
    P=findpeakslidersRedraw(x,y,SlopeThreshold,AmpThreshold,SmoothWidth,FitWidth);
else
    RedrawPeak
end