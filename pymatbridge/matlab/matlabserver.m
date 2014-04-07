function matlabserver(socket_address)
% This function takes a socket address as input and initiates a ZMQ session
% over the socket. I then enters the listen-respond mode until it gets an
% "exit" command

json.startup
messenger('init', socket_address);

while true
    % don't let any errors escape (and crash the server)
    try
        msg_in = messenger('listen');
        req = json.load(msg_in);

        switch(req.cmd)
            case {'connect'}
                messenger('respond', 'connected');

            case {'exit'}
                messenger('exit');
                clear mex;
                break;

            case {'call'}
                fhandle = str2func('pymat_call')
                resp = feval(fhandle, req)
                messenger('respond', resp)

            case {'eval'}
                fhandle = str2func('pymat_eval');
                resp = feval(fhandle, req);
                messenger('respond', resp);

            case {'get_var'}
                fhandle = str2func('pymat_get_variable');
                resp = feval(fhandle, req);
                messenger('respond', resp);

            otherwise
                messenger('respond', 'unrecognized command');
        end

    catch exception
        response.success = false;
        response.result  = exception.identifier;
        response.message = exception.message;

        json_response = json.dump(response);
        messenger('respond', 'json_response');
    end
end
