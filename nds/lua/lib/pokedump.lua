local util = require('util')
local screenshot_task = require('screenshot_task')

-- This directory (relative to the entry point .lua file) is where
-- screenshots, memory dumps, and flags will be written.
local OUTPUT_DIR = '../dump/'

-- Interval at which memory will be automatically dumped to file
local DUMP_INTERVAL = 1.0
local DUMP_WRITEFLAG_PATH = OUTPUT_DIR .. 'dump.writeflag'

-- Memory region containing the current stats for the party
-- (These are encrypted and don't update during battle)
local PARTY_RECORD_SIZE = 220
local PARTY_DUMP_SIZE = PARTY_RECORD_SIZE * 6
local PARTY_OUTPUT_PATH = OUTPUT_DIR .. 'party.bin'

-- Memory region containing the party stats while in battle
local BATTLE_RECORD_SIZE = 548
local BATTLE_DUMP_SIZE = BATTLE_RECORD_SIZE * 6
local BATTLE_OUTPUT_PATH = OUTPUT_DIR .. 'battle.bin'

-- Configuration for the screenshot-capture process, which needs to be
-- triggered manually
local SCREENSHOT_HOTKEY = {'control', 'shift', 'F11'}
local SCREENSHOT_WRITEFLAG_FILENAME = 'screenshot.writeflag'

--- Returns a function that can be registered as a GUI callback.
--
-- Each frame, that function will evaluate two conditions:
--
--   1. Whether screenshot capture has been triggered
--   2. Whether it's time to dump memory (based on DUMP_INTERVAL)
--
-- If screenshot capture is triggered, the script will execute a background
-- task writes out screenshot images and move stats to disk, followed by a
-- .writeflag file that tells the accompanying Python application that new
-- data is ready to be read.
--
-- At the memory dump interval, the script will dump a portion of memory to
-- party.bin and battle.bin, and then touch another .writeflag for the same
-- purpose.
--
function pokedump(party_offset, battle_offset, move_stats_offset)
	local task = screenshot_task(SCREENSHOT_HOTKEY, OUTPUT_DIR, SCREENSHOT_WRITEFLAG_FILENAME, move_stats_offset)
	local last_dump_time = 0.0

	function loop()
		current_time = os.time()
		if not task.running and current_time >= last_dump_time + DUMP_INTERVAL then
			util.dump_memory(party_offset, PARTY_DUMP_SIZE, PARTY_OUTPUT_PATH)
			util.dump_memory(battle_offset, BATTLE_DUMP_SIZE, BATTLE_OUTPUT_PATH)
			util.write_flag(DUMP_WRITEFLAG_PATH)
			last_dump_time = current_time
		end
		task:tick()
	end

	return loop
end

return pokedump
