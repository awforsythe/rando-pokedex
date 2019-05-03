import os

from pokedata.util import chunks, unpack

__battle_record_size__ = 548
__battle_record_format__ = [
    (0x00, 2, 'pokedex_id'),
    (0x02, 2, 'hp_max'),
    (0x04, 2, 'hp'),
]
__battle_record_move_base__ = 248
__battle_record_move_offset__ = 14
__battle_record_move_format__ = [
    (0x00, 2, 'move_id'),
    (0x02, 1, 'pp'),
    (0x03, 1, 'pp_max'),
]
__battle_dump_size__ = __battle_record_size__ * 6


def read_battle_record(data, party_member):
    result = unpack(__battle_record_format__, data)
    if result['pokedex_id'] != party_member['block_data']['pokedex_id']:
        return None

    moves = []
    for move_index in range(4):
        expected_move_id = party_member['block_data']['move_%d_id' % (move_index + 1)]
        if not expected_move_id:
            break
        offset = __battle_record_move_base__ + (move_index * __battle_record_move_offset__)
        move = unpack(__battle_record_move_format__, data[offset:])
        if move['move_id'] != expected_move_id:
            break
        moves.append(move)

    result['moves'] = moves
    return result


def read_battle_data(data, party):
    if not data or len(data) != __battle_dump_size__ or not party:
        return None

    results = []
    for i, chunk in enumerate(chunks(data, __battle_record_size__)):
        if i >= len(party):
            break

        record = read_battle_record(chunk, party[i])
        if not record:
            break

        results.append(record)

    return results if len(results) == len(party) else None
