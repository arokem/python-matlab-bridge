function webserver(varargin);
% WEBSERVER: a HTTP webserver for HTML code and images
%
% This function WEBSERVER, is a HTTP webserver for HTML code and images
% and also allows execution of Matlab code through the web.
%
%   webserver(port)
%
%   or
%   WEBSERVER(port)
%   WEBSERVER(config)
%   WEBSERVER(port,config)
%
%   port : A port nummer for instance 4000; defaults to 4000
%   config : A struct with config options
%     .www_folder         Folder with all html and other files, 'www';
%     .temp_folder        Folder to temporary store uploaded files, (default) 'www/temp';
%     .verbose            Display debug information, (default) true;
%     .defaultfile        If no file aksed display home page, (default) '/index.html';
%     .log_level          one of 'info','warning','error','critical','catastrophic'; less severe
%                          messages will not be logged. (default) 'warning'
%                          'catastrophic' means no logfile will be written.
%     .log_folder         where to put logs; (default) 'www/log';
%     .timeout            a timeout, in days. if no request is received within
%                          this many days of the last request, the server shuts
%                          down. default inf for backwards compatibility.
%
% Supports
%   - HTML and images
%   - Sub-Folders
%   - Upload files
%   - M file execution
%
% Example,
%  webserver(4000);
%  % Use firefox or internet explorer and visit http://localhost:4000/
%
% Exampe 2,
%  webserver(4000,struct('verbose',false))
%
% nb. to prevent rampant misuse of compute cycles and ports, we write a
% sentinel file in tempdir() of the form matlab_webserver_portnum.lock
% and attempt to delete it when done.
%
% Function is written by D.Kroon University of Twente (November 2010)

% Config of the HTTP server
close all;

% make file locations relative to 'here', the directory
% containing webserver.m
my_filename = mfilename('fullpath');
my_dir = fileparts(my_filename);

% more flexible input parsing%FOLDUP
p = inputParser;

p.addOptional('port',4000,@(x)(isnumeric(x) && isscalar(x) && (x > 999) && (floor(x) == x)));

p.addOptional('www_folder',fullfile(my_dir,'www'),@ischar);
p.addOptional('temp_folder',fullfile(my_dir,'www','temp'),@ischar);
p.addOptional('verbose',true,@islogical);
p.addOptional('defaultfile',[filesep(),'index.html'],@ischar);
p.addOptional('log_level','default',...
	@(x)(ischar(x) && ismember(lower(x),{'info','warning','error','critical','catastrophic','default'})));
p.addOptional('log_folder',fullfile(my_dir,'www','log'),@ischar);
p.addOptional('timeout',inf,@(x)(isnumeric(x) && (x > 0)))

% these are not publicized:
p.addOptional('mtime1',0.8,@(x)(isnumeric(x) && isscalar(x) && x > 0));
p.addOptional('mtime2',3.0,@(x)(isnumeric(x) && isscalar(x) && x > 0));

% parse it
p.parse(varargin{:});

% get results
config = p.Results;
port = config.port;
%UNFOLD

% logging%FOLDUP
persistent log_levels;

if (isempty(log_levels))
	log_levels = struct('info',0,'warning',1,'error',2,'critical',3,'catastrophic',inf);
	log_levels.default = log_levels.warning;
end
% it is convenient to store them here, rather than have log_levels be global
config.log_levels = log_levels;

% make the log_folder
if (isempty(dir(config.log_folder)))
	warning('webserver:directoryNotFound','directory %s was not found; will mkdir.',config.log_folder);
	try
		mkdir(config.log_folder);
	end
end

% open the log file
if ~isinf(log_levels.(config.log_level))
	config.logfile = fullfile(config.log_folder,sprintf('webserver_%d_%s.log',port,datestr(now(),'yyyymmddTHHMMSSFFF')));
	try
		config.log_FID = fopen(config.logfile,'w');
		if (config.verbose)  % ack! multiple log streams!
			if (config.log_FID > 0)
				fprintf(1,'logging to %s\n',config.logfile);
			else
				fprintf(2,'problem logging to %s\n',config.logfile);
			end
		end
	catch
		config.log_level = 'catastrophic';
		% you're on your own, son.
		fprintf(2,'problem logging to %s; no logging will be done.\n',config.logfile);
	end
