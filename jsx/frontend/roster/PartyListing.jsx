import React from 'react';
import PropTypes from 'prop-types';
import io from 'socket.io-client';

import Row from 'react-bootstrap/Row';

import PokemonDetails from './PokemonDetails.jsx';

class PartyListing extends React.Component {
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
      <Row style={{marginTop: 8}}>
        { members.map(member => <PokemonDetails key={member.pid} pokemon={member} />) }
      </Row>
    );
  }
};

export default PartyListing;
