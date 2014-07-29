function json_write(value, filename, varargin)
%WRITE Write a matlab value into a JSON file.
%
% SYNOPSIS
%
%   json.write(value, filename)
%   json.write(..., optionName, optionValue, ...)
%
% The function saves a matlab value in a JSON file. A value can be any
% of a double array, a logical array, a char array, a cell array, or a
% struct array. Numeric values other than double are converted to double.
% A struct array is mapped to a JSON object. However, since a JSON object
% is unordered, the order of field names are not preserved.
%
% The function takes the same options as json.dump.
%
% See also json.dump

  fid = 0;
  try
    fid = fopen(filename, 'w');
    fprintf(fid, '%s', json_dump(value, varargin{:}));
    fclose(fid);
  catch e
    if fid ~= 0, fclose(fid); end
    rethrow(e);
  end

end
