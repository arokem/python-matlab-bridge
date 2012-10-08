% web_eval
% Based on Max Jaderberg's web_feval


function json_response = web_eval(headers, config)
%WEB_FEVAL Returns a json object of the result of calling the function
%   This allows you to run any matlab code. To be used with webserver.m.
%   HTTP POST to /web_eval.m with the following parameters:
%       code: a string which contains the code to be run in the matlab session
%
%   Should return a json object containing the result

response.success = 'false';
field_names = fieldnames(headers.Content);

%     URL decode the POST data
for i=1:numel(field_names)
    headers.Content.(field_names{i}) = urldecode(headers.Content.(field_names{i}));
end

response.content = '';

code_check = false;
if size(field_names)
    if isfield(headers.Content, 'code')
        code_check = true;
    end
end

if ~code_check
    response.message = 'No code provided as POST parameter';
    json_response = mat2json(response);
    return
end

code = headers.Content.code;

try
    diary_file = [tempdir 'diary.txt'];
    diary(diary_file);
    evalin('base', code); 
    diary;
    response.success = 'true';
    response.content.code = code;
    [~, stdout] = system(['cat ' diary_file]);
    delete(diary_file)
    response.content.stdout = stdout; 
catch ME   
    response.success = 'false';
    response.content.stdout = ME.message;
    respone.content.code = code; 
end

json_response = mat2json(response);

return



end

