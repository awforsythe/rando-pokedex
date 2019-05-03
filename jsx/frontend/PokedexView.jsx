import React from 'react';
import io from 'socket.io-client';

import Container from 'react-bootstrap/Container';
import Table from 'react-bootstrap/Table';

import TypeBadge from './common/TypeBadge.jsx';
import SpriteImage from './common/SpriteImage.jsx';

function PokedexTableHeader(props) {
  return (
    <thead>
      <tr>
        <th></th>
        <th>Name</th>
        <th className="text-center">ID</th>
        <th className="text-center">Type</th>
        <th>Description</th>
        <th>Evolution</th>
      </tr>
    </thead>
  )
}

function PokedexRow(props) {
  const { dexinfo } = props;
  const { name, id, element1, element2, evolves_into, text } = dexinfo;
  return (
  <tr>
      <td style={{width: 120, padding: 0}}>
        <SpriteImage pokedexId={id} width={120} height={48} />
      </td>
      <td style={{fontWeight: 500}}>{name}</td>
      <td className="text-center">#{id}</td>
      <td className="text-center">
        <TypeBadge type={element1} hybridType={element2} />
      </td>
      <td><em>{text}</em></td>
      <td>
        {evolves_into ? evolves_into.name : null}
      </td>
    </tr>
  );
}

class PokedexListing extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoading: true,
      error: null,
      dexinfos: [],
    };
    this.socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
  }

  componentDidMount() {
    this.fetchPokedex();
    this.socket.on('pokedex_changed', this.onPokedexChanged);
  }

  componentWillUnmount() {
    this.socket.off('pokedex_changed', this.onPokedexChanged);
  }

  fetchPokedex() {
    this.setState({ isLoading: true });
    fetch('/api/pokedex')
      .then(response => response.json())
      .then(data => this.setState({ isLoading: false, error: null, dexinfos: data }))
      .catch(error => this.setState({ isLoading: false, error }));
  }

  onPokedexChanged = (dexinfo) => {
    const { dexinfos } = this.state;
    const index = dexinfos.findIndex(x => x.id === dexinfo.id);
    if (index >= 0) {
      this.setState({
        dexinfos: dexinfos.slice(0, index).concat([dexinfo]).concat(dexinfos.slice(index + 1)),
      });
    } else {
      let insertAt = 0;
      for (const [i, v] of dexinfos.entries()) {
        if (v.localeCompare(dexinfo.name) > 0) {
          insertAt = i;
          break;
        }
      }
      this.setState({
        dexinfos: dexinfos.slice(0, insertAt).concat([dexinfo]).concat(dexinfos.slice(insertAt)),
      });
    }
  };

  render() {
    const { dexinfos } = this.state;
    return (
      <Table size="sm">
        <PokedexTableHeader />
        <tbody>
          { dexinfos.map(dexinfo => <PokedexRow key={dexinfo.id} dexinfo={dexinfo} />) }
        </tbody>
      </Table>
    );
  }
}

function PokedexView(props) {
  return (
    <Container fluid>
      <PokedexListing />
    </Container>
  );
}

export default PokedexView;