end
%UNFOLD

% check the www folder%FOLDUP
if (isempty(dir(config.www_folder)))
	warning('webserver:directoryNotFound','directory %s was not found',config.www_folder);
	log_it(config,'warning','directory %s was not found',config.www_folder);
	% proceed, but probably something will barf.
end%UNFOLD

% make the temp_folder%FOLDUP
if (isempty(dir(config.temp_folder)))
	warning('webserver:directoryNotFound','directory %s was not found; will mkdir.',config.temp_folder);
	log_it(config,'warning','directory %s was not found; will mkdir.',config.temp_folder);
	try
		mkdir(config.temp_folder);
	catch
		log_it(config,'error','directory %s was not found; will mkdir.',config.temp_folder);
	end
end%UNFOLD

% Open a TCP Server Port
try
	TCP = JavaTcpServer('initialize',[],port,config);
catch
	% barf
	log_it(config,'critical','error initializing TCP server: %s',lasterr)
	cleanup(config);
	return;
end

if (config.verbose)
	fprintf(1,'Webserver available on http://localhost:%d/\nVisit http://localhost:%d/exit.m to shut down\n',port,port);
end

log_it(config,'info','Webserver available on http://localhost:%d/\nVisit http://localhost:%d/exit.m to shut down\n',port,port);

log_it(config,'info','starting main loop')

% termination conditions
last_request = now();
timed_out = (now() - last_request) > config.timeout;
exit_server = false;

