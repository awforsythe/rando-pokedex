local PARTY_OFFSET = 0x022349D4
local PARTY_RECORD_SIZE = 220
local PARTY_DUMP_SIZE = PARTY_RECORD_SIZE * 6
local PARTY_OUTPUT_PATH = '../dump/party.bin'

local BATTLE_OFFSET = 0x0226D6D0
local BATTLE_RECORD_SIZE = 548
local BATTLE_DUMP_SIZE = BATTLE_RECORD_SIZE * 6
local BATTLE_OUTPUT_PATH = '../dump/battle.bin'

local DUMP_INTERVAL = 1.0
local DUMP_WRITEFLAG_PATH = '../dump/dump.writeflag'
local SCREENSHOT_WRITEFLAG_PATH = '../dump/screenshot.writeflag'

local MOVE_STATS_OFFSET = 0x02146556
local MOVE_STATS_SIZE = 3
local MOVE_STATS_DIR = '../dump/'

local last_dump_time = 0.0

function dump_memory(offset, size, output_path)
	bytes = memory.readbyterange(offset, size)
	file = io.open(output_path, 'wb')
	for k, v in pairs(bytes) do
		file:write(string.char(v))
	end
	io.close(file)
end

function isolate_character()
	gui.togglelayer(0, 1)
	gui.togglelayer(0, 2)
	gui.togglelayer(0, 3)
	gui.togglelayer(0, 4)
end

function isolate_types()
	gui.togglelayer(0, 0)
	gui.togglelayer(0, 4)
end

function restore_all_layers()
	gui.togglelayer(0, 0)
	gui.togglelayer(0, 1)
	gui.togglelayer(0, 2)
	gui.togglelayer(0, 3)
end

function write_screenshot(screen, filename)
	file = io.open(filename, 'wb')
	file:write(gui.gdscreenshot(screen, filename))
	io.close(file)
end

function screenshot(filename)
	return function()
		write_screenshot('bottom', '../dump/' .. filename .. '.gd')
	end
end

function movestats(char_index, move_index)
	return function()
		local filename = 'party_0' .. tostring(char_index) .. '_move_0' .. tostring(move_index) .. '.bin'
		dump_memory(MOVE_STATS_OFFSET, MOVE_STATS_SIZE, MOVE_STATS_DIR .. filename)
	end
end

function write_flag(path)
	file = io.open(path, 'w')
	file:write('\n')
	io.close(file)
end

function dpad_left()
	joypad.set(0, {left = 1})
end

function dpad_right()
	joypad.set(0, {right = 1})
end

function dpad_up()
	joypad.set(0, {up = 1})
end

function dpad_down()
	joypad.set(0, {down = 1})
end

function button_a()
	joypad.set(0, {A = 1})
end

function button_b()
	joypad.set(0, {B = 1})
end

Script = {running = false, frame = 0, end_frame = 10, steps = {}}

function Script:add(func, delay)
	self.steps[self.end_frame] = func
	self.end_frame = self.end_frame + delay
end

function Script:start()
	self.running = true
	self.frame = 0
end

function Script:tick()
	if self.running == true then
		func = self.steps[self.frame]
		if func ~= nil then
			print(self.frame)
			func()
		end
		self.frame = self.frame + 1
		if self.frame >= self.end_frame then
			self.running = false
		end
	end
end

local script = Script
local screen_change_delay = 60
local move_load_delay = 10
local move_delay_initial = 15
local move_delay_end = 15

-- capture stats screen for slot 0
script:add(isolate_character, 2)
script:add(screenshot('party_00_char'), 2)
script:add(isolate_types, 2)
script:add(screenshot('party_00_type'), 2)
script:add(restore_all_layers, 2)

-- capture moves screen for slot 0
script:add(dpad_right, screen_change_delay)
script:add(screenshot('party_00_moves'), 2)
script:add(button_a, move_delay_initial)
script:add(movestats(0, 0), 2)
script:add(dpad_down, move_load_delay)
script:add(movestats(0, 1), 2)
script:add(dpad_down, move_load_delay)
script:add(movestats(0, 2), 2)
script:add(dpad_down, move_load_delay)
script:add(movestats(0, 3), 2)
script:add(button_b, move_delay_end)

-- capture moves screen for slot 1
script:add(dpad_down, screen_change_delay)
script:add(screenshot('party_01_moves'), 2)
script:add(button_a, move_delay_initial)
script:add(movestats(1, 0), 2)
script:add(dpad_down, move_load_delay)
script:add(movestats(1, 1), 2)
script:add(dpad_down, move_load_delay)
script:add(movestats(1, 2), 2)
script:add(dpad_down, move_load_delay)
script:add(movestats(1, 3), 2)
script:add(button_b, move_delay_end)

