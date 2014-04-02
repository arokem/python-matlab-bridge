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
libpath = fileparts(which(mfilename));
prefix = strsplit(libpath, 'lib');
binpath = strcat(prefix(1), 'bin');
cmd_str = sprintf('publish-notebook %s %s', mfile, outputfile);

setenv('PATH', sprintf('%s:%s', binpath{1}, getenv('PATH')));
[status, result] = system(cmd_str); 

if status == 0 
    disp('Conversion completed');
else
    disp(sprintf('There was a problem converting the file %s:', mfile));
    disp(result)
end




