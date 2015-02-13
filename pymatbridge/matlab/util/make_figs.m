function fig_files = make_figs(figdir, fmt, res)
% Get all the figures that are currently open (presumably from a cell
% that was just executed):
figHandles = get(0, 'children');

fig_files = {};

if (nargin < 2)
    fmt = 'png'
end
if (nargin < 3)
    res = 96
end

for fig=1:length(figHandles)
    h = figHandles(fig);
    % We will put all of these in the temp dir with an identifying root, so
    % that we can grab all of them into the cell (and they will be deleted
    % immediately after being rendered).
    filename = ['MatlabFig', sprintf('%03d.%s', fig, fmt)];
    filename = fullfile(figdir, filename);
    res_fmt = sprintf('-r%d', res);
    driver = sprintf('-d%s', fmt);
    print(h, filename, driver, res_fmt);
    % Once you've saved it, close it, so it doesn't get dragged into the
    % scope of other cells
    close(h);
    fig_files{fig} = filename;
end

end %function
