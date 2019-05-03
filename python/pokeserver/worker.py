import os
import hashlib
import requests
import base64
from collections import defaultdict
from io import BytesIO

from pokedata.nds.party import read_party_data
from pokedata.nds.battle import read_battle_data
from pokedata.nds.moves import read_move_stats
from pokedata.nds.screenshot import extract_sprite, get_pokemon_types, get_move_types

__data_dir__ = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'nds', 'dump'))
__party_bin_path__ = os.path.join(__data_dir__, 'party.bin')
__battle_bin_path__ = os.path.join(__data_dir__, 'battle.bin')
__dump_writeflag__ = os.path.join(__data_dir__, 'dump.writeflag')
__screenshot_writeflag__ = os.path.join(__data_dir__, 'screenshot.writeflag')


class WriteFlag(object):

    def __init__(self, path):
        self.path = path
        self.last_mtime = None

    def check(self):
        try:
            mtime = os.path.getmtime(self.path)
        except (IOError, OSError):
            mtime = None

        if mtime and mtime != self.last_mtime:
            self.last_mtime = mtime
            return True
        return False


class DumpFile(object):

    def __init__(self, path):
        self.path = path
        self.last_digest = None

    def read(self):
        md5 = hashlib.md5()
        try:
            with open(self.path, 'rb') as fp:
                data = fp.read()
                md5.update(data)
        except (IOError, OSError):
            return False, None

        digest = md5.hexdigest()
        if digest != self.last_digest:
            self.last_digest = digest
            return True, data
        return False, data


def get(url):
    port = int(os.getenv('PORT', 5000))
    response = requests.get('http://127.0.0.1:%d%s' % (port, url))
    if response.ok:
        try:
            return response.json()
        except:
            pass
    return None


def post(url, **kwargs):
    port = int(os.getenv('PORT', 5000))
    return requests.post('http://127.0.0.1:%d%s' % (port, url), json=kwargs)


def merge_battle_data_to_party(party, battle_data):
    assert len(party) == len(battle_data)
    new_party = []
    move_stats = {}
    for pokemon, battle_record in zip(party, battle_data):
        if pokemon['block_data']['pokedex_id'] == battle_record['pokedex_id']:
            pokemon['battle_stats']['hp'] = battle_record['hp']
            for i, move in enumerate(battle_record['moves']):
                if move['move_id'] == pokemon['block_data']['move_%d_id' % (i + 1)]:
                    pokemon['block_data']['move_%d_pp' % (i + 1)] = move['pp']
                    move_stats[move['move_id']] = {'pp_max': move['pp_max']}
        new_party.append(pokemon)
    return new_party, move_stats


def image_to_b64(im):
    with BytesIO() as buf:
        im.save(buf, format='png')
        return str(base64.b64encode(buf.getvalue()), 'utf-8')


def run_party_update(party_bin, battle_bin, dump_flag):
    if not dump_flag.check():
        return

    party_changed, party_dump = party_bin.read()
    battle_changed, battle_dump = battle_bin.read()
    if not party_changed and not battle_changed:
        return

    party = read_party_data(party_dump)
    if not party:
        return

    battle_data = read_battle_data(battle_dump, party)
    if battle_data:
        party, move_stats = merge_battle_data_to_party(party, battle_data)
        post('/w/move_stats', move_stats=move_stats)

    post('/w/party', party=party)


def run_screenshot_update(screenshot_flag):
    if not screenshot_flag.check():
        return

    party = get('/api/party')
    if not party:
        return

    pokemon_sprites = {}
    pokemon_types = {}
    move_stats = defaultdict(dict)

    for char_index, pokemon in enumerate(party):
        pokedex_id = pokemon['pokedex_id']

        char_gd = os.path.join(__data_dir__, 'party_%02d_char.gd' % char_index)
        if os.path.isfile(char_gd):
            sprite = extract_sprite(char_gd)
            if sprite:
                pokemon_sprites[pokedex_id] = image_to_b64(sprite)

        type_gd = os.path.join(__data_dir__, 'party_%02d_type.gd' % char_index)
        if os.path.isfile(type_gd):
            element1, element2 = get_pokemon_types(type_gd)
            if element1:
                pokemon_types[pokedex_id] = [element1] + ([element2] if element2 else [])

        moves_gd = os.path.join(__data_dir__, 'party_%02d_moves.gd' % char_index)
        if os.path.isfile(moves_gd):
            move_types = get_move_types(moves_gd)
            if move_types:
                for move_index, move in enumerate(pokemon['moves']):
                    if move_types[move_index] and move['type'] != move_types[move_index]:
                        move_stats[move['id']]['element'] = move_types[move_index]

        for move_index, move in enumerate(pokemon['moves']):
            filename = 'party_%02d_move_%02d.bin' % (char_index, move_index)
            try:
                with open(os.path.join(__data_dir__, filename), 'rb') as fp:
                    move_dump = read_move_stats(fp.read())
                    if move_dump:
                        move_stats[move['id']].update(move_dump)
            except (IOError, OSError):
                continue

    if pokemon_sprites:
        post('/w/pokemon_sprites', pokemon_sprites=pokemon_sprites)

    if pokemon_types:
        post('/w/pokemon_types', pokemon_types=pokemon_types)

    if move_stats:
        post('/w/move_stats', move_stats=move_stats)


def run_worker_thread(quit_flag):

    party_bin = DumpFile(__party_bin_path__)
    battle_bin = DumpFile(__battle_bin_path__)
    dump_flag = WriteFlag(__dump_writeflag__)

    screenshot_flag = WriteFlag(__screenshot_writeflag__)

    while not quit_flag.wait(1.0):
        run_party_update(party_bin, battle_bin, dump_flag)
        run_screenshot_update(screenshot_flag)
