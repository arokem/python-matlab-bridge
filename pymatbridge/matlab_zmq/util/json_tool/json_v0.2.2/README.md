Matlab JSON v0.2
================

This package contains Matlab class to serialize/decode matlab object in
json format. The software uses org.json java package to convert json to
java object and then translates it into Matlab object.

API
---

All functions are scoped under `json` namespace.

    startup Initialize runtime environment.
    dump    Encode matlab value into a JSON string.
    load    Load matlab value from a JSON string.
    read    Load a matlab value from a JSON file.
    write   Write a matlab value into a JSON file.

Usage
-----

Add path to the directory containing `+json` before use, and call
`json.startup`.

To serialize matlab object:

    >> X = struct('field1', magic(2), 'field2', 'hello');
    >> S = json.dump(X);
    >> disp(S);
    {"field2":"hello","field1":[[1,3],[4,2]]}

To decode json string:

    >> X = json.load(S);
    >> disp(X);
        field2: 'hello'
        field1: [2x2 double]

To read from or write to a json file.

    >> json.write(X, '/path/to/file.json');
    >> X = json.read('/path/to/file.json');

Note
----

Due to the multiple ways to represent an array in Matlab (i.e., numeric
array, cell array, or struct array), it is impossible to represent
everything in a compatible format. For example, a json string "[[1,2],[3,4]]"
can be interpreted in different ways in Matlab, such as [1,2;3,4], {1,2;3,4},
{[1,2],[3,4]}, etc. Because of this, `json.load` does not always yield the
exactly same input to `json.dump`.

This implementation is designed to maximize the ease of data exchange. For
that purpose, by default, json parser assumes the following.

 * Native arrays precede a cell array. "[1,2]" is [1,2] in matlab.
 * Row-major order. e.g., "[[1,2],[3,4]]" is [1,2;3,4] in matlab.
 * N-D array is a nested json array.
 * Any other ambiguous arrays are treated as cell array. "[]" is {}.

For example, a nested array with the same sized elements is treated as an N-D
array.

    >> x = json.load('[[[1,2],[3,4]],[[5,6],[7,8]]]')

    x(:,:,1) =
         1     2
         3     4

    x(:,:,2) =
         5     6
         7     8


The `json.load` function can optionally take an option to specify column-major
interpretation or cell-array precedence. Check `help json.load` for details.

Test
----

To run a test, use `test_all` function in the `test` directory.

    >> addpath('test');
    >> test_all;

License
-------

You may redistribute this software under BSD license.


Version
-------

 * 0.2 API changed to functions from a class.
 * 0.1 Initial release.

Links
-----

JSON in Java: http://json.org/java/
