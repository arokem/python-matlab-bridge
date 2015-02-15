function Y = isrow(X)
%
% ISROW    True for row vectors.
%
%   Y = ISROW(X) returns logical 1 if X is a row vector, 0 otherwise.
%   ISROW returns 1 for scalars also.
%
%

if ndims(X)==2 && size(X,1)==1 && size(X,2)>=1
   Y = logical(1);
else
   Y = logical(0);
end
