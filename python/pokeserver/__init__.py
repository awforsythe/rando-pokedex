import eventlet
eventlet.monkey_patch()

import os
import sys

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

import base64
import datetime
import requests
import copy
from io import BytesIO

from flask import Flask, jsonify, make_response, render_template, request, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

from worker import run_worker_thread

app = Flask(__name__)
app.config.from_pyfile('config.py')

instance_config_path = os.path.join(os.path.dirname(__file__), '..', 'instance', 'config.py')
if os.path.isfile(instance_config_path):
    app.config.from_pyfile(instance_config_path)

for key in ('DEBUG', 'SQLALCHEMY_TRACK_MODIFICATIONS', 'VALIDATE_POST_REQUESTS', 'FORWARD_POST_REQUESTS'):
    value = os.getenv(key)
    if value and value.lower() in ('true', 'false'):
        app.config[key] = value.lower() == 'true'

for key in ('API_SECRET', 'FORWARD_TO', 'TWITCH_USERNAME', 'GAME_DESCRIPTION'):
    value = os.getenv(key)
    if value is not None:
        app.config[key] = value

database_url = os.getenv('DATABASE_URL')
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url


__forwarder_queue__ = None
if app.config.get('FORWARD_POST_REQUESTS'):
    __forwarder_queue__ = eventlet.queue.Queue()

def run_forwarder_thread(flag):
    while not flag.wait(0.01):
        try:
            item = __forwarder_queue__.get_nowait()
            url, json, timeout = item
            try:
                requests.post(url, json=json, timeout=timeout)
            except:
                pass
        except eventlet.queue.Empty:
            pass


from models import db, MoveInfo, PokedexInfo, Party, Pokemon
from pokedata.nds.constants import __pokemon_names__, __pokemon_texts__, __move_names__, __move_texts__
db.init_app(app)

socketio = SocketIO(app)


def validate_post():
    if app.config.get('VALIDATE_POST_REQUESTS'):
        own_secret = app.config.get('API_SECRET')
        foreign_secret = request.json.get('api_secret')
        if not own_secret or not foreign_secret:
            return False
        if foreign_secret != own_secret:
            return False
    return True


def forward_post(url, timeout=0.1):
    if app.config.get('FORWARD_POST_REQUESTS') and __forwarder_queue__:
        forwarded_json = copy.deepcopy(request.json)
        forwarded_json['api_secret'] = app.config.get('API_SECRET')
        __forwarder_queue__.put((app.config.get('FORWARD_TO') + url, forwarded_json, timeout))


@app.route('/w/party', methods=['POST'])
def w_party():
    if not validate_post():
        return '', 403

    party = request.json.get('party')
    if not party:
        return '', 204

    party_obj = Party.query.first() or Party()
    old_party_pids = [party_obj.get_pid(i) for i in range(6)]

    updated_pokemon = []
    updated_dexinfo = []

    with db.session.no_autoflush:
        for i, pokemon in enumerate(party + ([None] * (6 - len(party)))):
            pid = pokemon['header']['pid'] if pokemon else None
            party_obj.set_pid(i, pid)

            if pid:
                updated_current = False

                pokemon_obj = Pokemon.query.filter_by(pid=pid).first() or Pokemon(pid=pid, created_time=datetime.datetime.utcnow())
                old_pokedex_id = pokemon_obj.pokedex_id
                new_pokedex_id = pokemon['block_data']['pokedex_id']

                if old_pokedex_id and new_pokedex_id != old_pokedex_id:
                    old_dex_obj = PokedexInfo.query.filter_by(pokedex_id=old_pokedex_id).first()
                    if old_dex_obj:
                        old_dex_obj.evolves_into_dexid = new_pokedex_id
                        db.session.add(old_dex_obj)
                        updated_dexinfo.append(old_dex_obj)

                if pokemon_obj.pokedex_id != new_pokedex_id:
                    pokemon_obj.pokedex_id = new_pokedex_id
                    updated_current = True

                for attr in ('ability', 'nature', 'held_item'):
                    if getattr(pokemon_obj, '%s_id' % attr) != pokemon['block_data'][attr]:
                        setattr(pokemon_obj, '%s_id' % attr, pokemon['block_data'][attr])
                        updated_current = True

                for attr in ('experience', 'nickname', 'move_1_id', 'move_2_id', 'move_3_id', 'move_4_id', 'move_1_pp', 'move_2_pp', 'move_3_pp', 'move_4_pp'):
                    if getattr(pokemon_obj, attr) != pokemon['block_data'][attr]:
                        setattr(pokemon_obj, attr, pokemon['block_data'][attr])
                        updated_current = True

                for attr in ('level', 'hp', 'hp_max', 'attack', 'defense', 'speed', 'sp_attack', 'sp_defense'):
                    if getattr(pokemon_obj, attr) != pokemon['battle_stats'][attr]:
                        setattr(pokemon_obj, attr, pokemon['battle_stats'][attr])
                        updated_current = True

                if updated_current:
                    db.session.add(pokemon_obj)
                    updated_pokemon.append(pokemon_obj)

        new_party_pids = [party_obj.get_pid(i) for i in range(6)]

        party_composition_changed = new_party_pids != old_party_pids
        reserve_composition_changed = set(new_party_pids) != set(old_party_pids)

        if party_composition_changed:
            db.session.add(party_obj)

    if party_composition_changed or updated_pokemon or updated_dexinfo:
        db.session.commit()
        for pokemon_obj in updated_pokemon:
            socketio.emit('pokemon_changed', pokemon_obj.serialize())
        for dex_obj in updated_dexinfo:
            socketio.emit('pokedex_changed', dex_obj.serialize())
        if party_composition_changed:
            socketio.emit('party_composition_changed')
        if reserve_composition_changed:
            socketio.emit('reserve_composition_changed')

    forward_post('/w/party')
    return '', 204


