function publish_notebook(mfile, varargin)
% function publish_notebook(mfile, [outputfile])
%
% Publish a Matlab m file as an interactive notebook in .ipynb format
%
% Parameters
% ----------
% mfile : str
%    Full path to the input m file.
% outputfile

if length(varargin)
    outputfile = varargin{1};
else
    outputfile = '';
end

% Matlab system path-setting is broken, so we place the
% publish-notebook executable right here, so we can easily find it
binpath = fileparts(which(mfilename));
cmd_str = sprintf('%s/publish-notebook %s %s', binpath, mfile, outputfile);

[status,result] = unix(cmd_str)