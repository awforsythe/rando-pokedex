util = {}

--- Dumps a fixed-size section of NDS RAM to a binary file.
function util.dump_memory(offset, size, output_path)
	local bytes = memory.readbyterange(offset, size)
	local file = io.open(output_path, 'wb')
	for k, v in pairs(bytes) do
		file:write(string.char(v))
	end
	io.close(file)
end

--- Writes an empty ASCII file to indicate that a new batch of files is ready for read.
function util.write_flag(path)
	local file = io.open(path, 'w')
	file:write('\n')
	io.close(file)
end

return util
