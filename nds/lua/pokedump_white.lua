-- Entry point for Pokémon White
package.path = package.path .. ';lib/?.lua'
local pokedump = require('pokedump')

-- Create a function that runs the script with the appropriate offsets for this game
local PARTY_OFFSET = 0x022349D4
local BATTLE_OFFSET = 0x0226D6D0
local MOVE_STATS_OFFSET = 0x02146556
callback = pokedump(PARTY_OFFSET, BATTLE_OFFSET, MOVE_STATS_OFFSET)

-- Register our callback to be executed every frame
gui.register(callback)
