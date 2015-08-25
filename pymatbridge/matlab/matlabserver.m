function matlabserver(socket_address, exit_when_done)
%MATLABSERVER   Take Commands from Python via ZMQ
% matlabserver(socket_address, exit_when_done)
% This function takes a socket address as input and initiates a ZMQ session
% over the socket. It then enters the listen-respond mode until it gets an
% "exit" command, at which point it returns (or exits if exit_when_done), or
% until it gets a "separate" command, at which point it launches the MATLAB
% desktop client and returns.
%

initialize_environment;
json_startup;
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

        case {'separate'}
            desktop; %no-op if desktop is already up
            c = onCleanup(@stop_messenger);
            break;

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

function initialize_environment()
    if ~exist('json_startup', 'file')
        [pathstr, ~, ~] = fileparts(mfilename('fullpath'));
        old_warning_state = warning('off','all');
        addpath(genpath(pathstr));
        warning(old_warning_state);
    end
end
