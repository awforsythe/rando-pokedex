import React from 'react';
import PropTypes from 'prop-types';

import './pokemon-stats-display.css';

function PokemonStatsDisplay(props) {
  const { hpMax, attack, defense, speed, spAttack, spDefense } = props;
  return (
    <div className="psd-container">
      <div className="psd-label">HP:</div>
      <div className="psd-value">{hpMax}</div>
      <div className="psd-label">Attack:</div>
      <div className="psd-value">{attack}</div>
      <div className="psd-label">Defense:</div>
      <div className="psd-value">{defense}</div>
      <div className="psd-label">Speed:</div>
      <div className="psd-value">{speed}</div>
      <div className="psd-label">SP. Attack</div>
      <div className="psd-value">{spAttack}</div>
      <div className="psd-label">SP. Defense</div>
      <div className="psd-value">{spDefense}</div>
    </div>
  );
}
PokemonStatsDisplay.propTypes = {
  hp: PropTypes.number,
  hpMax: PropTypes.number,
  attack: PropTypes.number,
  defense: PropTypes.number,
  speed: PropTypes.number,
  spAttack: PropTypes.number,
  spDefense: PropTypes.number,
};

export default PokemonStatsDisplay;
