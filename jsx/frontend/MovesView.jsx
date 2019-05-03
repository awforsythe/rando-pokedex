import React from 'react';
import io from 'socket.io-client';

import Container from 'react-bootstrap/Container';
import Table from 'react-bootstrap/Table';

import TypeBadge from './common/TypeBadge.jsx';
import CategoryBadge from './common/CategoryBadge.jsx';

function MoveTableHeader(props) {
  return (
    <thead>
      <tr>
        <th>Name</th>
        <th className="text-center">Type</th>
        <th className="text-center">Category</th>
        <th className="text-center">Power</th>
        <th className="text-center">Accuracy</th>
        <th className="text-center">PP</th>
        <th>Description</th>
      </tr>
    </thead>
  )
}

function MoveRow(props) {
  const { move } = props;
  const { name, element, pp_max, category, power, accuracy, text } = move;
  return (
  <tr>
      <td style={{fontWeight: 500, whiteSpace: 'nowrap'}}>{name}</td>
      <td className="text-center"><TypeBadge type={element} /></td>
      <td className="text-center"><CategoryBadge category={category} /></td>
      <td className="text-center">{power == 0 ? '--' : power}</td>
      <td className="text-center">{accuracy}</td>
      <td className="text-center">{pp_max}</td>
      <td><em>{text}</em></td>
    </tr>
  );
}

class MoveListing extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoading: true,
      error: null,
      moves: [],
    };
    this.socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
  }

  componentDidMount() {
    this.fetchMoves();
    this.socket.on('move_changed', this.onMoveChanged);
  }

  componentWillUnmount() {
    this.socket.off('move_changed', this.onMoveChanged);
  }

  fetchMoves() {
    this.setState({ isLoading: true });
    fetch('/api/moves')
      .then(response => response.json())
      .then(data => this.setState({ isLoading: false, error: null, moves: data }))
      .catch(error => this.setState({ isLoading: false, error }));
  }

  onMoveChanged = (move) => {
    const { moves } = this.state;
    const index = moves.findIndex(x => x.id === move.id);
    if (index >= 0) {
      this.setState({
        moves: moves.slice(0, index).concat([move]).concat(moves.slice(index + 1)),
      });
    } else {
      let insertAt = 0;
      for (const [i, v] of moves.entries()) {
        if (v.localeCompare(move.name) > 0) {
          insertAt = i;
          break;
        }
      }
      this.setState({
        moves: moves.slice(0, insertAt).concat([move]).concat(moves.slice(insertAt)),
      });
    }
  };

  render() {
    const { moves } = this.state;
    return (
      <Table size="sm">
        <MoveTableHeader />
        <tbody>
          { moves.map(move => <MoveRow key={move.id} move={move} />) }
        </tbody>
      </Table>
    );
  }
}

function MovesView(props) {
  return (
    <Container fluid>
      <MoveListing />
    </Container>
  );
}

export default MovesView;
