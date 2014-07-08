function matlabserver(socket_address)
% MATLABSERVER Run a Matlab server to handle requests from Python over ZMQ
%
% MATLABSERVER(SOCKET_ADDRESS) initiates a ZMQ session over the provided
% SOCKET_ADDRESS. Once started, it executes client requests and returns
% the response.
%
% The recognized requests are:
%   'ping': Elicit a response from the server
%   'exit': Request the server to shutdown
%   'call': Call a Matlab function with the provdided arguments

    json.startup
    messenger('init', socket_address);

    while true
        % don't let any errors escape (and crash the server)
        try
            msg_in = messenger('listen');
            req = json.load(msg_in);

            switch(req.cmd)
                case {'ping'}
                    messenger('respond', 'pong');

                case {'exit'}
                    messenger('exit');
                    clear mex;
                    break;

                case {'call'}
                    resp = call(req);
                    json_resp = json.dump(resp);
                    messenger('respond', json_resp);

                otherwise
                    throw(MException('MATLAB:matlabserver', ['Unrecognized command ' req.cmd]))
            end

        catch exception
            % format the exception and pass it back to the client
            resp.success = false;
            resp.result  = exception.identifier;
            resp.message = getReport(exception)

            json_resp = json.dump(resp);
            messenger('respond', json_resp);
        end
    end
end


function resp = call(req)
% CALL Call a Matlab function
%
% RESPONSE = CALL(REQUEST) calls Matlab's FEVAL function, intelligently
% handling the number of input and output arguments so that the argument
% spec is satisfied.
%
% The REQUEST is a struct with three fields:
%   'func': The name of the function to execute
%   'args': A cell array of args to expand into the function arguments
%   'nout': The number of output arguments requested

    % function of no arguments
    if ~isfield(req, 'args')
        req.args = {}
    end

    % determine the number of output arguments
    % TODO: What should the default behaviour be?
    func = str2func(req.func);
    nout = req.nout;
    [saveout nsaveout] = regexp(req.saveout, '(?:;)+', 'split', 'match');
    if isempty(nout)
        try
            nout = min(abs(nargout(func)), 1);
        catch
            nout = 1;
        end
    end

    % call the function, taking care of broadcasting outputs
    switch nout
        case 0
            func(req.args{:});
        case 1
            resp.result = func(req.args{:});
        otherwise
            [resp.result{1:nout}] = func(req.args{:});
    end

    if length(nsaveout)
        if nout == 1
            assignin('base',saveout{1},resp.result);
            resp.result = ['__VAR=' saveout{1} '|' class(resp.result)];
        elseif nout > 1
            tmp_result = '';
            for i=1:nout
                assignin('base',saveout{i},resp.result{i});
                tmp_result = ['__VAR=' saveout{i} '|' class(resp.result{i}) ';' tmp_result];
            end
            resp.result = tmp_result;
        end
    end

    % build the response
    resp.success = true;
    resp.message = 'Successfully completed request';
end
