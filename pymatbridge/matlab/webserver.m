function webserver(varargin);
% RUN javaaddpath('mongo-2.7.2.jar')
% This function WEBSERVER, is a HTTP webserver for HTML code and images
% and also allows execution of Matlab code through the web.
%
%   webserver(port)
% 
%   or
%
%   webserver(port,config)
%
%   port : A port nummer for instance 4000
%   (optional)
%   config : A struct with config options
%   config.www_folder : Folder with all html and other files, 'www';
%   config.temp_folder : Folder to temporary store uploaded files, (default) 'www/temp';
%   config.verbose : Display debug information, (default) true;
%   config.defaultfile : If no file aksed display home page, (default) '/index.html';
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
% Function is written by D.Kroon University of Twente (November 2010)

% Config of the HTTP server
close all;

% make file locations relative to 'here', the directory
% containing webserver.m
my_filename = mfilename('fullpath');
my_dir = fileparts(my_filename);

% more flexible input parsing
p = inputParser;

p.addOptional('port',4000,@(x)(isnumeric(x) && isscalar(x) && (x > 999) && (floor(x) == x)));

p.addOptional('www_folder',fullfile(my_dir,'www'),@ischar);
p.addOptional('temp_folder',fullfile(my_dir,'www','temp'),@ischar);
p.addOptional('verbose',true,@islogical);
p.addOptional('defaultfile',[filesep(),'index.html'],@ischar);
% these are not publicized:
p.addOptional('mtime1',0.8,@(x)(isnumeric(x) && isscalar(x) && x > 0));
p.addOptional('mtime2',3.0,@(x)(isnumeric(x) && isscalar(x) && x > 0));

% parse it
p.parse(varargin{:});

% get results
config = p.Results;
port = config.port;

fprintf(2,'the pwd is %s\n',pwd());

% check the www folder
if (isempty(dir(config.www_folder)))
	warning('webserver:directoryNotFound','directory %s was not found',config.www_folder);
	% proceed, but probably something will barf.
end

% make the temp_folder
if (isempty(dir(config.temp_folder)))
	warning('webserver:directoryNotFound','directory %s was not found; will mkdir.',config.temp_folder);
	try
		mkdir(config.temp_folder);
	end
end

% Open a TCP Server Port
TCP = JavaTcpServer('initialize',[],port,config);

if(config.verbose)
    disp(['Webserver Available on http://localhost:' num2str(port) '/']);
end

while(true)
    % Wait for connections of browsers
    TCP=JavaTcpServer('accept',TCP,[],config);
    
    % If socket is -1, the user has close the "Close Window"
    if(TCP.socket==-1), break, end
    
    % Read the data form the browser as an byte array of type int8
    
    [TCP,requestdata]=JavaTcpServer('read',TCP,[],config);
    if(isempty(requestdata))
        continue;
    end
    
    if(config.verbose), disp(char(requestdata(1:min(1000,end)))); end
    
    % Convert the Header text to a struct
    request = text2header(requestdata,config);
    if(config.verbose), disp(request); end
    
    % The filename asked by the browser
    if(isfield(request,'Get'))
        filename=request.Get.Filename;
    elseif(isfield(request,'Post'))
        filename=request.Post.Filename;
    else
        warning('Unknown Type of Request');
        continue
    end
    
    % If no filename, use default
    if(strcmp(filename,'/')), filename=config.defaultfile; end
    
    % Make the full filename inluding path
    fullfilename=[config.www_folder filename];
    [pathstr,name,ext] = fileparts(fullfilename);
    
    % Check if file asked by the browser can be opened
    fid = fopen(fullfilename, 'r');
    if(fid<0)
        filename='/404.html'; found=false;
        fullfilename=[config.www_folder filename]; 
    else
        found=true; fclose(fid);
    end
    
    % Based on the extention asked, read a local file and parse it.
    % or execute matlab code, which generates the file
    switch(ext)
        case {'.m'}
            fhandle = str2func(name);
            try
            html=feval(fhandle,request,config);
            catch ME
                html=['<html><body><font color="#FF0000">Error in file : ' name ...
                    '.m</font><br><br><font color="#990000"> The file returned the following error: <br>' ...
                    ME.message '</font></body></html>'];
                fprintf(ME.message);
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
            response=header2text(header);
        otherwise
            fid = fopen(fullfilename, 'r');
            html = fread(fid, inf, 'int8')';
            fclose(fid);
            header=make_bin_http_header(html,found);
            response=header2text(header);
    end
    
    if(config.verbose), disp(char(response)); end
    
    % Give the generated HTML or binary code back to the browser
    JavaTcpServer('write',TCP,int8(response),config);
    JavaTcpServer('write',TCP,int8(html),config);
end

JavaTcpServer('close',TCP);

end %function
