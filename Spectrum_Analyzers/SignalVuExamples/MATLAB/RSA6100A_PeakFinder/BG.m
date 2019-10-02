function findpeakslider6(n,h)
% Called when the BG slider is clicked.

global x
global y
global SlopeThreshold 
global AmpThreshold  
global SmoothWidth
global FitWidth
global P
global PeakNumber

warning off MATLAB:divideByZero

BaselinePoints=5;  % Change as you wish

% Acquire background points from user mouse clicks
title(['Click on ' num2str(BaselinePoints) ' points on the baseline between the peaks.'])
X=[];Y=[];
for g=1:BaselinePoints;
   [clickX,clickY] = GINPUT(1);
   X(g)=clickX;
   Y(g)=clickY;
   xlabel(['Baseline point '  num2str(g) ])
end
yy=y;
for k=1:length(X)-1,
   fp=val2ind(x,X(k));
   lp=val2ind(x,X(k+1));
   yy(fp:lp)=y(fp:lp)-((Y(k+1)-Y(k))/(X(k+1)-X(k))*(x(fp:lp)-X(k))+Y(k));
end
y=yy;
if PeakNumber==0,
    P=findpeakslidersRedraw(x,y,SlopeThreshold,AmpThreshold,SmoothWidth,FitWidth);
else
    RedrawPeak
end