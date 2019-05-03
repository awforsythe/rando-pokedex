import React from 'react';
import PropTypes from 'prop-types';

import './type-badge.css';

function sanitizeType(type) {
  if (type) {
    if (type.toLowerCase() == 'bug') return 'bug';
    if (type.toLowerCase() == 'dark') return 'dark';
    if (type.toLowerCase() == 'dragon') return 'dragon';
    if (type.toLowerCase() == 'electric') return 'electric';
    if (type.toLowerCase() == 'fighting') return 'fighting';
    if (type.toLowerCase() == 'fire') return 'fire';
    if (type.toLowerCase() == 'flying') return 'flying';
    if (type.toLowerCase() == 'ghost') return 'ghost';
    if (type.toLowerCase() == 'grass') return 'grass';
    if (type.toLowerCase() == 'ground') return 'ground';
    if (type.toLowerCase() == 'ice') return 'ice';
    if (type.toLowerCase() == 'normal') return 'normal';
    if (type.toLowerCase() == 'poison') return 'poison';
    if (type.toLowerCase() == 'psychic') return 'psychic';
    if (type.toLowerCase() == 'rock') return 'rock';
    if (type.toLowerCase() == 'steel') return 'steel';
    if (type.toLowerCase() == 'water') return 'water';
  }
  return 'unknown';
}

function TypeBadge(props) {
  const { type, hybridType, small } = props;
  const sanitized = sanitizeType(type);
  if (hybridType) {
    const sanitizedHybrid = sanitizeType(hybridType);
    const className = 'type-badge-hybrid' + (small ? ' type-badge-small' : '');
    return (
      <div className={className}>
        <div className={`hybrid-type-left type-badge-${sanitized}`}>
          {sanitized.toUpperCase()}
        </div>
        <div className={`hybrid-type-right type-badge-${sanitizedHybrid}`}>
          {sanitizedHybrid.toUpperCase()}
        </div>
      </div>
    );
  }
  const className = `type-badge type-badge-${sanitized}` + (small ? ' type-badge-small' : '');
  const displayText = sanitized == 'unknown' ? '¯\\_(ツ)_/¯' : sanitized.toUpperCase();
  return <div className={className}>{displayText}</div>;
}
TypeBadge.propTypes = {
  type: PropTypes.string,
  hybridType: PropTypes.string,
  small: PropTypes.bool,
};

export default TypeBadge;
