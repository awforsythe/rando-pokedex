import React from 'react';
import PropTypes from 'prop-types';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';

import TwitchButton from './TwitchButton.jsx';

function InfoModal(props) {
  const { show, onHide, twitchUsername, gameDescription } = props;
  const prefix = twitchUsername ? `${twitchUsername}'s` : 'a';
  const game = gameDescription || 'Pokémon';
  return (
    <Modal show={show} onHide={onHide} size="lg" centered>
      <Modal.Body>
        <Container>
          <Row>
            <h4>About this site</h4>
            <p>
              This site displays real-time information about {prefix} {game} run.
              You can use these pages to stay up-to-date with the Pokémon
              and moves seen so far.
            </p>
            <ul>
              <li><b>Roster:</b> All Pokémon captured so far, both in and out of the party.</li>
              <li><b>Pokédex:</b> Information about all Pokémon captured, organized by type.</li>
              <li><b>Moves:</b> Information about all moves learned, with their types and stats.</li>
            </ul>
            <p>
              The data shown on this site is pulled directly from the game.
              These pages should update automatically as the game progresses,
              but if anything looks wrong or stops updating, just press Ctrl+F5.
            </p>
            <p>
              <small>Developed by <a href="https://twitter.com/alexforsythe" target="_blank">Alex Forsythe</a></small>.
            </p>
            <br />
          </Row>
          <Row>
            { twitchUsername && <Col><TwitchButton username={twitchUsername} /></Col> }
            <Col>
              <Button variant="secondary" className="btn-block" onClick={onHide}>Close</Button>
            </Col>
          </Row>
        </Container>
      </Modal.Body>
    </Modal>
  );
}
InfoModal.propTypes = {
  show: PropTypes.bool.isRequired,
  onHide: PropTypes.func.isRequired,
  twitchUsername: PropTypes.string,
  gameDescription: PropTypes.string,
};

export default InfoModal;
