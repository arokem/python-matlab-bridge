function header=make_image_http_header(html,found)
if(found)
    header.HTTP='200 OK';
else
    header.HTTP='404 Not Found';
end
header.Date='Tue, 12 Oct 2010 09:19:05 GMT';
header.Server='Matlab Webserver';
header.LastModified='Last-Modified: Thu, 21 Jun 2007 14:56:37 GMT';
header.AcceptRanges='Accept-Ranges: bytes';
header.ContentLength=num2str(length(html));
header.ETag='"948921-15ae-c0dbf340"';
%header.KeepAlive='Keep-Alive: timeout=15, max=100';
header.ContentType='image/png';
