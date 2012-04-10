function webserver(port,config)
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

defaultoptions=struct('www_folder','www','temp_folder','www/temp','verbose',true,'defaultfile','/index.html','mtime1',0.8,'mtime2',3);

if(~exist('config','var')), config=defaultoptions;
else
    tags = fieldnames(defaultoptions);
    for i=1:length(tags),
        if(~isfield(config,tags{i})), config.(tags{i})=defaultoptions.(tags{i}); end
    end
    if(length(tags)~=length(fieldnames(config))),
        warning('image_registration:unknownoption','unknown options found');
    end
end


% Use Default Server Port, if user input not available
if(nargin<1), port=4000; end

% Add sub-functions to Matlab Search Path
add_function_paths();

% Open a TCP Server Port
TCP=JavaTcpServer('initialize',[],port,config);

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
            addpath(pathstr)
            fhandle = str2func(name);
            try
            html=feval(fhandle,request,config);
            catch ME
                html=['<html><body><font color="#FF0000">Error in file : ' name ...
                    '.m</font><br><br><font color="#990000"> The file returned the following error: <br>' ...
                    ME.message '</font></body></html>'];
                fprintf(ME.message);
            end
            rmpath(pathstr)
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


function add_function_paths()
try
    functionname='webserver.m';
    functiondir=which(functionname);
    functiondir=functiondir(1:end-length(functionname));
    addpath([functiondir '/functions'])
catch me
    disp(me.message);
end