try
	while (~(timed_out || exit_server))%FOLDUP
		touch_sentinel(config);

		% Wait for connections of browsers
		TCP=JavaTcpServer('accept',TCP,[],config);

		% If socket is -1, the user has close the "Close Window"
		if(TCP.socket==-1), break, end

		% Read the data form the browser as an byte array of type int8

		[TCP,requestdata]=JavaTcpServer('read',TCP,[],config);
		if(isempty(requestdata))
			timed_out = (now() - last_request) > config.timeout;
			continue;
		end
		last_request = now();

		if(config.verbose), disp(char(requestdata(1:min(1000,end)))); end

		log_it(config,'info','%s\n',char(requestdata));

		% Convert the Header text to a struct
		request = text2header(requestdata,config);
		if(config.verbose), disp(request); end

		% The filename asked by the browser
		if(isfield(request,'Get'))
			filename=request.Get.Filename;
		elseif(isfield(request,'Post'))
			filename=request.Post.Filename;
		else
			warning('webserver:badRequest','Unknown Type of Request');
			log_it(config,'warning','bad request?');
			continue;
		end

		log_it(config,'info','requesting %s',filename);

		% If no filename, use default
		if (strcmp(filename,'/')), filename=config.defaultfile; end

		% put special magic here to detect exit.m
		% so that we can properly shut down the server.
		% anything else is a hack.
		exit_server = (strcmp(filename,'/exit.m'));

		if (exit_server)%FOLDUP
			found = true;
			html = sprintf('<html><body><font color="#FF0000">shutting down server at %d</font><br><br></body></html>',port);
			header = make_html_http_header(html,found);
			response = header2text(header);
			% 2FIX: is it possible the webserver will terminate without this message
			% being returned? do we have to be persistent?
		%UNFOLD
		else%FOLDUP
			% Make the full filename inluding path
			fullfilename=[config.www_folder filename];
			[pathstr,name,ext] = fileparts(fullfilename);

			% Check if file asked by the browser can be opened
			fid = fopen(fullfilename, 'r');
			found = fid > 0;
			if (fid<0)
				log_it(config,'warning','could not open file %s',fullfilename);
				filename='/404.html';
				% 2FIX: if this is not found, fallback to a dynamic 404?
				fullfilename=[config.www_folder filename];
			else
				fclose(fid);  % won't this barf if fid < 0?
			end

			log_it(config,'info','writing to %s',fullfilename);

			% Based on the extention asked, read a local file and parse it.
			% or execute matlab code, which generates the file
			switch(ext)%FOLDUP
			case {'.m'}
				fhandle = str2func(name);
				try
					html=feval(fhandle,request,config);
				    disp('hey Im here!');
                    disp(html);
                catch ME
					html=['<html><body><font color="#FF0000">Error in file : ' name ...
					'.m</font><br><br><font color="#990000"> The file returned the following error: <br>' ...
					ME.message '</font></body></html>'];
					fprintf(ME.message);
					log_it(config,'error','file returned error %s',ME.message);
				end
				header=make_html_http_header(html,found);
				response=header2text(header);
			case {'.html','.htm'}
				fid = fopen(fullfilename, 'r');
				html = fread(fid, inf, 'int8')';
				fclose(fid);
				header=make_html_http_header(html,found);
				response=header2text(header);
			case {'.jpg','.png','.gif','.ico'}
				fid = fopen(fullfilename, 'r');
				html = fread(fid, inf, 'int8')';
				fclose(fid);
				header=make_image_http_header(html,found);
				% the wrong ContentTypes. bleah.
				switch ext
				case {'.ico'}
					header.ContentType = 'image/vnd.microsoft.icon';
				otherwise
					header.ContentType = sprintf('image/%s',ext(2:end));
				end
				response=header2text(header);
			otherwise
				fid = fopen(fullfilename, 'r');
				html = fread(fid, inf, 'int8')';
				fclose(fid);
				header=make_bin_http_header(html,found);
				response=header2text(header);
			end%UNFOLD
		end%UNFOLD

		if(config.verbose), disp(char(response)); end

		log_it(config,'info','%s\n%s\n%s',response,char(html),repmat('#',1,72));

		% Give the generated HTML or binary code back to the browser
		JavaTcpServer('write',TCP,int8(response),config);
		JavaTcpServer('write',TCP,int8(html),config);
	end%UNFOLD

	% 2FIX: should closing the TCP connection be part of cleanup?
	try
		JavaTcpServer('close',TCP);
	catch
		% barf
		log_it(config,'critical','error closing TCP server: %s',lasterr)
	end

	log_it(config,'info','finished main loop')
catch ME
	log_it(config,'error','some uncaught error: %s',ME.message);
	cleanup(config);
	return;
end

cleanup(config);

end %function
function log_it(config,severity,varargin)%FOLDUP
% log the message sprintf(varargin{:})
% if the configured log_level is <= the severity
% except when the log_level is 'catastrophic',
% in which case no logging is ever done.

try
	if (~ (config.log_levels.(config.log_level) > config.log_levels.(severity)))
		fprintf(config.log_FID,'%s:%s\n',datestr(now(),'yyyy-mm-ddTHH:MM:SS.FFF'),sprintf(varargin{:}));
	end
catch ME
	% ack!
	fprintf(2,'logging error: %s\n',ME.message);
end

end %function%UNFOLD
function cleanup(config);%FOLDUP

try
	fclose(config.log_FID);
end

try
	fname = touch_sentinel(config);
	delete(fname);
end

end %function%UNFOLD
function fname = touch_sentinel(config);%FOLDUP

try
	fname = fullfile(tempdir(),sprintf('matlab_webserver_%d.lock',config.port));
	FID = fopen(fname,'w');
	if (FID > 0)
		fclose(fopen(fname,'w'));
	else
		log_it(config,'warning','some problem touching sentinel file %s',fname);
	end
catch ME
	log_it(config,'error','some uncaught error: %s',ME.message);
end

end %function%UNFOLD
%#ok<*WNTAG,*CTCH,*NOSEM,*LERR,*TRYNC> 			%for matlab mlint; look away.
%for vim modeline: (do not edit)
% vim:ts=2:fdm=marker:fmr=FOLDUP,UNFOLD:cms=%%s:syntax=matlab:filetype=matlab
