local Task = {}

function Task.new(initial_delay, hotkey_keys)
	local self = Task
	self.running = false
	self.frame = 0
	self.end_frame = initial_delay
	self.hotkey_keys = hotkey_keys
	self.steps = {}
	return self
end

function Task:add(func, delay)
	self.steps[self.end_frame] = func
	self.end_frame = self.end_frame + delay
end

function Task:tick()
	if self.running then
		func = self.steps[self.frame]
		if func ~= nil then
			func()
		end
		self.frame = self.frame + 1
		if self.frame >= self.end_frame then
			self:stop()
		end
	elseif self:is_hotkey_pressed() then
		self:start()
	end
end

function Task:is_hotkey_pressed()
	keys = input.get()
	for _, hotkey in pairs(self.hotkey_keys) do
		if not keys[hotkey] then
			return false
		end
	end
	return true
end

function Task:start()
	self.running = true
	self.frame = 0
end

function Task:stop()
	self.running = false
end

return Task
