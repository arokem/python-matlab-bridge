function json_response = pymat_eval(req);
% PYMAT_EVAL: Returns a json object of the result of calling the function
%
% json_response = pymat_eval(req);
%
%   This allows you to run any matlab code. req should be a struct with the
%   following fields:
%       dname: The name of a directory to add to the runtime path before attempting to run the code.
%       func_name: The name of a function to invoke.
%       func_args: An array of arguments to send to the function.
%       nargout: An int specifying how many output arguments are expected.
%
%   Should return a json object containing the result.
%
% Based on Max Jaderberg's web_feval

response.success = true;
response.content = '';
response.result = '';
response.stack = {};

close all hidden;

try
	% tempname is less likely to get bonked by another process.
	diary_file = [tempname() '_diary.txt'];
	diary(diary_file);
		
	% Add function path to current path
	if req.dname
        addpath(req.dname);
    end

    % force a rehash of user functions
    rehash

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

  % Retrieve the stack trace.
  if ~exist('OCTAVE_VERSION', 'builtin');
    % For MATLAB, just grab it off the exception.
    response.stack = ME.stack;
  else
    % Octave exceptions don't seem to have a 'stack' field, so we use lasterror
    % instead. lasterror exists in MATLAB too, but it doesn't seem to return
    % the correct stack trace in this case.
    err = lasterror();
    stack = err.stack;

    % Strip off fields that aren't available on MException.
    stack = rmfield(stack, {'column', 'context', 'scope'});

    % The 'name' fields here look like 'foo>bar' in Octave, where foo is the
    % outermost calling function, and bar is the current function. With
    % MException there's only 'bar' so let's strip off the 'foo>'.

    % n.b. strsplit doesn't work in Octave when the delimiter is < or >.
    % This bug is fixed in Octave 4.0 (http://savannah.gnu.org/bugs/?44641)
    % but we support 3.8, so we use the regex mode as a workaround.
    for i = 1:numel(stack)
      name = stack(i).name;
      name = strsplit(name, '>', 'delimitertype', 'regularexpression');
      stack(i).name = name{end};
    end

    response.stack = stack;
  end

  % Strip off the last two frames -- these correspond to pymat_eval and
  % matlabserver, which we don't want to expose.
  response.stack = response.stack(1:end-2, :);

  % FIXME: The stack is returned as a nx1 struct array, and in Octave json_dump
  % throws an error trying to serialize it. Let's just transpose it for now.
  response.stack = response.stack';
  % FIXME: json_dump loops infinitely if this is a 1x0 struct array, so
  % let's just turn it back into an empty array if so.
  if ndims(response.stack) == 2 && ...
    size(response.stack, 1) == 1 && ...
    size(response.stack, 2) == 0
    response.stack = {};
  end
end

json_response = json_dump(response);

end %function
