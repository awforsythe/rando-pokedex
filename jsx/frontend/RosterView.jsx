import React from 'react';

import Container from 'react-bootstrap/Container';

import PartyListing from './roster/PartyListing.jsx';
import ReserveListing from './roster/ReserveListing.jsx';

function RosterView(props) {
  return (
    <Container fluid>
      <PartyListing />
      <ReserveListing />
    </Container>
  );
}

export default RosterView;
