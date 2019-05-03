import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router, Route, Redirect } from 'react-router-dom';
import PropTypes from 'prop-types';
import io from 'socket.io-client';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import NavigationBar from './frontend/NavigationBar.jsx';
import RosterView from './frontend/RosterView.jsx';
import PokedexView from './frontend/PokedexView.jsx';
import MovesView from './frontend/MovesView.jsx';

import '../node_modules/bootstrap/dist/css/bootstrap.min.css';

function App(props) {
  return (
    <Router>
      <NavigationBar />
      <Route path="/" exact render={() => (
        <Redirect to="/roster" />
      )}/>
      <Route path="/roster" component={RosterView} />
      <Route path="/pokedex" component={PokedexView} />
      <Route path="/moves" component={MovesView} />
    </Router>
  );
}

ReactDOM.render(<App />, document.querySelector('#main'));
