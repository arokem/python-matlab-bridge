function json_response = pymat_call(req)

    if ~isfield(req, 'func')
        response.message = 'No function given as func POST parameter';
        json_response = json.dump(response);
        return
    end

    if ~isfield(req, 'args')
        req.args = {}
    end

    func = str2func(req.func);
    if isfield(req, 'nout')
        nout = req.nout
    else
        try
            nout = min(abs(nargout(func)), 1);
        catch
            nout = 0;
        end
    end
   
    try
        switch nout
            case 0
                feval(func, req.args{:});
                response.result = true;
            case 1
                a = feval(func, req.args{:});
                response.result = a;
            case 2
                [a, b] = feval(func, req.args{:});
                response.result = {a, b};
            case 3
                [a, b, c] = feval(func, req.args{:});
                response.result = {a, b, c};
            case 4
                [a, b, c, d] = feval(func, req.args{:});
                response.result = {a, b, c, d};
            default
                % varargout or throw exception
                response.result = feval(func, req.args{:});
        end
        response.success = true;
        response.message = 'Successfully completed request';
    catch exception
        response.success = false;
        response.result  = exception.identifier;
        response.message = exception.message;
    end

    json_response = json.dump(response);
    return

end
