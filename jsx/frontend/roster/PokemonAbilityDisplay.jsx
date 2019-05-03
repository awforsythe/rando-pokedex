import React from 'react';
import PropTypes from 'prop-types';

import './pokemon-ability-display.css';

function PokemonAbilityDisplay(props) {
  const { name, text } = props;
  return (
    <div className="pad-container">
      <span className="pad-label">Ability:</span> <span className="pad-value">{name}</span> &ndash; <span className="pad-flavor">{text}</span>
    </div>
  );
}
PokemonAbilityDisplay.propTypes = {
  name: PropTypes.string,
  text: PropTypes.string,
};

export default PokemonAbilityDisplay;
