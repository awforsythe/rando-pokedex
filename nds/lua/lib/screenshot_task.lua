local Task = require('task')
local util = require('util')

local MOVE_STATS_SIZE = 3

local SCREEN_CHANGE_DELAY = 60
local MOVE_LOAD_DELAY = 10
local MOVE_DELAY_INITIAL = 15
local MOVE_DELAY_END = 15

--- Aborts with an error if gui.setlayermask is not exposed.
-- This is a custom function added to DeSmuME in a custom build made for this script.
-- It is not currently avaiable in any public build of DeSmuME.
-- If building DeSmuME from source, see README.md for the details of the changes.
function check_setlayermask_func()
	local f = gui.setlayermask
	if f == nil then
		error('This build of DeSmuME is not supported. In fact, no publicly-available build of DeSmuME is currently supported. Please see the README for more information.')
	end
end

--- Disables all main screen layers except BG0, which contains the character sprite.
function isolate_character()
	check_setlayermask_func()
	gui.setlayermask(1, 31) -- 00001, 11111
end

--- Disables all main screen layers except OBJ, which contains the type graphics.
function isolate_types()
	check_setlayermask_func()
	gui.setlayermask(16, 31) -- 10000, 11111
end

--- Enables all screen layers.
function restore_all_layers()
	check_setlayermask_func()
	gui.setlayermask(31, 31) -- 11111, 11111
end

--- Sets DS input states.
function dpad_left() joypad.set(0, {left = 1}) end
function dpad_right() joypad.set(0, {right = 1}) end
function dpad_up() joypad.set(0, {up = 1}) end
function dpad_down() joypad.set(0, {down = 1}) end
function button_a() joypad.set(0, {A = 1}) end
function button_b() joypad.set(0, {B = 1}) end

--- Returns a Task object that writes out screenshots and memory dumps when the specified hotkey is pressed.
--
-- This task is meant to be run when viewing the Summary screen for the first
-- Pokemon in the party, looking at the stats rather than the move list. The
-- cycles through each of the six Pokemon, and for each one it writes out:
--
--   party_%02d_char.gd - The character sprite on a green background
--   party_%02d_type.gd - The badge that indicates the Pokemon's type(s)
--   party_%02d_moves.gd - The list of moves, showing the moves' type(s)
--   party_%02d_move_%02d.bin - Files with 3 bytes reflecting the stats of each move
--
-- Upon completion, the task writes out a .writeflag file, letting the
-- accompanying Python application know that these files are updated and have
-- finished being written.
--
function screenshot_task(hotkey, output_dir, writeflag_filename, move_stats_offset)

	-- Thunk to create a screenshot with the given filename
	function screenshot(filename)
		return function()
			local file = io.open(output_dir .. filename .. '.gd', 'wb')
			file:write(gui.gdscreenshot('bottom'))
			io.close(file)
		end
	end

	-- Thunk to dump the tiny region of memory that contains the stats for the currently-selected move
	function movestats(char_index, move_index)
		return function()
			local filename = 'party_0' .. tostring(char_index) .. '_move_0' .. tostring(move_index) .. '.bin'
			util.dump_memory(move_stats_offset, MOVE_STATS_SIZE, output_dir .. filename)
		end
	end

	-- Thunk to write out a writeflag with the correct name
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
