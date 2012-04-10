function header=make_html_http_header(html,found)
if(found)
    header.HTTP='200 OK';
else
    header.HTTP='404 Not Found';
end
header.Date='Tue, 12 Oct 2010 09:19:05 GMT';
header.Server='Matlab Webserver';
header.XPoweredBY=['Matlab' version];
header.SetCookie='SESSID=5322082bf473207961031e3df1f45a22; path=/';
header.Expires='Thu, 19 Nov 1980 08:00:00 GMT';
header.CacheControl='no-store, no-cache, must-revalidate, post-check=0, pre-check=0';
header.Pragma='no-cache';
header.Connection='close';
header.ContentLength=num2str(length(html));
header.ContentType='text/html; charset=UTF-8';