@app.route('/w/move_stats', methods=['POST'])
def w_move_stats():
    if not validate_post():
        return '', 403

    updated_moves = []
    for move_id, stats in request.json.get('move_stats', {}).items():
        updated_current = False
        move_obj = MoveInfo.query.filter_by(move_id=move_id).first() or MoveInfo(move_id=move_id)

        for attr in ('element', 'category', 'power', 'accuracy', 'pp_max'):
            if attr in stats and getattr(move_obj, attr) != stats[attr]:
                setattr(move_obj, attr, stats[attr])
                updated_current = True

        if updated_current:
            db.session.add(move_obj)
            updated_moves.append(move_obj)

    updated_pokemon = set()
    if updated_moves:
        db.session.commit()
        for move_obj in updated_moves:
            socketio.emit('move_changed', move_obj.serialize())

            q = Pokemon.query.filter(
                (Pokemon.move_1_id == move_obj.move_id) |
                (Pokemon.move_2_id == move_obj.move_id) |
                (Pokemon.move_3_id == move_obj.move_id) |
                (Pokemon.move_4_id == move_obj.move_id))
            for pokemon_obj in q.all():
                updated_pokemon.add(pokemon_obj)

    for pokemon_obj in updated_pokemon:
        socketio.emit('pokemon_changed', pokemon_obj.serialize())

    forward_post('/w/move_stats')
    return '', 204


@app.route('/w/pokemon_types', methods=['POST'])
def w_pokemon_types():
    if not validate_post():
        return '', 403

    updated_dexinfo = []
    updated_pokemon = []
    for pokedex_id, types in request.json.get('pokemon_types', {}).items():
        element1 = types[0]
        element2 = types[1] if len(types) > 1 else None
        dex_obj = PokedexInfo.query.filter_by(pokedex_id=pokedex_id).first() or PokedexInfo(pokedex_id=pokedex_id)
        if dex_obj.element1 != element1 or dex_obj.element2 != element2:
            dex_obj.element1 = element1
            dex_obj.element2 = element2
            db.session.add(dex_obj)
            updated_dexinfo.append(dex_obj)

            for pokemon_obj in Pokemon.query.filter_by(pokedex_id=pokedex_id).all():
                db.session.add(pokemon_obj)
                updated_pokemon.append(pokemon_obj)

    if updated_dexinfo or updated_pokemon:
        db.session.commit()
        for dex_obj in updated_dexinfo:
            socketio.emit('pokedex_changed', dex_obj.serialize())
        for pokemon_obj in updated_pokemon:
            socketio.emit('pokemon_changed', pokemon_obj.serialize())

    forward_post('/w/pokemon_types')
    return '', 204


@app.route('/w/pokemon_sprites', methods=['POST'])
def w_pokemon_sprites():
    if not validate_post():
        return '', 403

    ids_changed = []
    for pokedex_id, sprite_data in request.json.get('pokemon_sprites', {}).items():
        pokedex_id = int(pokedex_id)
        dex_obj = PokedexInfo.query.filter_by(pokedex_id=pokedex_id).first() or PokedexInfo(pokedex_id=pokedex_id)
        dex_obj.sprite_data = sprite_data
        db.session.add(dex_obj)
        ids_changed.append(pokedex_id)

    if ids_changed:
        db.session.commit()
        for pokedex_id in ids_changed:
            socketio.emit('sprite_changed', {'pokedex_id': pokedex_id})

    forward_post('/w/pokemon_sprites', timeout=1.0)
    return '', 204


@app.route('/api/config')
def api_config():
    result = {}

    twitch_username = app.config.get('TWITCH_USERNAME')
    if twitch_username:
        result['twitch_username'] = twitch_username

    game_description = app.config.get('GAME_DESCRIPTION')
    if game_description:
        result['game_description'] = game_description

    return jsonify(result)


@app.route('/api/party')
def api_party():
    party = Party.query.first()
    pids = list(filter(None, [party.get_pid(i) for i in range(6)])) if party else []

    result = []
    for pid in pids:
        pokemon_obj = Pokemon.query.filter_by(pid=pid).first()
        if not pokemon_obj:
            return []
        result.append(pokemon_obj.serialize())
    return jsonify(result)


