% Redraws graph for FindPeakSliders when Peak slider is moved.
% Tom O'Haver (toh@umd.edu). Version 1.6 October 26, 2006
warning off MATLAB:divideByZero
warning off MATLAB:polyfit:PolyNotUnique
global x
global y
global SlopeThreshold 
global AmpThreshold  
global SmoothWidth
global FitWidth
global PeakNumber
global P
axes(h);
if PeakNumber>max(P(:,1)),
    PeakNumber=max(P(:,1));
end
xincrement=x(2)-x(1);
P=findpeaks(x,y,SlopeThreshold,AmpThreshold,SmoothWidth,FitWidth);
FitWidth=round(real(FitWidth));
LowerLimit=round(P(PeakNumber,2)./xincrement-FitWidth);
if LowerLimit<1, LowerLimit=1;,end
UpperLimit=round(P(PeakNumber,2)./xincrement+FitWidth);
if UpperLimit>length(y), UpperLimit=length(y);,end
% [LowerLimit UpperLimit] 
PeakRange=[LowerLimit:UpperLimit];
plot(x(PeakRange),y(PeakRange),'m.');hold on
LowerLimit=round(P(PeakNumber,2)./xincrement-FitWidth/2);
UpperLimit=round(P(PeakNumber,2)./xincrement+FitWidth/2);
if LowerLimit<1, LowerLimit=1;,end
if UpperLimit>length(y), UpperLimit=length(y);,end
PlotRange=[LowerLimit:UpperLimit];
% [min(PlotRange) max(PlotRange)] 
xx=x(PlotRange);
yy=y(PlotRange);
[coef,S,MU]=polyfit(xx,log(abs(yy)),2);  % Fit parabola to log10 of sub-group
c1=coef(3);c2=coef(2);c3=coef(1);
PeakX=-((MU(2).*c2/(2*c3))-MU(1));   % Compute peak position and height or fitted parabola
PeakY=exp(c1-c3*(c2/(2*c3))^2);
MeasuredWidth=MU(2).*2.35703/(sqrt(2)*sqrt(-1*c3));
plot(xx,PeakY.*gaussian(xx,PeakX,MeasuredWidth));
hold off
title(['Peak number ' num2str(PeakNumber) '    Height = ' num2str(PeakY) '    Position =' num2str(round(100*PeakX)/100) '    Width =' num2str(round(10*MeasuredWidth)/10)])
text(P(PeakNumber,2),0.9.*P(PeakNumber,3),num2str(PeakNumber))
xlabel(['SlopeT = ' num2str(SlopeThreshold) '   AmpT = ' num2str(AmpThreshold) '   SmoothWidth = ' num2str(SmoothWidth) '   FitWidth = ' num2str(FitWidth) ])
%axis([x(PeakRange(1)) x(length(PeakRange)) min(y) max(y)]); % Update plot
currentaxis=axis;
text(currentaxis(1),0.99.*currentaxis(4),['Set peak slider to zero to see all peaks'])