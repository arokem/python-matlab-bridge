function test_all
%TEST_ALL Run all tests.

  files = dir(fullfile('test', 'test_*.m'));
  for i = 1:numel(files)
    fname = strrep(files(i).name, '.m', '');
    if ~strcmp(fname, 'test_all')
      fprintf('== %s ==\n', fname);
      feval(fname);
    end
  end

end
