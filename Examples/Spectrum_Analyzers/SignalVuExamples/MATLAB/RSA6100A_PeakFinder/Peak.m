function findpeakslider5(n,h)
% Changes PeakNumber when the Peak slider is moved.
global x
global y
global SlopeThreshold 
global AmpThreshold  
global SmoothWidth
global FitWidth
global P
global PeakNumber
PeakNumber=round(n);
if PeakNumber==0,
    P=findpeakslidersRedraw(x,y,SlopeThreshold,AmpThreshold,SmoothWidth,FitWidth);
else
    RedrawPeak
end