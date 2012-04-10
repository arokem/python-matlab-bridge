function subdata=multipart2struct(subrequestdata,config)
request_text=char(subrequestdata);
request_lines = regexp(request_text, '\n+', 'split');
request_words = regexp(request_lines, '\s+', 'split');

i=1;
subdata=struct;
subdata.Name='';
subdata.Filename='';
subdata.ContentType='';
subdata.ContentData='';
while(true)
    i=i+1; if((i>length(request_lines))||(uint8(request_lines{i}(1)==13))), break; end
    line=request_lines{i};
    type=request_words{i}{1};
    switch(type)
        case 'Content-Disposition:'
            for j=3:length(request_words{i})
                line_words=regexp(request_words{i}{j}, '"', 'split');
                switch(line_words{1})
                    case 'name='
                        subdata.Name=line_words{2};
                    case 'filename='
                        subdata.Filename=line_words{2};
                end
            end
        case 'Content-Type:'
             subdata.ContentType=rmvp(line(15:end));
    end
end
w=find(subrequestdata==10);
switch(subdata.ContentType) 
    case ''
        subdata.ContentData=char(subrequestdata(w(i)+1:end));
    otherwise
        subdata.ContentData=subrequestdata(w(i)+1:end);
        [pathstr,name,ext] = fileparts(subdata.Filename);
        filename=['/' char(round(rand(1,32)*9)+48)];
        fullfilename=[config.temp_folder filename ext];
        fid = fopen(fullfilename,'w'); fwrite(fid,subdata.ContentData,'int8'); fclose(fid);
        subdata.Filename=fullfilename;
end
