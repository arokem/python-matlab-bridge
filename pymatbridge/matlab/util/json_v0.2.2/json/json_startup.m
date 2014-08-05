function json_startup(varargin)
%STARTUP Initialize runtime environment.
%
% SYNOPSIS
%
%   json.startup(optionName, optionValue, ...)
%
% The function internally adds dynamic java class path. This process clears
% any matlab internal states, such as global/persistent variables or mex
% functions. To avoid unexpected state reset, execute this function once before
% using other json API functions.
%
% OPTIONS
%
% The function takes a following option.
%
%   'WarnOnAddPath'   Warn when javaaddpath is internally called. Default false.
%
% EXAMPLE
%
%   >> json.startup
%
% See also javaaddpath javaclasspath

  WARN_ON_ADDPATH = false;
  for i = 1:2:numel(varargin)
    switch varargin{i}
      case 'WarnOnAddpath', WARN_ON_ADDPATH = logical(varargin{i+1});
    end
  end

  jar_file = fullfile(fileparts(mfilename('fullpath')), 'java', 'json.jar');
  if ~any(strcmp(jar_file, javaclasspath))
    javaaddpath(jar_file);
    if WARN_ON_ADDPATH
      warning('json:startup', ['Adding json.jar to the dynamic Java class ' ...
        'path. This has cleared matlab internal states, such as global '...
        'variables, persistent variables, or mex functions. To avoid this, '...
        'call json.startup before using other json API functions. See '...
        '<a href="matlab:doc javaaddpath">javaaddpath</a> for more ' ...
        'information.' ...
        ]);
    end
  end
end
