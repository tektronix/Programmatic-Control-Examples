function d=secderiv(a)
% Second derivative of vector using 3-point central difference.
% Example: secderiv([0 1 2 3 4 3 2 1 0]) yields [ 0 0 0 0 -2 0 0 0 0]
%  T. C. O'Haver, 2006.
n=length(a);
for j = 2:n-1;
  d(j)=a(j+1) - 2.*a(j) + a(j-1);
end
d(1)=d(2);
d(n)=d(n-1);