function matlabserver(socket_address)
% This function takes a socket address as input and initiates a ZMQ session
% over the socket. I then enters the listen-respond mode until it gets an 
% "exit" command

messenger('init', socket_address);

while(1)
    msg_in = messenger('listen');
    req = parse_json(msg_in);
    req = req{1};
    
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




