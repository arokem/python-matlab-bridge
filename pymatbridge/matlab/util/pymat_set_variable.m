function res = pymat_set_variable(args)
% Setup a variable in Matlab workspace

    assignin('base', args.name, args.value);
    res = 1;

end %function
