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
%    Full path to the output .ipynb file

if length(varargin)
    outputfile = sprintf('--outfile %s', varargin{1});
else
    outputfile = '';
end

% Matlab system path-setting is broken, so we place the
% publish-notebook executable right here, so we can easily find it
binpath = fileparts(which(mfilename));
pkgpath = fileparts(fileparts(fileparts(binpath)));
cmd_str = sprintf('%s/publish-notebook %s %s', binpath, mfile, outputfile);

setenv('PYTHONPATH', pkgpath);
[status,result] = system(cmd_str)
