function text=header2text(header)
text='';
fn=fieldnames(header);
for i=1:length(fn)
    name=fn{i}; data=header.(name);
    switch name
        case 'HTTP'
            data=['HTTP/1.0 ' data];
        case 'Date'
            data=['Date: ' data];
        case 'Server'
            data=['Server: ' data];
        case 'XPoweredBY'
            data=['X-Powered-By: ' data];
        case 'SetCookie'
            data=['Set-Cookie: ' data];
        case 'Expires'
            data=['Expires: ' data];
        case 'CacheControl'
            data=['Cache-Control: ' data];
        case 'Pragma'
            data=['Pragma: ' data];
        case 'XPingback'
            data=['X-Pingback: ' data];
        case 'Connection'
            data=['Connection: ' data];
        case 'ContentLength'
            data=['Content-Length: '  data];
        case 'ContentType'
            data=['Content-Type: ' data];
        case 'LastModified'
            data=['Last-Modified: ' data];
        case 'AcceptRanges';
            data=['Accept-Ranges: ' data];
        case 'ETag';
            data=['ETag: ' data];
        case'KeepAlive';
            data=['Keep-Alive: ' data];
        otherwise
            warning('header fieldname wrong');
            continue;
    end
    text=[text data '\n'];
end
text=[text '\n'];
text=sprintf(text);
