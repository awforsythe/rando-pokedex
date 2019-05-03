import React from 'react';
import PropTypes from 'prop-types';
import io from 'socket.io-client';

import Row from 'react-bootstrap/Row';

import PokemonDetails from './PokemonDetails.jsx';

class ReserveListing extends React.Component {
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
    this.fetchReserve();
    this.socket.on('reserve_composition_changed', this.onReserveCompositionChanged);
    this.socket.on('pokemon_changed', this.onPokemonChanged);
  }

  componentWillUnmount() {
    this.socket.off('reserve_composition_changed', this.onReserveCompositionChanged);
    this.socket.off('pokemon_changed', this.onPokemonChanged);
  }

  fetchReserve() {
    this.setState({ isLoading: true });
    fetch('/api/reserve')
      .then(response => response.json())
      .then(data => this.setState({ isLoading: false, error: null, members: data }))
      .catch(error => this.setState({ isLoading: false, error }));
  }

  onReserveCompositionChanged = () => {
    this.fetchReserve();
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
    if (!members || members.length <= 0) {
      return null;
    }
    return (
      <React.Fragment>
        <h5 style={{marginTop: 16}}>Reserve Pokémon</h5>
        <Row>
          { members.map(member => <PokemonDetails key={member.pid} pokemon={member} />) }
        </Row>
      </React.Fragment>
    );
  }
};

export default ReserveListing;
