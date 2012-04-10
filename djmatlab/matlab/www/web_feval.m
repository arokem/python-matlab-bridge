% Max Jaderberg 2011

function json_response = web_feval(headers, config)
%WEB_FEVAL Returns a json object of the result of calling the funciton
%   This allows you to run any local matlab file. To be used with webserver.m. 
%   HTTP POST to /web_feval.m with the following parameters:
%       func_path: a string which is the path to the .m file you want to
%       call
%       arguments: a json string of the arguments structure to pass to the
%       function you are calling
% 
%   Returns a json object containing the result

    response.success = 'false';
    field_names = fieldnames(headers.Content);
    
%     URL decode the POST data
    for i=1:numel(field_names)
        headers.Content.(field_names{i}) = urldecode(headers.Content.(field_names{i}));
    end
    
    response.content = '';
    
    func_path_check = false;
    arguments_check = false;
    if size(field_names)
        if isfield(headers.Content, 'func_path')
            func_path_check = true;
        end
        if isfield(headers.Content, 'arguments')
            arguments_check = true;
        end
    end
    
    if ~func_path_check
        response.message = 'No function given as func_path POST parameter';
        json_response = mat2json(response);
        return
    end
    
    func_path = headers.Content.func_path;
    
    if arguments_check
        arguments = json2mat(headers.Content.arguments);
    else
        arguments = '';
    end
    
    response.result = run_dot_m(func_path, arguments);
    response.success = 'true';
    response.message = 'Successfully completed request';

    response.content.func_path = func_path;
    response.content.arguments = arguments;
    
    json_response = mat2json(response);
        
    return
    
    
    
end

