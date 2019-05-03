util = {}

function util.dump_memory(offset, size, output_path)
	local bytes = memory.readbyterange(offset, size)
	local file = io.open(output_path, 'wb')
	for k, v in pairs(bytes) do
		file:write(string.char(v))
	end
	io.close(file)
end

function util.write_flag(path)
	local file = io.open(path, 'w')
	file:write('\n')
	io.close(file)
end

return util
