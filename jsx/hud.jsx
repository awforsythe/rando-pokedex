import React from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';
import io from 'socket.io-client';

import 'typeface-oswald';

import './hud/normalize.css';
import './hud/hud.css';

function PartyMemberHeadline(props) {
  const { level, nickname, alive } = props;
  return (
    <div className="party-member-headline">
      <div className={`level ${alive ? '' : 'text-fainted'}`}>{ level }</div>
      <div className={`nickname ${alive ? '' : 'text-fainted'}`}>{ nickname }</div>
    </div>
  );
}
PartyMemberHeadline.propTypes = {
  level: PropTypes.number.isRequired,
  nickname: PropTypes.string.isRequired,
  alive: PropTypes.bool.isRequired,
};

function PokemonTypeBadges(props) {
  const { type1, type2 } = props;
  return (
    <React.Fragment>
      <img className="pokemon-element-1" src={`/img/type/${type1 || 'unknown'}`} />
      {type2 ? <img className="pokemon-element-2" src={`/img/type/${type2}`} /> : null }
    </React.Fragment>
  );
}
PokemonTypeBadges.propTypes = {
  type1: PropTypes.string,
  type2: PropTypes.string,
};

function HealthBar(props) {
  const { current, total } = props;
  const pct = total == 0 ? 0.0 : current / total;
  const cond = pct <= 0.2 ? 'critical' : (pct <= 0.5 ? 'weak' : 'healthy');
  const width = Math.round(pct * 100);
  return (
    <div className="healthbar">
      <div className="bar">
        <div className={`fill bar-${cond}`} style={{width: `${width}%`}} />
      </div>
      <div className={`readout ${current > 0 ? '' : 'text-fainted'}`}>
        { current > 0 ? current : 'FNT'}
      </div>
    </div>
  );
}
HealthBar.propTypes = {
  current: PropTypes.number.isRequired,
  total: PropTypes.number.isRequired,
};

function getMoveColorClass(pp, ppMax, alive) {
  if (!alive) {
    return 'text-fainted';
  }
  if (pp <= 0) {
    return 'text-pp-exhausted';
  }
  if (ppMax) {
    const ppPct = pp / ppMax;
    if (ppPct <= 0.2) {
      return 'text-pp-critical';
    }
    if (ppPct <= 0.5) {
      return 'text-pp-low';
    }
  }
  return '';
}

function MoveLine(props) {
  const { id, name, pp, ppMax, type, alive } = props;
  const colorClass = getMoveColorClass(pp, ppMax, alive);
  return (
    <div className="move-line">
      <img src={`/img/type/${type || 'unknown'}`} />
      <div className="pp-count-wrapper">
        <div className={`pp-count ${colorClass}`}>{pp}</div>
      </div>
      <span className={`move-name ${colorClass}`}>{name}</span>
    </div>
  );
};
MoveLine.propTypes = {
  id: PropTypes.number.isRequired,
  name: PropTypes.string,
  pp: PropTypes.number,
  ppMax: PropTypes.number,
  type: PropTypes.string,
  alive: PropTypes.bool,
};

function MoveDisplay(props) {
  const { moves, alive } = props;
  return (
    <div className="move-display">
      { moves.map(move => <MoveLine key={move.id} id={move.id} name={move.name} pp={move.pp} ppMax={move.pp_max} type={move.type} alive={alive} />) }
    </div>
  );
}
MoveDisplay.propTypes = {
  moves: PropTypes.array,
  alive: PropTypes.bool.isRequired,
};

function NatureLine(props) {
  const { nature, name, ability, alive } = props;
  return (
    <div className={`nature-line ${alive ? '' : 'text-fainted'}`}>
      {nature} {name} &bull; <em>{ability}</em>
    </div>
  );
}
NatureLine.propTypes = {
  nature: PropTypes.string,
  name: PropTypes.string,
  ability: PropTypes.string,
  alive: PropTypes.bool,
};

class PartySprite extends React.Component {
  constructor(props) {
    super(props);
    this.socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
  }

  componentDidMount() {
    this.socket.on('sprite_changed', this.onSpriteChanged);
  }

  componentWillUnmount() {
    this.socket.off('sprite_changed', this.onSpriteChanged);
  }

  onSpriteChanged = (obj) => {
    const { pokedexId } = this.props;
    if (pokedexId == obj.pokedex_id) {
      const node = ReactDOM.findDOMNode(this);
      if (node) {
        node.src = `/img/sprite/${pokedexId}?random=${new Date().getTime()}`;
      }
    }
  };

  render() {
    const { pokedexId } = this.props;
    return (
      <img
        className="sprite"
        src={`/img/sprite/${pokedexId}`}
      />
    );
  }
}
PartySprite.propTypes = {
  pokedexId: PropTypes.number.isRequired,
};

function PartyMember(props) {
  const { member } = props;
  return (
    <div className="party-member">
      <PartySprite pokedexId={member.pokedex_id} />
      <PokemonTypeBadges type1={member.types[0]} type2={member.types.length > 1 ? member.types[1] : null} />
      <PartyMemberHeadline level={member.level} nickname={member.nickname} alive={member.hp > 0} />
      <HealthBar current={member.hp} total={member.hp_max} />
      <MoveDisplay moves={member.moves} alive={member.hp > 0} />
      <NatureLine nature={member.nature} name={member.name} ability={member.ability} alive={member.hp > 0} />
    </div>
  );
}
PartyMember.propTypes = {
  member: PropTypes.object,
};

class Party extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoading: true,
      error: null,
      members: [],
    };
    this.socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
  }

  componentDidMount() {
    this.fetchParty();
    this.socket.on('party_composition_changed', this.onPartyCompositionChanged);
    this.socket.on('pokemon_changed', this.onPokemonChanged);
  }

  componentWillUnmount() {
    this.socket.off('party_composition_changed', this.onPartyCompositionChanged);
    this.socket.off('pokemon_changed', this.onPokemonChanged);
  }

  fetchParty() {
    this.setState({ isLoading: true });
    fetch('/api/party')
      .then(response => response.json())
      .then(data => this.setState({ isLoading: false, error: null, members: data }))
      .catch(error => this.setState({ isLoading: false, error }));
  }

  onPartyCompositionChanged = () => {
    this.fetchParty();
  };

  onPokemonChanged = (newPokemon) => {
    const { members } = this.state;
    const index = members.findIndex(x => x.pid === newPokemon.pid);
    if (index >= 0) {
      this.setState({
        members: members.slice(0, index).concat([newPokemon]).concat(members.slice(index + 1)),
      });
    }
  };

  hasPokemon(pid) {
    const { members } = this.state;
    for (const member of members) {
      if (member.pid === pid) {
        return true;
      }
    }
    return false;
  }

  render() {
    const { members } = this.state;
    return (
      <div id="party-wrapper">
        { members.map(member => <PartyMember key={member.pid} member={member} />) }
      </div>
    );
  }
}
Party.propTypes = {
};

function App(props) {
  return <Party />;
}

ReactDOM.render(<App />, document.querySelector('#main'));
