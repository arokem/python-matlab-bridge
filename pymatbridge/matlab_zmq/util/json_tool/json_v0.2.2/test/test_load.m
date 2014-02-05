function test_load
%TEST_LOAD Test json.load.

  fixtures = {...
    [],        'null';...
    1,         '1.0';...
    true,      'true';...
    'foo',     'foo';...
    {},        '[]';...
    struct(),  '{}';...
    1:5,       '[1,2,3,4,5]';...
    (1:5)',    '[[1],[2],[3],[4],[5]]';...
    [1,2;3,4], '[[1,2],[3,4]]';...
    cat(3,[1,2;3,4],[5,6;7,8]), '[[[1,2],[3,4]],[[5,6],[7,8]]]';...
    {{}},      '[[]]';...
    struct('a',[1,2]), '{"a":[1,2]}';...
    struct('a',struct('b',{1,2})), '{"a":[{"b":1},{"b":2}]}';...
    {'foo','bar','baz'}, '["foo","bar","baz"]';...
    };

  for i = 1:size(fixtures, 1)
    value = json.load(fixtures{i,2});
    if equal_(value, fixtures{i,1})
      fprintf('PASS\n');
    else
      fprintf('FAIL: fixture %d: ''%s''.\n', i, fixtures{i,2});
    end
  end

end

function flag = equal_(value1, value2)
%EQUAL_ Check if two values are the same.
  t1 = type_info_(value1);
  t2 = type_info_(value2);
  flag = numel(t1) == numel(t2) && all(t1 == t2);
  if ~flag, return; end

  if iscell(value1)
    for i = 1:numel(value1)
      flag = equal_(value1{i}, value2{i});
      if ~flag, return; end
    end
  elseif isstruct(value1)
    for j = 1:numel(value1)
      fields = fieldnames(value1);
      for i = 1:numel(fields)
        flag = equal_(value1(j).(fields{i}), value2(j).(fields{i}));
        if ~flag, return; end
      end
    end
  elseif ~isempty(value1)
    flag = all(value1(:) == value2(:));
  end
end

function vec = type_info_(value)
%TYPE_INFO_ Return binary encoding of type information
  vec = [uint8(class(value)), typecast(size(value), 'uint8')];
  if isstruct(value)
    fields = fieldnames(value);
    vec = [vec, uint8([fields{:}])];
  end
end