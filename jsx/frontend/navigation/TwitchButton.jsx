import React from 'react';
import PropTypes from 'prop-types';

import Button from 'react-bootstrap/Button';

import './twitch-button.css';

function TwitchButton(props) {
  const { username, short } = props;
  const className = short ? 'twitch-button' : 'twitch-button btn-block';
  const displayText = short ? `twitch.tv/${username}` : `Watch ${username} on Twitch!`;
  const url = `http://twitch.tv/${username}`;
  return (
    <Button
      variant="primary"
      className={className}
      href={url}
      target="_blank"
    >
      {displayText}
    </Button>
  );
}
TwitchButton.propTypes = {
  username: PropTypes.string.isRequired,
  short: PropTypes.bool,
};

export default TwitchButton;
