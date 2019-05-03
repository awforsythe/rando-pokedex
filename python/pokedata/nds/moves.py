import os

from pokedata.util import unpack

__move_dump_size__ = 3
__move_dump_format__ = [
    (0x00, 1, 'category'),
    (0x01, 1, 'power'),
    (0x02, 1, 'accuracy'),
]

def read_move_stats(data):
    if not data or len(data) != __move_dump_size__:
        return None
    return unpack(__move_dump_format__, data)
