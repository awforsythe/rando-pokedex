local util = require('util')
local screenshot_task = require('screenshot_task')

local OUTPUT_DIR = '../dump/'

local DUMP_INTERVAL = 1.0
local DUMP_WRITEFLAG_PATH = OUTPUT_DIR .. 'dump.writeflag'

local PARTY_RECORD_SIZE = 220
local PARTY_DUMP_SIZE = PARTY_RECORD_SIZE * 6
local PARTY_OUTPUT_PATH = OUTPUT_DIR .. 'party.bin'

local BATTLE_RECORD_SIZE = 548
local BATTLE_DUMP_SIZE = BATTLE_RECORD_SIZE * 6
local BATTLE_OUTPUT_PATH = OUTPUT_DIR .. 'battle.bin'

local SCREENSHOT_HOTKEY = {'control', 'shift', 'F11'}
local SCREENSHOT_WRITEFLAG_FILENAME = 'screenshot.writeflag'

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
