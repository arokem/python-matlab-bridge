% Max Jaderberg 2011

function result = run_dot_m( file_to_run, arguments )
%RUN_DOT_M Runs the given .m file with the argument struct given
%   For exmaple run_dot_m('/path/to/function.m', args);
%   args is a struct containing the arguments. function.m must take only
%   one parameter, the argument structure

    [dir, func_name, ext] = fileparts(file_to_run);

    if ~size(ext)
        result = 'Error: Need to give path to .m file';
        return
    end

    if ~strcmp(ext, '.m')
        result = 'Error: Need to give path to .m file';
        return
    end

%     Add function path to current path
    addpath(dir);
    if isstruct(arguments)
        result = feval(func_name, arguments);
    else
        result = feval(func_name);
    end
end
