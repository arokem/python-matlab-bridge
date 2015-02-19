function fig_files = make_figs(figdir)
% Get all the figures that are currently open (presumably from a cell
% that was just executed):
figHandles = get(0, 'children');

fig_files = {};

for fig=1:length(figHandles)
    h = figHandles(fig);
    % We will put all of these in the temp dir with an identifying root, so
    % that we can grab all of them into the cell (and they will be deleted
    % immediately after being rendered).
    filename = fullfile(figdir, ['MatlabFig', sprintf('%03d', fig)]);
    saveas(h, [filename, '.png']);
    % Once you've saved it, close it, so it doesn't get dragged into the
    % scope of other cells
    if (strcmp(get(h, 'visible'), 'off'))
        close(h);
    end
    fig_files{fig} = [filename '.png'];
end

end %function
