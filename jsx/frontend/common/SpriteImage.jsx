import React from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';
import io from 'socket.io-client';

function getSpriteStyle(width, height) {
  if (!width && !height) {
    return {}
  }
  let result = {objectFit: 'none'};
  if (width) {
    result.width = width;
  }
  if (height) {
    result.height = height;
  }
  return result;
}

class SpriteImage extends React.Component {
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
    const { pokedexId, width, height } = this.props;
    return (
      <img
        style={getSpriteStyle(width, height)}
        src={`/img/sprite/${pokedexId}`}
      />
    );
  }
}
SpriteImage.propTypes = {
  pokedexId: PropTypes.number.isRequired,
  width: PropTypes.number,
  height: PropTypes.number,
};

export default SpriteImage;
