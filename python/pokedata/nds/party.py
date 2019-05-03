import os
import struct

from pokedata.util import chunks, unpack

__block_orders__ = ['ABCD', 'ABDC', 'ACBD', 'ACDB', 'ADBC', 'ADCB', 'BACD', 'BADC', 'BCAD', 'BCDA', 'BDAC', 'BDCA', 'CABD', 'CADB', 'CBAD', 'CBDA', 'CDAB', 'CDBA', 'DABC', 'DACB', 'DBAC', 'DBCA', 'DCAB', 'DCBA']
__block_size__ = 32


def decode_str(x):
    s = ''
    for wchar in chunks(x, 2):
        if wchar == b'\xff\xff':
            break
        char = wchar.decode('utf-16')
        if ord(char) < 1000:
            s += wchar.decode('utf-16')
    return s


def decode_date(x):
    return struct.unpack('BBB', x)


__header_offset__ = 0
__header_size__ = 8
__header_format__ = [
    (0x00, 4, 'pid'),
    (0x00, 4, 'shift', lambda x: ((struct.unpack('I', x)[0] & 0x3e000) >> 0xd) % 24),
    (0x06, 2, 'checksum'),
]

__block_data_offset__ = __header_size__
__block_data_size__ = 128
__block_data_format__ = [
    (0x00, 2, 'pokedex_id'),
    (0x02, 2, 'held_item'),
    (0x04, 2, 'ot_id'),
    (0x06, 2, 'ot_secret_id'),
    (0x08, 4, 'experience'),
    (0x0c, 1, 'friendship_or_steps'),
    (0x0d, 1, 'ability'),
    (0x0e, 1, 'markings'),
    (0x0f, 1, 'original_language'),
    (0x10, 1, 'ev_hp'),
    (0x11, 1, 'ev_attack'),
    (0x12, 1, 'ev_defense'),
    (0x13, 1, 'ev_speed'),
    (0x14, 1, 'ev_sp_attack'),
    (0x15, 1, 'ev_sp_defense'),
    (0x16, 1, 'cv_cool'),
    (0x17, 1, 'cv_beauty'),
    (0x18, 1, 'cv_cute'),
    (0x19, 1, 'cv_smart'),
    (0x1a, 1, 'cv_tough'),
    (0x1b, 1, 'cv_sheen'),
    (0x1c, 2, 'sinnoh_ribbon_set_1'),
    (0x1e, 2, 'unova_ribbon_set'),
    (0x20, 2, 'move_1_id'),
    (0x22, 2, 'move_2_id'),
    (0x24, 2, 'move_3_id'),
    (0x26, 2, 'move_4_id'),
    (0x28, 1, 'move_1_pp'),
    (0x29, 1, 'move_2_pp'),
    (0x2a, 1, 'move_3_pp'),
    (0x2b, 1, 'move_4_pp'),
    (0x2c, 4, 'move_pp_ups'),
    (0x30, 4, 'iv_field'),
    (0x34, 2, 'hoenn_ribbon_set_1'),
    (0x36, 2, 'hoenn_ribbon_set_2'),
    (0x38, 1, 'gender_form_bits'),
    (0x39, 1, 'nature'),
    (0x3a, 1, 'dream_flags'),
    (0x40, 22, 'nickname', decode_str),
    (0x57, 1, 'origin_game'),
    (0x58, 2, 'sinnoh_ribbon_set_3'),
    (0x5a, 2, 'sinnoh_ribbon_set_4'),
    (0x60, 16, 'ot_name', decode_str),
    (0x70, 3, 'date_egg_received', decode_date),
    (0x73, 3, 'date_met', decode_date),
    (0x76, 2, 'egg_location'),
    (0x78, 2, 'met_location'),
    (0x7a, 1, 'pokerus'),
    (0x7b, 1, 'poke_ball'),
    (0x7c, 1, 'met_level_ot_gender'),
    (0x7d, 1, 'encounter_type'),
]

__battle_stats_offset__ = __block_data_offset__ + __block_data_size__
__battle_stats_size__ = 84
__battle_stats_format__ = [
    (0x00, 1, 'status_flags'),
    (0x04, 1, 'level'),
    (0x05, 1, 'capsule_index'),
    (0x06, 2, 'hp'),
    (0x08, 2, 'hp_max'),
    (0x0a, 2, 'attack'),
    (0x0c, 2, 'defense'),
    (0x0e, 2, 'speed'),
    (0x10, 2, 'sp_attack'),
    (0x12, 2, 'sp_defense'),
]

__record_size__ = 220
__party_size__ = 6
__party_dump_size__ = __record_size__ * __party_size__

assert __header_size__ + __block_data_size__ + __battle_stats_size__ == __record_size__
assert __battle_stats_offset__ + __battle_stats_size__ == __record_size__


class PRNG(object):

    def __init__(self, seed):
        self.value = seed

    def next(self):
        self.value = (0x41c64e6d * self.value + 0x6073) & 0xffffffff
        return self.value


def decrypt_block_data(header, encrypted_block_data):
    num_values = __block_data_size__ // struct.calcsize('H')
    fmt = 'H' * num_values

    prng = PRNG(header['checksum'])
    values = [x ^ (prng.next() >> 16) for x in struct.unpack(fmt, encrypted_block_data)]

    block_order = __block_orders__[header['shift']]
    blocks = list(chunks(values, num_values // len(block_order)))
    shuffled_blocks = [blocks[block_order.index(x)] for x in 'ABCD']
    shuffled_values = [value for block in shuffled_blocks for value in block]
    return struct.pack(fmt, *shuffled_values)


def decrypt_battle_stats(header, encrypted_battle_stats):
    num_values = __battle_stats_size__ // struct.calcsize('H')
    fmt = '<' + ('H' * num_values)

    prng = PRNG(header['pid'])
    values = [x ^ (prng.next() >> 16) for x in struct.unpack(fmt, encrypted_battle_stats)]
    return struct.pack(fmt, *values)


def read_party_data(data):
    if not data or len(data) != __party_dump_size__:
        return None

    party = []
    for chunk in chunks(data, __record_size__):
        header_data = chunk[__header_offset__:__header_offset__ + __header_size__]
        encrypted_block_data = chunk[__block_data_offset__:__block_data_offset__ + __block_data_size__]
        encrypted_battle_stats = chunk[__battle_stats_offset__:__battle_stats_offset__ + __battle_stats_size__]

        try:
            header = unpack(__header_format__, header_data)
            block_data = unpack(__block_data_format__, decrypt_block_data(header, encrypted_block_data))
            battle_stats = unpack(__battle_stats_format__, decrypt_battle_stats(header, encrypted_battle_stats))
        except UnicodeDecodeError:
            return []

        if not header['checksum']:
            continue

        party.append({
            'header': header,
            'block_data': block_data,
            'battle_stats': battle_stats,
        })

    return party
