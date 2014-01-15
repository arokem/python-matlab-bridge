function J=mat2json(M,F)
%MAT2JSON: converts a Matlab structure into a javscript data object (JSON).
%
% J = MAT2JSON(M,F)
%
%         M can also be a file name. In the spirit of fast prototyping
%         this function takes a very loose approach to data types and
%         dimensionality - neither is explicitly retained.
%
%         The second input argument is optional and when used it indicates
%         the name of the file where J is to be stored.
%
% Example: mat2json(json2mat('{lala:2,lele:4,lili:[1,2,{bubu:5}]}'))
%
% Jonas Almeida, March 2010

PRECISION = 10; % Keep a maximum of 10 decimal digits

switch class(M)
	case 'struct'
		J='{';
		f=fieldnames(M);
		for i=1:length(f)
			J=[J,'"',f{i},'":',mat2json(M.(f{i})),','];
		end
		J(end)='}';

	case 'cell'
		J='[';
		for i=1:length(M)
			J=[J,mat2json(M{i}),','];
		end
		if J == '[';
			J='[]';
		else
			J(end) = ']';
		end
	otherwise
		if isnumeric(M) % notice looseness in not converting single numbers into arrays
			if length(M(:))==1
				J=num2str(M, PRECISION);
			else
				s=size(M);
				if (length(s)==2)&(s(1)<2) % horizontal or null vector
					J=['[',num2str(M, PRECISION),']']; % and of destroying dimensionality
					J=regexprep(J,'\s+',',');
				elseif length(s)==2 %2D solution
					J='[';
					for i=1:s(1)
						J=[J,mat2json(M(i,:)),','];
					end
					J(end)=']';
				elseif length(s)>2 % for now treat higher dimensions as linear vectors
					J=['[',num2str(M(:)', PRECISION),']']; % and of destroying dimensionality
					J=regexprep(J,'\s+',',');
				end
			end
		elseif ischar(M)
			% see http://json.org/
			M = strrep(M,'\','\\');   % reverse solidus; have to do this one first!
			M = strrep(M,'/','\/');   % solidus
			M = strrep(M,'"','\"');   % quotation marks
			M = strrep(M,char(8),'\b');  % backspace
			M = strrep(M,char(12),'\f');  % form feed
			M = strrep(M,char(10),'\n');  % newline
			M = strrep(M,char(13),'\r');  % carriage return
			M = strrep(M,char(9),'\t');  % horizontal tab
			J=['"',M,'"']; % otherwise it is treated as a string
		else  % punt!
			J=['"',M,'"']; % otherwise it is treated as a string
		end
end

if nargin>1 %save JSON result in file
	fid=fopen(F,'w');
	fprintf(fid,'%s',J);
	fclose(fid);
end

end %function
