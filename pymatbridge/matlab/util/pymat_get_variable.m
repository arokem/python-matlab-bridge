function json_response = pymat_get_variable(req)
% Reach into the current namespace get a variable in json format that can
% be returned as part of a response

    try
        response.result  = evalin('base', req.varname);
        response.success = true;
    catch exception
        response.success = false;
        response.result  = exception.identifier;
        response.message = exception.message;
    end

    json_response = json.dump(response);
    return

end
