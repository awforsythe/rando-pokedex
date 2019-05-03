from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from pokedata.nds.constants import (
    __nature_names__,
    __pokemon_names__,
    __pokemon_texts__,
    __ability_names__,
    __ability_texts__,
    __move_names__,
    __move_texts__,
    __item_names__,
)


class MoveInfo(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    move_id = db.Column(db.Integer, unique=True, nullable=False)
    element = db.Column(db.Text)
    category = db.Column(db.Integer)
    power = db.Column(db.Integer)
    accuracy = db.Column(db.Integer)
    pp_max = db.Column(db.Integer)

    def serialize(self):
        return {
            'id': self.move_id,
            'element': self.element,
            'category': self.category,
            'power': self.power,
            'accuracy': self.accuracy,
            'pp_max': self.pp_max,
            'name': __move_names__[self.move_id] if self.move_id < len(__move_names__) else None,
            'text': __move_texts__[self.move_id] if self.move_id < len(__move_texts__) else None,
        }


class PokedexInfo(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    pokedex_id = db.Column(db.Integer, unique=True, nullable=False)
    element1 = db.Column(db.Text)
    element2 = db.Column(db.Text)
    evolves_into_dexid = db.Column(db.Integer)
    sprite_data = db.Column(db.Text)

    def serialize(self):
        name = __pokemon_names__[self.pokedex_id] if self.pokedex_id < len(__pokemon_names__) else None
        text = __pokemon_texts__[self.pokedex_id] if self.pokedex_id < len(__pokemon_texts__) else None
        evolves_into = None
        if self.evolves_into_dexid:
            evolves_into = {
                'pokedex_id': self.evolves_into_dexid,
                'name':__pokemon_names__[self.evolves_into_dexid] if self.evolves_into_dexid < len(__pokemon_names__) else None,
            }
        return {
            'id': self.pokedex_id,
            'name': name,
            'text': text,
            'element1': self.element1,
            'element2': self.element2,
            'evolves_into': evolves_into,
        }


class Party(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    pid0 = db.Column(db.BigInteger)
    pid1 = db.Column(db.BigInteger)
    pid2 = db.Column(db.BigInteger)
    pid3 = db.Column(db.BigInteger)
    pid4 = db.Column(db.BigInteger)
    pid5 = db.Column(db.BigInteger)

    def get_pid(self, i):
        if i == 0:
            return self.pid0
        elif i == 1:
            return self.pid1
        elif i == 2:
            return self.pid2
        elif i == 3:
            return self.pid3
        elif i == 4:
            return self.pid4
        elif i == 5:
            return self.pid5

    def set_pid(self, i, pid):
        if i == 0:
            self.pid0 = pid
        elif i == 1:
            self.pid1 = pid
        elif i == 2:
            self.pid2 = pid
        elif i == 3:
            self.pid3 = pid
        elif i == 4:
            self.pid4 = pid
        elif i == 5:
            self.pid5 = pid
        return self

    def serialize(self):
        party = []
        for pid in [self.pid0, self.pid1, self.pid2, self.pid3, self.pid4, self.pid5]:
            pokemon = Pokemon.query.filter_by(pid=pid).first()
            if pokemon:
                party.append(pokemon.serialize())
        return party


class Pokemon(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime, nullable=False)
    pid = db.Column(db.BigInteger, unique=True, nullable=False)
    pokedex_id = db.Column(db.Integer, nullable=False)
    ability_id = db.Column(db.Integer, nullable=False)
    nature_id = db.Column(db.Integer, nullable=False)
    held_item_id = db.Column(db.Integer, nullable=False)
    level = db.Column(db.Integer, nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    nickname = db.Column(db.Text, nullable=False)
    hp = db.Column(db.Integer, nullable=False)
    hp_max = db.Column(db.Integer, nullable=False)
    attack = db.Column(db.Integer, nullable=False)
    defense = db.Column(db.Integer, nullable=False)
    speed = db.Column(db.Integer, nullable=False)
    sp_attack = db.Column(db.Integer, nullable=False)
    sp_defense = db.Column(db.Integer, nullable=False)
    move_1_id = db.Column(db.Integer)
    move_2_id = db.Column(db.Integer)
    move_3_id = db.Column(db.Integer)
    move_4_id = db.Column(db.Integer)
    move_1_pp = db.Column(db.Integer)
    move_2_pp = db.Column(db.Integer)
    move_3_pp = db.Column(db.Integer)
    move_4_pp = db.Column(db.Integer)

    def serialize(self):
        types = []
        evolves_into = None
        dex_obj = PokedexInfo.query.filter_by(pokedex_id=self.pokedex_id).first()
        if dex_obj:
            if dex_obj.element1:
                types.append(dex_obj.element1)
            if dex_obj.element2:
                types.append(dex_obj.element2)
            if dex_obj.evolves_into_dexid:
                evolves_into = {
                    'pokedex_id': dex_obj.evolves_into_dexid,
                    'name': __pokemon_names__[dex_obj.evolves_into_dexid] if dex_obj.evolves_into_dexid < len(__pokemon_names__) else None,
                }

        moves = []
        for move_id, pp in zip([self.move_1_id, self.move_2_id, self.move_3_id, self.move_4_id], [self.move_1_pp, self.move_2_pp, self.move_3_pp, self.move_4_pp]):
            if move_id:
                move_obj = MoveInfo.query.filter_by(move_id=move_id).first()
                moves.append({
                    'id': move_id,
                    'pp': pp,
                    'name': __move_names__[move_id] if move_id < len(__move_names__) else None,
                    'text': __move_texts__[move_id] if move_id < len(__move_texts__) else None,
                    'type': move_obj.element if move_obj else None,
                    'category': move_obj.category if move_obj else None,
                    'power': move_obj.power if move_obj else None,
                    'accuracy': move_obj.accuracy if move_obj else None,
                    'pp_max': move_obj.pp_max if move_obj else None,
                })

        pokemon_name = __pokemon_names__[self.pokedex_id] if self.pokedex_id < len(__pokemon_names__) else None
        ability_name = __ability_names__[self.ability_id] if self.ability_id < len(__ability_names__) else None
        ability_text = __ability_texts__[self.ability_id] if self.ability_id < len(__ability_texts__) else None
        nature_name = __nature_names__[self.nature_id] if self.nature_id < len(__nature_names__) else None
        held_item_name = __item_names__[self.held_item_id] if self.held_item_id < len(__item_names__) else None

        return {
            'id': self.id,
            'pid': self.pid,
            'pokedex_id': self.pokedex_id,
            'level': self.level,
            'experience': self.experience,
            'name': pokemon_name,
            'nickname': self.nickname,
            'ability': ability_name,
            'ability_text': ability_text,
            'nature': nature_name,
            'held_item': held_item_name,
            'types': types,
            'moves': moves,
            'hp': self.hp,
            'hp_max': self.hp_max,
            'stats': {
                'attack': self.attack,
                'defense': self.defense,
                'speed': self.speed,
                'sp_attack': self.sp_attack,
                'sp_defense': self.sp_defense,
            },
        }
