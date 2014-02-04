function pymat_set_variable(args)
% Setup a variable in Matlab workspace

    assignin('base', args.name, args.value);

end %function
