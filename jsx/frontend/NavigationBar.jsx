import React from 'react';
import { LinkContainer } from 'react-router-bootstrap';

import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';
import Button from 'react-bootstrap/Button';

import TwitchButton from './navigation/TwitchButton.jsx';
import InfoModal from './navigation/InfoModal.jsx';

class NavigationBar extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      showInfo: false,
      config: {},
      error: null,
    };
  }

  componentDidMount() {
    fetch('/api/config')
      .then(response => response.json())
      .then(data => this.setState({ error: null, config: data }))
      .catch(error => this.setState({ error }));
  }

  handleInfoClick = (evt) => {
    this.setState({ showInfo: true });
  };

  handleInfoHide = (evt) => {
    this.setState({ showInfo: false });
  };

  render() {
    const { showInfo, config } = this.state;
    const { twitch_username, game_description } = config;
    return (
      <Navbar bg="dark" variant="dark">
        <Navbar.Brand>Rando Pokédex</Navbar.Brand>
        <Nav className="mr-auto">
          <LinkContainer to="/roster"><Nav.Link>Roster</Nav.Link></LinkContainer>
          <LinkContainer to="/pokedex"><Nav.Link>Pokédex</Nav.Link></LinkContainer>
          <LinkContainer to="/moves"><Nav.Link>Moves</Nav.Link></LinkContainer>
        </Nav>
        { twitch_username && <TwitchButton username={twitch_username} short /> }
        <Button variant="primary" className="ml-1" onClick={this.handleInfoClick}>Info</Button>
        <InfoModal
          show={showInfo}
          onHide={this.handleInfoHide}
          twitchUsername={twitch_username}
          gameDescription={game_description}
        />
      </Navbar>
    );
  }
}

export default NavigationBar;
