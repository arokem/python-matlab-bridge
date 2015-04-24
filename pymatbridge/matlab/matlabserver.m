function matlabserver(socket_address)
% This function takes a socket address as input and initiates a ZMQ session
% over the socket. I then enters the listen-respond mode until it gets an
% "exit" command

json_startup
messenger('init', socket_address);

c=onCleanup(@()exit);

while(1)
    msg_in = messenger('listen');
    req = json_load(msg_in);

    switch(req.cmd)
        case {'connect'}
            messenger('respond', 'connected');

        case {'exit'}
            messenger('exit');
            break;

        case {'eval'}
            resp = pymat_eval(req);
            messenger('respond', resp);

        otherwise
            messenger('respond', 'i dont know what you want');
    end

end
