function json_response = pymat_eval(req);
% PYMAT_EVAL: Returns a json object of the result of calling the function
%
% json_response = pymat_eval(req);
%
%   This allows you to run any matlab code. req should be a struct with the
%   following fields:
%       code: a string which contains the code to be run in the matlab session
%
%   Should return a json object containing the result.
%
% Based on Max Jaderberg's web_feval

response.success = 'false';
field_names = fieldnames(req);

response.content = '';

code_check = false;
if size(field_names)
	if isfield(req, 'code')
		code_check = true;
	end
end

if ~code_check
	response.message = 'No code provided as POST parameter';
	json_response = json_dump(response);
	return;
end

code = req.code;

try
	% tempname is less likely to get bonked by another process.
	diary_file = [tempname() '_diary.txt'];
	diary(diary_file);
	evalin('base', code);
	diary('off');

	datadir = fullfile(tempdir(),'MatlabData');
	response.content.datadir = [datadir, filesep()];
	if ~exist(datadir, 'dir')
        mkdir(datadir);
    end

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

json_response = json_dump(response);

end %function
