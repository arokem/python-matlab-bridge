function matlabserver(socket_address, exit_when_done)
%MATLABSERVER   Take Commands from Python via ZMQ
% This function takes a socket address as input and initiates a ZMQ session
% over the socket. I then enters the listen-respond mode until it gets an
% "exit" command

json_startup
messenger('init', socket_address);

if nargin > 1 && exit_when_done
    c = onCleanup(@stop_messenger_and_exit);
else
    c = onCleanup(@stop_messenger);
end

while(1)
    msg_in = messenger('listen');
    req = json_load(msg_in);

    switch(req.cmd)
        case {'connect'}
            messenger('respond', 'connected');

        case {'exit'}
            break;

        case {'eval'}
            resp = pymat_eval(req);
            messenger('respond', resp);

        otherwise
            messenger('respond', 'i dont know what you want');
    end

end

end %matlabserver

function stop_messenger_and_exit()
    messenger('exit');
    exit;
end

function stop_messenger()
    messenger('exit');
end
