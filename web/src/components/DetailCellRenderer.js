import React from 'react';
import PropTypes from 'prop-types';
import { AgGridReact } from 'ag-grid-react';

const DetailCellRenderer = (props) => {
  const detailColumnDefs = [
    { field: 'product_code', headerName: 'Código do Produto' },
    { field: 'product_name', headerName: 'Nome do Produto' },
    { field: 'quantity', headerName: 'Quantidade' },
    { field: 'received', headerName: 'Recebido' },
    {
      field: 'delivery_status',
      headerName: 'Status da Entrega',
      valueGetter: (params) => {
        const received = params.data.received;
        const quantity = params.data.quantity;
        return received === quantity ? 'Completo' : received === 0 ? 'Pendente' : 'Parcial';
      }
    }
  ];

  return (
    <div className="full-width-panel">
      <div className="full-width-grid">
        <AgGridReact
          columnDefs={detailColumnDefs}
          rowData={props.data.details}
          defaultColDef={{
            flex: 1,
            sortable: true,
            filter: true,
          }}
          domLayout="autoHeight"
        />
      </div>
    </div>
  );
};

DetailCellRenderer.propTypes = {
  data: PropTypes.shape({
    details: PropTypes.arrayOf(PropTypes.shape({
      product_code: PropTypes.string,
      product_name: PropTypes.string,
      quantity: PropTypes.number,
      received: PropTypes.number,
    })).isRequired,
  }).isRequired,
};

export default DetailCellRenderer;