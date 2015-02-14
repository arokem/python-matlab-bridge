% Max Jaderberg 2011

function varargout = run_dot_m( func_to_run, arguments, nout )
%RUN_DOT_M Runs the given function or .m file with the arguments given
%   and the nout selected
%   For exmaple run_dot_m('/path/to/function.m', args, 1);
%   arguments can be a scalar, as cell, or struct containing the arguments.
%   If it is a struct, func_to_run must take only one parameter, the argument structure

    [dname, func_name, ext] = fileparts(func_to_run);

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

    if iscell(arguments)
        [varargout{1:nout}] = feval(func_name, arguments{:});
    else
        [varargout{1:nout}] = feval(func_name, arguments);
    end

end
