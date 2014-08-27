% Max Jaderberg 2011

function json_response = pymat_feval(req)

    response.success = 'false';
    field_names = fieldnames(req);

    response.result = '';

    func_path_check = false;
    arguments_check = false;
    if size(field_names)
        if isfield(req, 'func_path')
            func_path_check = true;
        end
        if isfield(req, 'func_args')
            arguments_check = true;
        end
    end

    if ~func_path_check
        response.message = 'No function given as func_path POST parameter';
        json_response = json_dump(response);
        return
    end

    func_path = req.func_path;
    if arguments_check
        arguments = req.func_args;
    else
        arguments = '';
    end

    response.result = run_dot_m(func_path, arguments);
    response.success = 'true';
    response.message = 'Successfully completed request';

    json_response = json_dump(response);

    return

end
