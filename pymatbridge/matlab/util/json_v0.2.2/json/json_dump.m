function str = json_dump(value, varargin)
%DUMP Encode matlab value into a JSON string.
%
% SYNOPSIS
%
%   str = json.dump(value)
%   str = json.dump(..., optionName, optionValue, ...)
%
% The function converts a matlab value to a JSON string. A value can be any
% of a double array, a logical array, a char array, a cell array, or a
% struct array. Numeric values other than double are converted to double.
% A struct array is mapped to a JSON object. However, since a JSON object
% is unordered, the order of field names are not preserved.
%
% OPTIONS
%
% The function takes following options.
%
%   'ColMajor'    Represent matrix in column-major order. Default false.
%   'indent'      Pretty-print the output string with indentation.  Default
%                 []
%
% EXAMPLE
%
%   >> X = struct('matrix', magic(2), 'char', 'hello');
%   >> str = json.dump(X)
%   str =
%
%   {"char":"hello","matrix":[[1,3],[4,2]]}
%
%   >> str = json.dump([1,2,3;4,5,6])
%   str =
%
%   [[1,2,3],[4,5,6]]
%
%   >> str = json.dump([1,2,3;4,5,6], 'ColMajor', true)
%   str =
%
%   [[1,4],[2,5],[3,6]]
%
%   >> str = json.dump([1,2,3;4,5,6], 'indent', 2)
%     str =
%
%     [
%       [
%         1,
%         2,
%         3
%       ],
%       [
%         4,
%         5,
%         6
%       ]
%     ]
%
% NOTE
%
% Since any matlab values are an array, it is impossible to uniquely map
% all matlab values to JSON primitives. This implementation aims to have
% better interoperability across platforms. Therefore, some matlab values
% are mapped to the same representation. For example, [1,2] and {1,2} are
% mapped to the same json string '[1,2]'.
%
% See also json.load json.write

  json_startup('WarnOnAddpath', true);
  options = get_options_(varargin{:});
  obj = dump_data_(value, options);
  if isempty(options.indent)
      str = char(obj.toString());
  else
      str = char(obj.toString(options.indent));
  end
end

function options = get_options_(varargin)
%GET_OPTIONS_
  options = struct(...
    'ColMajor', false,...
    'indent', [] ...
    );
  for i = 1:2:numel(varargin)
    switch varargin{i}
      case 'ColMajor'
        options.ColMajor = logical(varargin{i+1});
      case 'indent'
        options.indent = varargin{i+1};
      otherwise
        error('Unknown option to json.dump')
    end
  end
end

function obj = dump_data_(value, options)
%DUMP_DATA_
  if ischar(value) && (isvector(value) || isempty(value))
    obj = javaObject('java.lang.String', value);
  elseif isempty(value) && isnumeric(value)
    json_object = javaObject('org.json.JSONObject');
    obj = json_object.NULL;
  elseif ~isscalar(value)
    obj = javaObject('org.json.JSONArray');

    if ndims(value) > 2
      split_value = num2cell(value, 1:ndims(value)-1);
      for i = 1:numel(split_value)
        obj.put(dump_data_(split_value{i}, options));
      end
    else
      if options.ColMajor && iscolumn(value) || ...
          ~options.ColMajor && isrow(value)
        if iscell(value)
          for i = 1:numel(value), obj.put(dump_data_(value{i}, options)); end
        else
          for i = 1:numel(value), obj.put(dump_data_(value(i), options)); end
        end
      else
        value = num2cell(value, 2 - options.ColMajor);
        if all(cellfun(@isscalar, value))
          for i = 1:numel(value), obj.put(dump_data_(value(i), options)); end
        else
          for i = 1:numel(value), obj.put(dump_data_(value{i}, options)); end
        end
      end
    end
  elseif iscell(value)
    obj = javaObject('org.json.JSONArray');
    for i = 1:numel(value)
      obj.put(dump_data_(value{i}, options));
    end
  elseif isnumeric(value)
    if isreal(value)
      obj = javaObject('java.lang.Double', value);
    % Encode complex number as a struct
    else
      complex_struct = struct;
      complex_struct.real = real(value);
      complex_struct.imag = imag(value);
      obj = dump_data_(complex_struct, options);
    end
  elseif islogical(value)
    obj = javaObject('java.lang.Boolean', value);
  elseif isstruct(value)
    obj = javaObject('org.json.JSONObject');
    keys = fieldnames(value);
    for i = 1:length(keys)
      obj.put(keys{i},dump_data_(value.(keys{i}), options));
    end
  else
    error('json:typeError', 'Unsupported data type: %s', class(value));
  end
end
