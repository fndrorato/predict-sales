import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

const CustomCheckboxFilter = ({ column, filterChangedCallback, api }) => {
  const [selectedValues, setSelectedValues] = useState([]);
  const [options, setOptions] = useState([]);

  useEffect(() => {
    // Obtém valores únicos da coluna
    const uniqueValues = new Set();
    api.forEachNode((node) => {
      if (node.data[column.colId]) {
        uniqueValues.add(node.data[column.colId]);
      }
    });
    setOptions(Array.from(uniqueValues));
  }, [api, column]);

  const onCheckboxChange = (value) => {
    let newSelected = [...selectedValues];
    if (newSelected.includes(value)) {
      newSelected = newSelected.filter((v) => v !== value);
    } else {
      newSelected.push(value);
    }
    setSelectedValues(newSelected);
    filterChangedCallback(); // Notifica o AG Grid que o filtro mudou
  };

  return (
    <div style={{ padding: '5px' }}>
      {options.map((value) => (
        <label key={value} style={{ display: 'block' }}>
          <input
            type="checkbox"
            checked={selectedValues.includes(value)}
            onChange={() => onCheckboxChange(value)}
          />
          {value}
        </label>
      ))}
    </div>
  );
};

CustomCheckboxFilter.propTypes = {
  column: PropTypes.shape({
    colId: PropTypes.string.isRequired
  }).isRequired,
  filterChangedCallback: PropTypes.func.isRequired,
  api: PropTypes.shape({
    forEachNode: PropTypes.func.isRequired
  }).isRequired
};

export default CustomCheckboxFilter;
