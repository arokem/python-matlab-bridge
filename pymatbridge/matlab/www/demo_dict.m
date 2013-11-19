function [val1 val2 val3] = demo_dict(args)
% Demonstration of passing Python dictionary variables around
    val1 = args.pDict(1).apple;
    val2 = args.pDict(1).pear;
    val3 = args.pDict(1).banana;

end
