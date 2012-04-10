function json_response = test_connect(headers, config)
    c = clock;
    response.message = sprintf('Matlab: %s connected!', headers.Content.id);
    response.time = sprintf('%d:%d', c(4), c(5));
	json_response = mat2json(response);