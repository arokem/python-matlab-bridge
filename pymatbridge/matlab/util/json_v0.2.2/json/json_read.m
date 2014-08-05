function value = json_read(filename, varargin)
%READ Load a matlab value from a JSON file.
%
% SYNOPSIS
%
%   value = json.read(filename)
%   value = json.read(..., optionName, optionValue, ...)
%
% The function parses a JSON file and load into a matlab value. By default,
% numeric literals are converted to double, string is converted to a char
% array, logical literals are converted to logical. A JSON array is converted
% to either a double array, a logical array, a cell array, or a struct
% array. A JSON object is converted to a struct array.
%
% The function takes the same options as json.load.
%
% See also json.load

  fid = 0;
  try
    fid = fopen(filename, 'r');
    value = json_load(fscanf(fid, '%c', inf));
    fclose(fid);
  catch e
    if fid ~= 0, fclose(fid); end
    rethrow(e);
  end

end
