function value = json_load(str, varargin)
%LOAD Load matlab value from a JSON string.
%
% SYNOPSIS
%
%   value = json.load(str)
%   value = json.dump(..., optionName, optionValue, ...)
%
% The function parses a JSON string into a matlab value. By default,
% numeric literals are converted to double, string is converted to a char
% array, logical literals are converted to logical. A JSON array is converted
% to either a double array, a logical array, a cell array, or a struct
% array. A JSON object is converted to a struct array.
%
% OPTIONS
%
% The function takes following options.
%
%   'MergeCell'   Try to convert a JSON array into a double, a logical, or
%                 a struct array when possible. Default true.
%
%   'ColMajor'    Represent matrix in column-major order. Default false.
%
% EXAMPLE
%
%   >> value = json.load('{"char":"hello","matrix":[[1,3],[4,2]]}')
%   value =
%
%         char: 'hello'
%       matrix: [2x2 double]
%
%   >> value = json.load('[[1,2,3],[4,5,6]]')
%   value =
%
%        1     2     3
%        4     5     6
%
%   >> value = json.load('[[1,2,3],[4,5,6]]', 'ColMajor', true)
%   value =
%        1     4
%        2     5
%        3     6
%
%   >> value = json.load('[[1,2,3],[4,5,6]]', 'MergeCell', false)
%   value =
%
%       {1x3 cell}    {1x3 cell}
%
% NOTE
%
% Since any matlab values are an array, it is impossible to uniquely map
% all JSON primitives to matlab values. This implementation aims to have
% better interoperability across platforms. Therefore, some matlab values
% cannot be represented in a JSON string. For example, '[1,2,3]' is mapped to
% either [1, 2, 3] or {{1}, {2}, {3}} depending on 'MergeCell' option, but
% cannot produce {1, 2, 3}.
%
% See also json.dump json.read

  json_startup('WarnOnAddpath', true);
  options = get_options_(varargin{:});
  singleton = false;

  str = strtrim(str);
  if isempty(str)
    error('json:invalidString','Invalid JSON string');
  end
  if str(1)=='{'
    node = javaObject('org.json.JSONObject', javaObject('java.lang.String', str));
  else
    singleton = str(1) ~= '[' && str(end) ~= ']';
    if singleton, str = ['[',str,']']; end
    node = javaObject('org.json.JSONArray', javaObject('java.lang.String', str));
  end
  value = parse_data_(node, options);
  if singleton, value = value{:}; end
end

function options = get_options_(varargin)
%GET_OPTIONS_
  options = struct(...
    'MergeCell', true,...
    'ColMajor', false...
    );
  for i = 1:2:numel(varargin)
    switch varargin{i}
      case 'MergeCell'
        options.MergeCell = logical(varargin{i+1});
      case 'ColMajor'
        options.ColMajor = logical(varargin{i+1});
    end
  end
end

function value = parse_data_(node, options)
%LOAD_DATA_
  if isa(node, 'char')
    value = char(node);
  elseif isa(node, 'double')
    value = double(node);
  elseif isa(node, 'logical')
    value = logical(node);
  elseif isa(node, 'org.json.JSONArray')
    value = cell(node.length() > 0, node.length());
    for i = 1:node.length()
      value{i} = parse_data_(node.get(i-1), options);
    end
    if options.MergeCell
      value = merge_cell_(value, options);
    end
  elseif isa(node, 'org.json.JSONObject')
    value = struct;
    itr = node.keys();
    while itr.hasNext()
      key = itr.next();
      field = char(key);
      safe_field = genvarname(char(key), fieldnames(value));
      if ~strcmp(field, safe_field)
        warning('json:fieldNameConflict', ...
                'Field %s renamed to %s', field, safe_field);
      end
      value.(safe_field) = parse_data_(node.get(javaObject('java.lang.String', key)), ...
                                       options);    
    end
    % Check if the struct just decoded represents an array or complex number
    if isfield(value,'ndarray') && isfield(value, 'shape')
      if isfield(value, 'data')
          arr = typecast(base64decode(value.data), 'double');
      else
          r = typecast(base64decode(value.real), 'double');
          im = typecast(base64decode(value.imag), 'double');
          arr = complex(r, im);
      end
      value = reshape(arr, value.shape);
    elseif isfield(value,'real') && isfield(value, 'imag')
      complex_value = complex(value.real, value.imag);
      value = complex_value;
    end
  % In MATLAB, nested classes end up with a $ in the name, in Octave it's a .
  elseif isa(node, 'org.json.JSONObject$Null') || isa(node, 'org.json.JSONObject.Null')
    value = [];
  else
    error('json:typeError', 'Unknown data type: %s', class(node));
  end
end

