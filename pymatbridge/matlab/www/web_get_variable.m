function json_response = web_get_variable(headers, config)
% Reach into the current namespace get a variable in json format that can
% be returned as part of a response

response.success = 'false';

field_names = fieldnames(headers.Content);

%     URL decode the POST data
for i=1:numel(field_names)
    headers.Content.(field_names{i}) = urldecode(headers.Content.(field_names{i}));
end

response.content = '';

varname_check = false;
if size(field_names)
    if isfield(headers.Content, 'varname')
        varname_check = true;
    end
end

if ~varname_check
    response.message = 'No variable name provided as POST parameter';
    json_response = mat2json(response);
    return
end


varname = headers.Content.varname;

response.var = mat2json(evalin('base', varname));

json_response = mat2json(response);

return
end
