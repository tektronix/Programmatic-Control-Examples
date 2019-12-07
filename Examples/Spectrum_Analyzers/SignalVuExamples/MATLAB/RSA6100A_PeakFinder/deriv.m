function d=deriv(a)
% First derivative of vector using 2-point central difference.
% Example: deriv([1 1 1 2 3 4]) yeilds [0 0 .5 1 1 1]
%  T. C. O'Haver, 1988.
n=length(a);
d(1)=a(2)-a(1);
d(n)=a(n)-a(n-1);
for j = 2:n-1;
  d(j)=(a(j+1)-a(j-1)) ./ 2;
end