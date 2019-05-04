local Task = {}

--- Creates a new Task.
-- A Task provides a means of scheduling work to be done synchronously over
-- the course of several frames of emulation. initial_delay denotes how many
-- frames to wait before executing the first step added to the Task.
-- hotkey_keys should be a list of key names that trigger this Task,
-- e.g. {'control', 'alt', 'F5'}
function Task.new(initial_delay, hotkey_keys)
	local self = Task
	self.running = false
	self.frame = 0
	self.end_frame = initial_delay
	self.hotkey_keys = hotkey_keys
	self.steps = {}
	return self
end

--- Adds a 0-argument function to the list of steps in this task.
-- The delay specifies how many frames to wait AFTER executing this task
-- before the next function will be added.
function Task:add(func, delay)
	self.steps[self.end_frame] = func
	self.end_frame = self.end_frame + delay
end

--- Called each frame to update the state of the task.
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

--- Indicates whether the Task's hotkey inputs are currently active.
function Task:is_hotkey_pressed()
	keys = input.get()
	for _, hotkey in pairs(self.hotkey_keys) do
		if not keys[hotkey] then
			return false
		end
	end
	return true
end

--- Starts running the Task from the beginning.
function Task:start()
	self.running = true
	self.frame = 0
end

--- Stops Task execution.
function Task:stop()
	self.running = false
end

return Task
