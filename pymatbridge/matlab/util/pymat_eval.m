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

response.success = true;
response.content = '';
response.result = '';

close all hidden;

try
	% tempname is less likely to get bonked by another process.
	diary_file = [tempname() '_diary.txt'];
	diary(diary_file);
		
	% Add function path to current path
	if req.dname
        addpath(req.dname);
    end

    if iscell(req.func_args)
        [resp{1:req.nargout}] = feval(req.func_name, req.func_args{:});
    else
    	[resp{1:req.nargout}] = feval(req.func_name, req.func_args);
    end

    if req.nargout == 1
        response.result = resp{1};
    else
        response.result = resp;
    end

	diary('off');

	datadir = fullfile(tempdir(),'MatlabData');
	response.content.datadir = [datadir, filesep()];
	if ~exist(datadir, 'dir')
        mkdir(datadir);
    end

	fig_files = make_figs(datadir);
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
		response.success = false;
		response.content.stdout = sprintf('could not open %s for read',diary_file);
	end
	delete(diary_file)
catch ME
	diary('off');
	response.success = false;
	response.content.stdout = ME.message;
end

json_response = json_dump(response);

end %function