-- capture stats screen for slot 1
script:add(dpad_left, screen_change_delay)
script:add(isolate_character, 2)
script:add(screenshot('party_01_char'), 2)
script:add(isolate_types, 2)
script:add(screenshot('party_01_type'), 2)
script:add(restore_all_layers, 2)

-- capture stats screen for slot 2
script:add(dpad_down, screen_change_delay)
script:add(isolate_character, 2)
script:add(screenshot('party_02_char'), 2)
script:add(isolate_types, 2)
script:add(screenshot('party_02_type'), 2)
script:add(restore_all_layers, 2)

-- capture moves screen for slot 2
script:add(dpad_right, screen_change_delay)
script:add(screenshot('party_02_moves'), 2)
script:add(button_a, move_delay_initial)
script:add(movestats(2, 0), 2)
script:add(dpad_down, move_load_delay)
script:add(movestats(2, 1), 2)
script:add(dpad_down, move_load_delay)
script:add(movestats(2, 2), 2)
script:add(dpad_down, move_load_delay)
script:add(movestats(2, 3), 2)
script:add(button_b, move_delay_end)

-- capture moves screen for slot 3
script:add(dpad_down, screen_change_delay)
script:add(screenshot('party_03_moves'), 2)
script:add(button_a, move_delay_initial)
script:add(movestats(3, 0), 2)
script:add(dpad_down, move_load_delay)
script:add(movestats(3, 1), 2)
script:add(dpad_down, move_load_delay)
script:add(movestats(3, 2), 2)
script:add(dpad_down, move_load_delay)
script:add(movestats(3, 3), 2)
script:add(button_b, move_delay_end)

-- capture stats screen for slot 3
script:add(dpad_left, screen_change_delay)
script:add(isolate_character, 2)
script:add(screenshot('party_03_char'), 2)
script:add(isolate_types, 2)
script:add(screenshot('party_03_type'), 2)
script:add(restore_all_layers, 2)

-- capture stats screen for slot 4
script:add(dpad_down, screen_change_delay)
script:add(isolate_character, 2)
script:add(screenshot('party_04_char'), 2)
script:add(isolate_types, 2)
script:add(screenshot('party_04_type'), 2)
script:add(restore_all_layers, 2)

-- capture moves screen for slot 4
script:add(dpad_right, screen_change_delay)
script:add(screenshot('party_04_moves'), 2)
script:add(button_a, move_delay_initial)
script:add(movestats(4, 0), 2)
script:add(dpad_down, move_load_delay)
script:add(movestats(4, 1), 2)
script:add(dpad_down, move_load_delay)
script:add(movestats(4, 2), 2)
script:add(dpad_down, move_load_delay)
script:add(movestats(4, 3), 2)
script:add(button_b, move_delay_end)

-- capture moves screen for slot 5
script:add(dpad_down, screen_change_delay)
script:add(screenshot('party_05_moves'), 2)
script:add(button_a, move_delay_initial)
script:add(movestats(5, 0), 2)
script:add(dpad_down, move_load_delay)
script:add(movestats(5, 1), 2)
script:add(dpad_down, move_load_delay)
script:add(movestats(5, 2), 2)
script:add(dpad_down, move_load_delay)
script:add(movestats(5, 3), 2)
script:add(button_b, move_delay_end)

-- capture stats screen for slot 5
script:add(dpad_left, screen_change_delay)
script:add(isolate_character, 2)
script:add(screenshot('party_05_char'), 2)
script:add(isolate_types, 2)
script:add(screenshot('party_05_type'), 2)
script:add(restore_all_layers, 2)

-- write out a flag so we know all screenshots are finished updating
script:add(function() write_flag(SCREENSHOT_WRITEFLAG_PATH) end, 2)

function loop()
	current_time = os.time()
	if script.running == false and current_time >= last_dump_time + DUMP_INTERVAL then
		dump_memory(PARTY_OFFSET, PARTY_DUMP_SIZE, PARTY_OUTPUT_PATH)
		dump_memory(BATTLE_OFFSET, BATTLE_DUMP_SIZE, BATTLE_OUTPUT_PATH)
		write_flag(DUMP_WRITEFLAG_PATH)
		last_dump_time = current_time
	end

	keys = input.get()
	if script.running == false and keys['F11'] == true and keys['control'] == true and keys['shift'] == true then
		script:start()
	end
	script:tick()
end

gui.register(loop)
