% Max Jaderberg 2011

function varargout = run_dot_m( file_to_run, arguments, nout )
%RUN_DOT_M Runs the given .m file with the argument struct given
%   For exmaple run_dot_m('/path/to/function.m', args);
%   args is a struct containing the arguments. function.m must take only
%   one parameter, the argument structure

    [dname, func_name, ext] = fileparts(file_to_run);

    if size(ext)
        if ~strcmp(ext, '.m')
            varargout = 'Error: Need to give path to .m file';
            return
        end
    end

    % Add function path to current path
    if size(dname)
        addpath(dname);
    end

    [varargout{1:nout}] = feval(func_name, arguments);

end
