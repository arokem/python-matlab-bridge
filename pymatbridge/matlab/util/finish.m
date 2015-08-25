% make sure socket gets closed no matter how MATLAB exists (sans crash)
if exist('messenger', 'file')
    if messenger('check')
        messenger('exit');
    end
end
