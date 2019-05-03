local Task = require('task')
local util = require('util')

local MOVE_STATS_SIZE = 3

local SCREEN_CHANGE_DELAY = 60
local MOVE_LOAD_DELAY = 10
local MOVE_DELAY_INITIAL = 15
local MOVE_DELAY_END = 15

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

function dpad_left() joypad.set(0, {left = 1}) end
function dpad_right() joypad.set(0, {right = 1}) end
function dpad_up() joypad.set(0, {up = 1}) end
function dpad_down() joypad.set(0, {down = 1}) end
function button_a() joypad.set(0, {A = 1}) end
function button_b() joypad.set(0, {B = 1}) end

function screenshot_task(hotkey, output_dir, writeflag_filename, move_stats_offset)

	function screenshot(filename)
		return function()
			local file = io.open(output_dir .. filename .. '.gd', 'wb')
			file:write(gui.gdscreenshot('bottom'))
			io.close(file)
		end
	end

	function movestats(char_index, move_index)
		return function()
			local filename = 'party_0' .. tostring(char_index) .. '_move_0' .. tostring(move_index) .. '.bin'
			util.dump_memory(move_stats_offset, MOVE_STATS_SIZE, output_dir .. filename)
		end
	end

	function write_flag()
		util.write_flag(output_dir .. writeflag_filename)
	end

	local task = Task.new(10, hotkey)

	-- capture stats screen for slot 0
	task:add(isolate_character, 2)
	task:add(screenshot('party_00_char'), 2)
	task:add(isolate_types, 2)
	task:add(screenshot('party_00_type'), 2)
	task:add(restore_all_layers, 2)

	-- capture moves screen for slot 0
	task:add(dpad_right, SCREEN_CHANGE_DELAY)
	task:add(screenshot('party_00_moves'), 2)
	task:add(button_a, MOVE_DELAY_INITIAL)
	task:add(movestats(0, 0), 2)
	task:add(dpad_down, MOVE_LOAD_DELAY)
	task:add(movestats(0, 1), 2)
	task:add(dpad_down, MOVE_LOAD_DELAY)
	task:add(movestats(0, 2), 2)
	task:add(dpad_down, MOVE_LOAD_DELAY)
	task:add(movestats(0, 3), 2)
	task:add(button_b, MOVE_DELAY_END)

	-- capture moves screen for slot 1
	task:add(dpad_down, SCREEN_CHANGE_DELAY)
	task:add(screenshot('party_01_moves'), 2)
	task:add(button_a, MOVE_DELAY_INITIAL)
	task:add(movestats(1, 0), 2)
	task:add(dpad_down, MOVE_LOAD_DELAY)
	task:add(movestats(1, 1), 2)
	task:add(dpad_down, MOVE_LOAD_DELAY)
	task:add(movestats(1, 2), 2)
	task:add(dpad_down, MOVE_LOAD_DELAY)
	task:add(movestats(1, 3), 2)
	task:add(button_b, MOVE_DELAY_END)

	-- capture stats screen for slot 1
	task:add(dpad_left, SCREEN_CHANGE_DELAY)
	task:add(isolate_character, 2)
	task:add(screenshot('party_01_char'), 2)
	task:add(isolate_types, 2)
	task:add(screenshot('party_01_type'), 2)
	task:add(restore_all_layers, 2)

	-- capture stats screen for slot 2
	task:add(dpad_down, SCREEN_CHANGE_DELAY)
	task:add(isolate_character, 2)
	task:add(screenshot('party_02_char'), 2)
	task:add(isolate_types, 2)
	task:add(screenshot('party_02_type'), 2)
	task:add(restore_all_layers, 2)

	-- capture moves screen for slot 2
	task:add(dpad_right, SCREEN_CHANGE_DELAY)
	task:add(screenshot('party_02_moves'), 2)
	task:add(button_a, MOVE_DELAY_INITIAL)
	task:add(movestats(2, 0), 2)
	task:add(dpad_down, MOVE_LOAD_DELAY)
	task:add(movestats(2, 1), 2)
	task:add(dpad_down, MOVE_LOAD_DELAY)
	task:add(movestats(2, 2), 2)
	task:add(dpad_down, MOVE_LOAD_DELAY)
	task:add(movestats(2, 3), 2)
	task:add(button_b, MOVE_DELAY_END)

	-- capture moves screen for slot 3
	task:add(dpad_down, SCREEN_CHANGE_DELAY)
	task:add(screenshot('party_03_moves'), 2)
	task:add(button_a, MOVE_DELAY_INITIAL)
	task:add(movestats(3, 0), 2)
	task:add(dpad_down, MOVE_LOAD_DELAY)
	task:add(movestats(3, 1), 2)
	task:add(dpad_down, MOVE_LOAD_DELAY)
	task:add(movestats(3, 2), 2)
	task:add(dpad_down, MOVE_LOAD_DELAY)
	task:add(movestats(3, 3), 2)
	task:add(button_b, MOVE_DELAY_END)

	-- capture stats screen for slot 3
	task:add(dpad_left, SCREEN_CHANGE_DELAY)
	task:add(isolate_character, 2)
	task:add(screenshot('party_03_char'), 2)
	task:add(isolate_types, 2)
	task:add(screenshot('party_03_type'), 2)
	task:add(restore_all_layers, 2)

	-- capture stats screen for slot 4
	task:add(dpad_down, SCREEN_CHANGE_DELAY)
	task:add(isolate_character, 2)
	task:add(screenshot('party_04_char'), 2)
	task:add(isolate_types, 2)
	task:add(screenshot('party_04_type'), 2)
	task:add(restore_all_layers, 2)

	-- capture moves screen for slot 4
	task:add(dpad_right, SCREEN_CHANGE_DELAY)
	task:add(screenshot('party_04_moves'), 2)
	task:add(button_a, MOVE_DELAY_INITIAL)
	task:add(movestats(4, 0), 2)
	task:add(dpad_down, MOVE_LOAD_DELAY)
	task:add(movestats(4, 1), 2)
	task:add(dpad_down, MOVE_LOAD_DELAY)
	task:add(movestats(4, 2), 2)
	task:add(dpad_down, MOVE_LOAD_DELAY)
	task:add(movestats(4, 3), 2)
	task:add(button_b, MOVE_DELAY_END)

	-- capture moves screen for slot 5
	task:add(dpad_down, SCREEN_CHANGE_DELAY)
	task:add(screenshot('party_05_moves'), 2)
	task:add(button_a, MOVE_DELAY_INITIAL)
	task:add(movestats(5, 0), 2)
	task:add(dpad_down, MOVE_LOAD_DELAY)
	task:add(movestats(5, 1), 2)
	task:add(dpad_down, MOVE_LOAD_DELAY)
	task:add(movestats(5, 2), 2)
	task:add(dpad_down, MOVE_LOAD_DELAY)
	task:add(movestats(5, 3), 2)
	task:add(button_b, MOVE_DELAY_END)

	-- capture stats screen for slot 5
	task:add(dpad_left, SCREEN_CHANGE_DELAY)
	task:add(isolate_character, 2)
	task:add(screenshot('party_05_char'), 2)
	task:add(isolate_types, 2)
	task:add(screenshot('party_05_type'), 2)
	task:add(restore_all_layers, 2)

	-- write out a flag so we know all screenshots are finished updating
	task:add(write_flag, 2)

	return task
end

return screenshot_task