@app.route('/api/reserve')
def api_reserve():
    party = Party.query.first()
    party_pids = set(filter(None, [party.get_pid(i) for i in range(6)])) if party else set()

    results = []
    for pokemon_obj in Pokemon.query.order_by(Pokemon.level.desc()):
        if pokemon_obj.pid not in party_pids:
            results.append(pokemon_obj.serialize())
    return jsonify(results)


@app.route('/api/pokedex')
def api_pokedex():
    results = [obj.serialize() for obj in PokedexInfo.query.all()]
    results.sort(key=lambda x: x['name'])
    return jsonify(results)


@app.route('/api/pokedex/<int:pokedex_id>')
def api_pokedex_single(pokedex_id):
    dex_obj = PokedexInfo.query.filter_by(pokedex_id=pokedex_id).first()
    if dex_obj:
        return jsonify(dex_obj.serialize())

    if pokedex_id and pokedex_id < len(__pokemon_names__):
        return jsonify({
            'id': pokedex_id,
            'name': __pokemon_names__[pokedex_id],
            'text': __pokemon_texts__[pokedex_id],
            'element1': None,
            'element2': None,
            'evolves_into': None,
        })

    return '', 404


@app.route('/api/moves')
def api_moves():
    results = [obj.serialize() for obj in MoveInfo.query.all()]
    results.sort(key=lambda x: x['name'])
    return jsonify(results)


@app.route('/api/moves/<int:move_id>')
def api_moves_single(move_id):
    move_obj = MoveInfo.query.filter_by(move_id=move_id).first()
    if move_obj:
        return jsonify(move_obj.serialize())

    if move_id and move_id < len(__move_names__):
        return jsonify({
            'id': move_id,
            'pp': None,
            'name': __move_names__[move_id],
            'text': __move_texts__[move_id] if move_id < len(__move_texts__) else None,
            'type': None,
            'category': None,
            'power': None,
            'accuracy': None,
            'pp_max': None,
        })


@app.route('/img/sprite/<int:pokedex_id>')
def img_sprite(pokedex_id):

    UNKNOWN_PNG = 'iVBORw0KGgoAAAANSUhEUgAAADwAAAA8CAYAAAA6/NlyAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyZpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNi1jMTExIDc5LjE1ODMyNSwgMjAxNS8wOS8xMC0wMToxMDoyMCAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENDIDIwMTUgKFdpbmRvd3MpIiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOjIyNTJENzNENkFBQzExRTk5RjVBRUJCMTg3MTZGMTM0IiB4bXBNTTpEb2N1bWVudElEPSJ4bXAuZGlkOjIyNTJENzNFNkFBQzExRTk5RjVBRUJCMTg3MTZGMTM0Ij4gPHhtcE1NOkRlcml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6MjI1MkQ3M0I2QUFDMTFFOTlGNUFFQkIxODcxNkYxMzQiIHN0UmVmOmRvY3VtZW50SUQ9InhtcC5kaWQ6MjI1MkQ3M0M2QUFDMTFFOTlGNUFFQkIxODcxNkYxMzQiLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz5dnrGvAAAL20lEQVR42uRb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'

    dex_obj = PokedexInfo.query.filter_by(pokedex_id=pokedex_id).first()
    if dex_obj and dex_obj.sprite_data:
        sprite_data = dex_obj.sprite_data
        filename = '%d.png' % int(pokedex_id)
    else:
        sprite_data = UNKNOWN_PNG
        filename = 'unknown.png'

    buf = BytesIO()
    buf.write(base64.b64decode(sprite_data))
    buf.seek(0)
    return send_file(buf, mimetype='image/png', cache_timeout=-1)


@app.route('/img/type/<name>')
def img_type(name):

    types_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), 'static', 'types'))

    if os.sep not in os.path.normpath(name):
        filepath = os.path.join(types_dir, '%s.png' % name)
        if os.path.isfile(filepath):
            return send_file(filepath)

    unknown_filepath = os.path.join(types_dir, 'unknown.png')
    if not os.path.isfile(unknown_filepath):
        return make_response('', 404)
    return send_file(unknown_filepath)


@app.route('/')
@app.route('/roster')
@app.route('/pokedex')
@app.route('/moves')
def frontend():
    username = app.config.get('TWITCH_USERNAME')
    prefix = ("%s's" % username) if username else 'Rando'
    page_title = '%s Pokédex' % prefix
    return render_template('frontend.html', page_title=page_title)


@app.route('/hud')
def hud():
    return render_template('hud.html')


if __name__ == '__main__':
    with app.test_request_context():
        db.create_all()

    use_worker = not app.config.get('VALIDATE_POST_REQUESTS')

    if use_worker:
        flag = eventlet.event.Event()
        pool = eventlet.greenpool.GreenPool()
        pool.spawn(run_worker_thread, flag)
        if app.config.get('FORWARD_POST_REQUESTS') and __forwarder_queue__:
            pool.spawn(run_forwarder_thread, flag)

    socketio.run(app, host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=app.config['DEBUG'])

    if use_worker:
        flag.send('done')
        pool.waitall()
