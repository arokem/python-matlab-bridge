function figdir = make_figs()
% Get all the figures that are currently open (presumably from a cell 
% that was just executed):
figHandles = get(0, 'children') ;

% We will return the location of the matlab tempdir, so that ipython knows
% where to get the figures and render them from:
figdir = tempdir;

% We will put all of these in the temp dir with an identifying root, so
% that we can grab all of them into the cell (and they will be deleted
% immediately after being rendered).
filename = [figdir, 'MatlabFig', num2str(fig)];

for fig=1:length(figHandles)
    h = figHandles(fig);
    saveas(h, [filename, '.png']
    % Once you've saved it, close it, so it doesn't get dragged into the
    % scope of other cells
    close(h);
end

close

