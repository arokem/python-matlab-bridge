function header = text2header(requestdata,config)
request_text=char(requestdata);
request_lines = regexp(request_text, '\r\n+', 'split');
request_words = regexp(request_lines, '\s+', 'split');
for i=1:length(request_lines)
    line=request_lines{i};
    if(isempty(line)), break; end
    type=request_words{i}{1};
    switch(lower(type))
        case 'get'
            header.Get.Filename=request_words{i}{2};
            header.Get.Protocol=request_words{i}{3};
        case 'post'
            header.Post.Filename=request_words{i}{2};
            header.Post.Protocol=request_words{i}{3};
        case 'host:'
            header.Host=rmvp(line(7:end));
        case 'user-agent:'
            header.UserAgent=rmvp(line(13:end));
        case 'accept:'
            header.Accept=rmvp(line(9:end));
        case 'accept-language:'
            header.AcceptLanguage=rmvp(line(18:end));
        case 'accept-encoding:'
            header.AcceptEncoding=rmvp(line(18:end));
        case 'accept-charset:'
            header.AcceptCharset=rmvp(line(17:end));
        case 'keep-alive:'
            header.KeepAlive=rmvp(line(13:end));
        case 'connection:'
            header.Connection=rmvp(line(13:end));
        case 'content-length:'
            header.ContentLength=rmvp(line(17:end));
        case 'content-type:'
            %lines=rmvp(line(15:end));
            switch rmvp(request_words{i}{2})
                case {'application/x-www-form-urlencoded','application/x-www-form-urlencoded;'}
                    header.ContentType.Type='application/x-www-form-urlencoded';
                    header.ContentType.Boundary='&';
                case {'multipart/form-data','multipart/form-data;'}
                    header.ContentType.Type='multipart/form-data';
                    str=request_words{i}{3};
                    header.ContentType.Boundary=str(10:end);
                otherwise
                    disp('unknown')
            end
        otherwise
    end
end
header.Content=struct;
if(isfield(header,'ContentLength'))
    cl=str2double(header.ContentLength);
    str=request_text(end-cl+1:end);
    data=requestdata(end-cl+1:end);
    if(~isfield(header,'ContentType'))
        header.ContentType.Type=''; header.ContentType.Boundary='&';
    end
    switch (header.ContentType.Type)
        case {'application/x-www-form-urlencoded',''}
            str=rmvp(str);
            words = regexp(str, '&', 'split');
            for i=1:length(words)
                words2 = regexp(words{i}, '=', 'split');
                header.Content.(words2{1})=words2{2};
            end
        case 'multipart/form-data'
            pos=strfind(str,header.ContentType.Boundary);
            while((pos(1)>1)&&(str(pos(1)-1)=='-'))
                header.ContentType.Boundary=['-' header.ContentType.Boundary];
                pos=strfind(str,header.ContentType.Boundary);
            end
            
            for i=1:(length(pos)-1)
                pstart=pos(i)+length(header.ContentType.Boundary);
                pend=pos(i+1)-3; % Remove "13 10" End-line characters
                subrequestdata=data(pstart:pend);
                subdata= multipart2struct(subrequestdata,config);
                header.Content.(subdata.Name).Filename=subdata.Filename;
                header.Content.(subdata.Name).ContentType=subdata.ContentType;
                header.Content.(subdata.Name).ContentData=subdata.ContentData;
            end
        otherwise
            disp('unknown')
    end
end