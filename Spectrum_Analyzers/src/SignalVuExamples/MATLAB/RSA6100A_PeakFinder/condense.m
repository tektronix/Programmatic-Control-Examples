function sy=condense(y,n)
% Condense y by a factor of n, where n is a non-zero positive integer.
% Produces a shorter, approximate version of vector y, with each group 
% of n adjacent points in y replaced by its average. Use for reducing the 
% length and processing time of over-sampled signals or for preliminary 
% and exploratory analysis of very large signals to locate the interesting 
% bits, which can then be selected out of the full-length signal for 
% more precise analysis. For x,y data sets, use this function on both 
% independent variable x AND dependent variable y so that the features 
% of y will appear at the same x values.
% Example: condense([1 2 3 4 5 6 7 8 9 10 11 12],3) yields [2 5 8 11]
% condense([.9 1.1 .9 1 .9 1.1 .9 1 .9 1.1 .9 1],3) = [0.9667 1 0.9333 1]
% condense([0 0 0 0 0 0 0 1 1 1 1 1 1 1],2) = [0 0 0 .5 1 1 1]
n=round(n);
m=floor(length(y)/n);
if n > 1
    sy=mean(reshape(y(1:n*m),n,m));
else
    sy=y;
end