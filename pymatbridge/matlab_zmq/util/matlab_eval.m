function json_response = web_eval(headers, varargin);
%WEB_EVAL: Returns a json object of the result of calling the function
%
% json_response = WEB_EVAL(headers);
% json_response = WEB_EVAL(headers, config);
%
%   This allows you to run any matlab code. To be used with webserver.m.
%   HTTP POST to /web_eval.m with the following parameters:
%       code: a string which contains the code to be run in the matlab session
%
%   Should return a json object containing the result
%
% Based on Max Jaderberg's web_feval

response.success = 'false';
field_names = fieldnames(headers.Content);

% URL decode the POST data
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
	return;
end

code = headers.Content.code;

try
	% tempname is less likely to get bonked by another process.
	diary_file = [tempname() '_diary.txt'];
	diary(diary_file);
	evalin('base', code);
	diary('off');

	datadir = fullfile(tempdir(),'MatlabData');
	response.content.datadir = [datadir, filesep()];
	mkdir(datadir);

	fig_files = make_figs(datadir);

	response.success = 'true';
	response.content.figures = fig_files;

	% this will not work on Windows:
	%[ignore_status, stdout] = system(['cat ' diary_file]);
	% cf. http://rosettacode.org/wiki/Read_entire_file#MATLAB_.2F_Octave
	FID = fopen(diary_file,'r');
	if (FID > 0)
		[stdout,count] = fread(FID, [1,inf], 'uint8=>char');
		fclose(FID);
		response.content.stdout = stdout;
	else
		response.success = 'false';
		response.content.stdout = sprintf('could not open %s for read',diary_file);
	end
	delete(diary_file)
catch ME
	diary('off');
	response.success = 'false';
	response.content.stdout = ME.message;
end

response.content.code = code;

json_response = mat2json(response);

end %function
