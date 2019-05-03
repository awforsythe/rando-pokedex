import React from 'react';
import PropTypes from 'prop-types';

import Table from 'react-bootstrap/Table';
import Modal from 'react-bootstrap/Modal';

import TypeBadge from './../common/TypeBadge.jsx';
import CategoryBadge from './../common/CategoryBadge.jsx';

import './pokemon-move-listing.css';


class PokemonMoveRow extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      showDescription: false,
    };
    this.descriptionContainer = null;
  }

  openDescription = () => {
    this.setState({ showDescription: true });
  };

  closeDescription = () => {
    this.setState({ showDescription: false });
  };

  render() {
    const { move } = this.props;
    const { type, name, text, category, power, accuracy, pp, pp_max } = move;
    const { showDescription } = this.state;
    return (
      <React.Fragment>
        <tr className="pml-row" onClick={this.openDescription}>
          <td className="pml-col-pp">{pp}</td>
          <td className="pml-col-pp-delim">/</td>
          <td className="pml-col-pp-max">{pp_max}</td>
          <td className="pml-col-name">{name}</td>
          <td className="pml-col-type"><TypeBadge small type={type} /></td>
          <td className="pml-col-category"><CategoryBadge category={category} /></td>
          <td className="pml-col-power">{power == 0 ? '--' : power}</td>
          <td className="pml-col-accuracy">{accuracy}</td>
        </tr>
        <Modal centered show={showDescription} onHide={this.closeDescription}>
          <Modal.Body>
            <h4>{name}</h4>
            <p className="pml-modal-description">{text}</p>
          </Modal.Body>
        </Modal>
      </React.Fragment>
    );
  }
}
PokemonMoveRow.propTypes = {
  move: PropTypes.object,
};

function PokemonMoveListing(props) {
  const { moves, showDescription } = props;
  return (
      <Table hover size="sm">
        <tbody>
          { moves.map(move => (
            <PokemonMoveRow
              key={move.id}
              move={move}
            />
          ))}
        </tbody>
      </Table>
  );
}
PokemonMoveListing.propTypes = {
  moves: PropTypes.array,
};

export default PokemonMoveListing;