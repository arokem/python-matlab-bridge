function json_response = pymat_get_variable(req)
% Reach into the current namespace get a variable in json format that can
% be returned as part of a response

response.success = 'false';

field_names = fieldnames(req);

response.content = '';

varname_check = false;
if size(field_names)
    if isfield(req, 'varname')
        varname_check = true;
    end
end

if ~varname_check
    response.message = 'No variable name provided as input argument';
    json_response = json_dump(response);
    return
end


varname = req.varname;


% if the var doesn't exist in the workspace, inform adequately
expr = strcat('exist(''', varname, ''',''var'')');
var_exists = evalin('base', expr);
if ~var_exists
    response.exists = false;
    response.var = '';
else
    response.exists = true;
    response.var = evalin('base', varname);
end

json_response = json_dump(response);

return
end
