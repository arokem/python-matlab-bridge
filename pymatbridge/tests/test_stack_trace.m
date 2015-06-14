function o = test_stack_trace(input)
  o = foo(input);
end

function o = foo(input)
  o = bar(input)
end

function o = bar(input)
  o = baz(input)
end

function o = baz(input)
  o = quux(input)
end
