function P=findpeakslidersRedraw(x,y,SlopeThreshold,AmpThreshold,SmoothWidth,FitWidth)
% Redraws graph for FindPeakSliders when slider are moved.
% Tom O'Haver (toh@umd.edu). Version 1.6 October 26, 2006

hold off
plot(x,y,'m')  % Graph the signal in red
P=findpeaks(x,y,SlopeThreshold,AmpThreshold,SmoothWidth,FitWidth);
title([num2str(max(P(:,1))) ' peaks detected.'])
xlabel(['SlopeT = ' num2str(SlopeThreshold) '    AmpT = ' num2str(AmpThreshold) '    SmoothWidth = ' num2str(SmoothWidth) '    FitWidth = ' num2str(FitWidth) ])
text(P(:, 2),P(:, 3),num2str(P(:,1)))  % Number the peaks found on the graph
axis([x(1) x(length(x)) min(y) max(y)]); % Update plot