function findpeakslider2(n,h)
% Changes AmpThreshold when the AmpThreshold slider is moved.
global x
global y
global SlopeThreshold 
global AmpThreshold  
global SmoothWidth
global FitWidth
global P
global PeakNumber
AmpThreshold=n;
if PeakNumber==0,
    P=findpeakslidersRedraw(x,y,SlopeThreshold,AmpThreshold,SmoothWidth,FitWidth);
else
    RedrawPeak
end