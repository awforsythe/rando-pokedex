import React from 'react';
import PropTypes from 'prop-types';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Table from 'react-bootstrap/Table';
import Card from 'react-bootstrap/Card'

import SpriteImage from './../common/SpriteImage.jsx';
import TypeBadge from './../common/TypeBadge.jsx';
import PokemonStatsDisplay from './PokemonStatsDisplay.jsx';
import PokemonAbilityDisplay from './PokemonAbilityDisplay.jsx';
import PokemonMoveListing from './PokemonMoveListing.jsx';

import './pokemon-details.css'

function RosterHeadline(props) {
  const { level, nickname, nature, name, pokedexId, types } = props;
  return (
    <div className="pd-headline">
      <div className="pd-headline-level">Lv.</div>
      <div className="pd-headline-level-no">{level}</div>
      <div className="pd-headline-nickname">{nickname}</div>
      <div className="pd-headline-details">
        <div className="pd-headline-details-nature">{nature}</div>
        <div className="pd-headline-details-name">{name}</div>
        <div className="pd-headline-details-dexid">#{pokedexId}</div>
      </div>
      <div className="pd-headline-type"><TypeBadge type={types[0]} hybridType={types[1]} /></div>
    </div>
  );
}
RosterHeadline.propTypes = {
  level: PropTypes.number,
  nickname: PropTypes.string,
  nature: PropTypes.string,
  name: PropTypes.string,
  pokedexId: PropTypes.number,
  types: PropTypes.array,
};

function RosterStats(props) {
  const { hp, hpMax, attack, defense, speed, spAttack, spDefense } = props;
  return (
    <div className="pd-stats">
      <Table className="pd-stats-table" size="sm">
        <thead>
          <tr className="pd-stats-headers">
            <th>Max HP</th>
            <th>Attack</th>
            <th>Defense</th>
            <th>Speed</th>
            <th>SP Atk</th>
            <th>SP Def</th>
          </tr>
        </thead>
        <tbody>
          <tr className="pd-stats-values">
            <td>{hpMax}</td>
            <td>{attack}</td>
            <td>{defense}</td>
            <td>{speed}</td>
            <td>{spAttack}</td>
            <td>{spDefense}</td>
          </tr>
        </tbody>
      </Table>
    </div>
  );
}
RosterStats.propTypes = {
  hp: PropTypes.number,
  hpMax: PropTypes.number,
  attack: PropTypes.number,
  defense: PropTypes.number,
  speed: PropTypes.number,
  spAttack: PropTypes.number,
  spDefense: PropTypes.number,
};

function RosterAbility(props) {
  const { name, text } = props;
  return (
    <div className="pd-ability">
      <span className="pd-ability-name">{name}</span> &mdash; <span className="pd-ability-text">{text}</span>
    </div>
  );
}
RosterAbility.propTypes = {
  name: PropTypes.string,
  text: PropTypes.string,
};

function RosterSprite(props) {
  const { pokedexId, type } = props;
  const className = 'pd-sprite-box' + (type ? ` pd-sprite-background-${type}` : '');
  return (
    <div className={className}>
      <SpriteImage pokedexId={pokedexId} width={120} height={120} />
    </div>
  );
}
RosterSprite.propTypes = {
  pokedexId: PropTypes.number,
  type: PropTypes.string,
};

function RosterBody(props) {
  const { pokedexId, hp, hpMax, stats, abilityName, abilityText, types } = props;
  const { attack, defense, speed, sp_attack, sp_defense } = stats;
  return (
    <div className="pd-main">
      <div className="pd-body">
        <RosterStats
          hp={hp}
          hpMax={hpMax}
          attack={attack}
          defense={defense}
          speed={speed}
          spAttack={sp_attack}
          spDefense={sp_defense}
        />
        <RosterAbility
          name={abilityName}
          text={abilityText}
        />
      </div>
      <RosterSprite pokedexId={pokedexId} type={types[0]} />
    </div>
  );
}
RosterBody.propTypes = {
  pokedexId: PropTypes.number,
  hp: PropTypes.number,
  hpMax: PropTypes.number,
  stats: PropTypes.object,
  abilityName: PropTypes.string,
  abilityText: PropTypes.string,
  types: PropTypes.array,
}

function PokemonDetails(props) {
  /*
  const { pokemon } = props;
  const { nickname, name, nature, pokedex_id, level, moves, hp, hp_max, stats, ability, ability_text } = pokemon;
  const { attack, defense, speed, sp_attack, sp_defense } = stats;
  return (
    <div className="pd-container">
      <div className="pd-left">
        <div className="pd-image-frame">
          <div className="pd-image-wrapper">
            <SpriteImage pokedexId={pokedex_id} />
          </div>
        </div>
      </div>
      <div className="pd-right">
        <div className="pd-headline">
          <div className="pd-headline-left">
            <span className="pd-nickname">{nickname}</span> / {nature} <span className="pd-emphasis">{name}</span> <span className="pd-parenthetical">(#{pokedex_id})</span>
          </div>
          <div className="pd-headline-right">
            <TypeBadge type={pokemon.types[0]} />
            {pokemon.types.length > 1 ? <TypeBadge type={pokemon.types[1]} /> : null }
            <div className="pd-level">
              Lv. <span className="pd-level-no">{level}</span>
            </div>
          </div>
        </div>
        <PokemonStatsDisplay hp={hp} hpMax={hp_max} attack={attack} defense={defense} speed={speed} spAttack={sp_attack} spDefense={sp_defense} />
        <PokemonAbilityDisplay name={ability} text={ability_text} />
        <PokemonMoveListing moves={moves} />
      </div>
    </div>
  );
  */
  const { pokemon } = props;
  const { level, nickname, nature, name, pokedex_id, types, hp, hp_max, stats, ability, ability_text, moves } = pokemon;
  return (
    <Col className="pd-root" xs={12} xl={6}>
      <RosterHeadline
        level={level}
        nickname={nickname}
        nature={nature}
        name={name}
        pokedexId={pokedex_id}
        types={types}
      />
      <RosterBody
        pokedexId={pokedex_id}
        hp={hp}
        hpMax={hp_max}
        stats={stats}
        abilityName={ability}
        abilityText={ability_text}
        types={types}
      />
      <PokemonMoveListing moves={moves} />
    </Col>
  );
}
PokemonDetails.propTypes = {
  pokemon: PropTypes.object,
};

export default PokemonDetails;
