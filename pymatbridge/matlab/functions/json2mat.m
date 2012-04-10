function M=json2mat(J)

%JSON2MAT converts a javscript data object (JSON) into a Matlab structure
%         using s recursive approach. J can also be a file name.
%
%Example: lala=json2mat('{lele:2,lili:4,lolo:[1,2,{lulu:5,bubu:[[1,2],[3,4],[5,6]]}]}') 
%         notice lala.lolo{3}.bubu is read as a 2D matrix.
%
% Jonas Almeida, March 2010

if exist(J)==2 % if J is a filename
    fid=fopen(J,'r');
    J='';
    while ~feof(fid)
        J=[J,fgetl(fid)];
    end
    fclose(fid);
    M=json2mat(J);  
else
    J1=regexprep(J(1:min([5,length(J)])),'\s',''); %despaced start of J string
    if J1(1)=='{' %extract structures
        JJ=regexp(J,'\{(.*)\}','tokens');
        M=extract_struct(JJ{1}{1});
    elseif J1(1)=='[' %extract cells
        JJ=regexp(J,'\[(.*)\]','tokens');
        M=extract_cell(JJ{1}{1});
    elseif J1(1)=='"' %literal string
        JJ=regexp(J,'\"(.*)\"','tokens');
        M=JJ{1}{1};
    else %numeric value
        M=str2num(J); % is number
    end
end

function y=extract_struct(x)
%detag arrays first
indOC=extract_embed(x,'[',']');
n=size(indOC,1);
for i=n:-1:1
    tag{i}=json2mat(x(indOC(i,1):indOC(i,2)));
    x=[x(1:indOC(i,1)-1),'tag{',num2str(i),'}',x(indOC(i,2)+1:end)];
end


a=regexp(x,'[^:,]+:[^,]+');
n=length(a);
a=[a,length(x)+2];
for i=1:n
    s=x(a(i):a(i+1)-2);
    t=regexp(s,'([^:]+):(.+)','tokens');
    %t{1}{1}(t{1}{1}==32)=[]; % remove blanks, maybe later do something fancier like replace with underscores
    t{1}{1}=strrep(t{1}{1},' ','_');
    t{1}{1}=strrep(t{1}{1},'"','');
    if t{1}{1}(1)=='_' %JSON allows for fieldnames starting with "_"
        t{1}{1}(1)=''; % this line will cause hard to track problems if the same object has 2 attributes with the same name but one of them starting with "_"
    end        
    if regexp(t{1}{2},'tag{\d+}')
        y.(t{1}{1})=eval(t{1}{2});
    else
        y.(t{1}{1})=json2mat(t{1}{2});
    end
    %y.(t{1}{1})=json2mat(t{1}{2});
end

function y=extract_cell(x)

indOC=extract_embed(x,'{','}');
n=size(indOC,1);
for i=n:-1:1
    tag{i}=json2mat(x(indOC(i,1):indOC(i,2)));
    x=[x(1:indOC(i,1)-1),'tag~<',num2str(i),'>~',x(indOC(i,2)+1:end)];
end
indOC=extract_embed(x,'[',']');
m=size(indOC,1);
for j=m:-1:1
    i=n+j;
    tag{i}=json2mat(x(indOC(i,1):indOC(i,2)));
    try;tag{i}=cell2mat(tag{i});end
    x=[x(1:indOC(i,1)-1),'tag{',num2str(i),'}',x(indOC(i,2)+1:end)];
end
x=strrep(x,'~<','{');
x=strrep(x,'>~','}');
if exist('tag') %catching numeric content
    if isnumeric([tag{:}])
        try
            y=eval(['[',strrep(x,'},','};'),']']);
        end
    end
end

if exist('y')~=1
    y=eval(['{',strrep(x,'"',''''),'}']);
end

%look for embeded objects and arrays

function y=extract_embed(x,tagOpen,tagClose)

%EXTRACT_EMBED identifies embeded tagged segments
%Example y=extract_embed(str,'[',']')

indOpen=strfind(x,tagOpen)';
indOpen=[indOpen,ones(length(indOpen),1)];
indClose=strfind(x,tagClose)';
indClose=[indClose,-ones(length(indClose),1)];
indOpenClose=[indOpen;indClose];
[~,Ind]=sort(indOpenClose(:,1));
indOpenClose=indOpenClose(Ind,:);
n=size(indOpenClose,1);
for i=2:n % add one for open, take one for close
    indOpenClose(i,2)=indOpenClose(i-1,2)+indOpenClose(i,2);
end
i=0;
op=0; %open
while i<n
    i=i+1;
    if (indOpenClose(i,2)==1)*(op==0)
        op=1;
    elseif indOpenClose(i,2)==0
        op=0;
    else
        indOpenClose(i,2)=-1;
    end
end
if isempty(indOpenClose)
    y=[];
else
    indOpenClose(indOpenClose(:,2)<0,:)=[];
    y=[indOpenClose(1:2:end,1),indOpenClose(2:2:end,1)];% Open/Close Indexes
end