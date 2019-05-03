import React from 'react';
import PropTypes from 'prop-types';

function parseCategory(category) {
  if (category == 2) {
    return 'Special';
  }
  if (category == 1) {
    return 'Physical';
  }
  if (category == 0) {
    return 'Status';
  }
  return '';
}

function getCategoryStyle(category) {
  if (category == 2) {
    return {fontWeight: 500, color: '#5167a1'};
  }
  if (category == 1) {
    return {fontWeight: 500, color: '#a21b0d'};
  }
  if (category == 0) {
    return {fontWeight: 500, color: '#969296'};
  }
  return {};
}

function CategoryBadge(props) {
  const { category } = props;
  const displayText = parseCategory(category);
  const style = getCategoryStyle(category);
  return <span style={style}>{displayText}</span>;
}
CategoryBadge.propTypes = {
  category: PropTypes.number,
};

export default CategoryBadge;