function value = merge_cell_(value, options)
%MERGE_CELL_
  if isempty(value) || all(cellfun(@isempty, value))
    return;
  end
  if isscalar(value)
    return;
  end
  if ~all(cellfun(@isscalar, value)) && all(cellfun(@ischar, value))
    return;
  end

  if is_mergeable_(value);
    dim = ndims(value)+1;
    mergeable = true;
    if options.ColMajor
      if all(cellfun(@isscalar, value))
        dim = 1;
        if all(cellfun(@iscell, value)) % Singleton row vector [[a],[b]].
          value = cat(2, value{:});
          mergeable = is_mergeable_(value);
          dim = 2;
        end
      elseif all(cellfun(@iscolumn, value))
        dim = 2;
      end
    else
      if all(cellfun(@isscalar, value))
        dim = 2;
        if all(cellfun(@iscell, value)) % Singleton col vector [[a],[b]].
          value = cat(1, value{:});
          mergeable = is_mergeable_(value);
          dim = 1;
        end
      elseif all(cellfun(@isrow, value))
        dim = 1;
      end
    end
    if mergeable
      value = cat(dim, value{:});
    end
  end
end

function flag = is_mergeable_(value)
%CHECK_MERGEABLE_ Check if the cell array is mergeabhe.
  signature = type_info_(value{1});
  flag = true;
  for i = 2:numel(value)
    vec = type_info_(value{i});
    flag = numel(signature) == numel(vec) && all(signature == vec);
    if ~flag, break; end
  end
end

function vec = type_info_(value)
%TYPE_INFO_ Return binary encoding of type information
  vec = [uint8(class(value)), typecast(size(value), 'uint8')];
  if isstruct(value)
    fields = fieldnames(value);
    vec = [vec, uint8([fields{:}])];
  end
end



function y = base64decode(x)
  %BASE64DECODE Perform base64 decoding on a string.
  %
  %   BASE64DECODE(STR) decodes the given base64 string STR.
  %
  %   Any character not part of the 65-character base64 subset set is silently
  %   ignored.
  %
  %   This function is used to decode strings from the Base64 encoding specified
  %   in RFC 2045 - MIME (Multipurpose Internet Mail Extensions).  The Base64
  %   encoding is designed to represent arbitrary sequences of octets in a form
  %   that need not be humanly readable.  A 65-character subset ([A-Za-z0-9+/=])
  %   of US-ASCII is used, enabling 6 bits to be represented per printable
  %   character.
  %
  %   See also BASE64ENCODE.

  %   Author:      Peter J. Acklam
  %   Time-stamp:  2004-09-20 08:20:50 +0200
  %   E-mail:      pjacklam@online.no
  %   URL:         http://home.online.no/~pjacklam

  %   Modified by Guillaume Flandin, May 2008

  % check number of input arguments
  %--------------------------------------------------------------------------

  error(nargchk(1, 1, nargin));

  % Perform the following mapping
  %--------------------------------------------------------------------------
  %   A-Z  ->  0  - 25         a-z  ->  26 - 51         0-9  ->  52 - 61
  %   +    ->  62              /    ->  63              =    ->  64
  %   anything else -> NaN

  base64chars = NaN(1,256);
  base64chars('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=') = 0:64;
  x = base64chars(x);

  % Remove/ignore any characters not in the base64 characters list or '='
  %--------------------------------------------------------------------------

  x = x(~isnan(x));

  % Replace any incoming padding ('=' -> 64) with a zero pad
  %--------------------------------------------------------------------------

  if     x(end-1) == 64, p = 2; x(end-1:end) = 0;
  elseif x(end)   == 64, p = 1; x(end) = 0;
  else                   p = 0;
  end

  % Allocate decoded data array
  %--------------------------------------------------------------------------

  n = length(x) / 4;                               % number of groups
  x = reshape(uint8(x), 4, n);                     % input data
  y = zeros(3, n, 'uint8');                        % decoded data

  % Rearrange every 4 bytes into 3 bytes
  %--------------------------------------------------------------------------
  %    00aaaaaa 00bbbbbb 00cccccc 00dddddd
  %
  % to form
  %
  %    aaaaaabb bbbbcccc ccdddddd

  y(1,:) = bitshift(x(1,:), 2);                    % 6 highest bits of y(1,:)
  y(1,:) = bitor(y(1,:), bitshift(x(2,:), -4));    % 2 lowest bits of y(1,:)

  y(2,:) = bitshift(x(2,:), 4);                    % 4 highest bits of y(2,:)
  y(2,:) = bitor(y(2,:), bitshift(x(3,:), -2));    % 4 lowest bits of y(2,:)

  y(3,:) = bitshift(x(3,:), 6);                    % 2 highest bits of y(3,:)
  y(3,:) = bitor(y(3,:), x(4,:));                  % 6 lowest bits of y(3,:)

  % Remove any zero pad that was added to make this a multiple of 24 bits
  %--------------------------------------------------------------------------

  if p, y(end-p+1:end) = []; end

  % Reshape to a row vector
  %--------------------------------------------------------------------------

  y = reshape(y, 1, []);
end
