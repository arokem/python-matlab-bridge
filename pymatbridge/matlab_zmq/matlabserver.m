function matlabserver(socket_address)
% This function takes a socket address as input and initiates a ZMQ session
% over the socket. I then enters the listen-respond mode until it gets an
% "exit" command

json.startup
messenger('init', socket_address);

while(1)
    msg_in = messenger('listen');
    req = json.load(msg_in);

    switch(req.cmd)
        case {'connect'}
            messenger('respond', 'connected');
        case {'exit'}
            messenger('exit');
            clear mex;
            break;
        case {'run_function'}
            fhandle = str2func('matlab_feval');
            resp = feval(fhandle, req);

            messenger('respond', resp);
        case {'run_code'}
            % Not implemented yet
            resp = struct('success', 0);
            resp = mat2json(resp);
            messenger('respond', resp);
        otherwise
            messenger('respond', 'i dont know what you want');
    end

end
