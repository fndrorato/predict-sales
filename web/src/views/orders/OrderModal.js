import React from 'react';
import PropTypes from 'prop-types';
import {
  CModal,
  CModalHeader,
  CModalTitle,
  CModalBody,
  CRow,
  CCol,
  CFormLabel,
  CFormInput,
  CTable,
  CTableHead,
  CTableRow,
  CTableHeaderCell,
  CTableBody,
  CTableDataCell
} from '@coreui/react';

const OrderModal = ({ visible, onClose, order }) => {
  const formatNumber = (number) => {
    return number?.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  };
  return (
    <CModal 
      visible={visible} 
      onClose={onClose}
      size="lg"
    >
      <CModalHeader>
        <CModalTitle className='text-body-secondary'>Detalhes da Ordem de Compra {order?.oc_number}</CModalTitle>
      </CModalHeader>
      <CModalBody>
        {order && (
          <>
            <CRow className="mb-1">
              <CCol sm={2}>
                <CFormLabel className="form-label-sm text-body-secondary">Sucursal</CFormLabel>
                <CFormInput
                  size="sm"
                  value={`${order.store} - ${order.store_name}`}
                  disabled
                />
              </CCol>
              <CCol sm={4}>
                <CFormLabel className="form-label-sm text-body-secondary">Fornecedor</CFormLabel>
                <CFormInput
                  size="sm"
                  value={`${order.supplier} - ${order.supplier_name}`}
                  disabled
                />
              </CCol>
              <CCol sm={2}>
                <CFormLabel className="form-label-sm text-body-secondary">Valor Total</CFormLabel>
                <CFormInput
                  size="sm"
                  value={formatNumber(order.total_amount)}
                  disabled
                  className="text-end"
                />
              </CCol>
              <CCol sm={2}>
                <CFormLabel className="form-label-sm text-body-secondary">Data</CFormLabel>
                <CFormInput
                  size="sm"
                  type="date"
                  value={order.date}
                  disabled
                  className="text-end"
                />
              </CCol>  
              <CCol sm={2}>
                <CFormLabel className="form-label-sm text-body-secondary">Data Prevista</CFormLabel>
                <CFormInput
                  size="sm"
                  type="date"
                  value={order.expected_date}
                  disabled
                  className="text-end"
                />
              </CCol>                          
            </CRow>
            

            <CTable small striped className="mt-2 table-sm small-font-table">
              <CTableHead className="text-small small-text">
                <CTableRow>
                  <CTableHeaderCell scope="col">Item</CTableHeaderCell>
                  <CTableHeaderCell scope="col">Descrição</CTableHeaderCell>
                  <CTableHeaderCell scope="col" className="text-end">Qtd. Pedido</CTableHeaderCell>
                  <CTableHeaderCell scope="col" className="text-end">Qtd. Recebida</CTableHeaderCell>
                  <CTableHeaderCell scope="col" className="text-end">Preço</CTableHeaderCell>
                </CTableRow>
              </CTableHead>
              <CTableBody className="text-small small-text">
                {order.items.map((item, index) => (
                  <CTableRow key={index}>
                    <CTableDataCell>{item.item}</CTableDataCell>
                    <CTableDataCell>{item.item_name}</CTableDataCell>
                    <CTableDataCell className="text-end">{item.quantity_order}</CTableDataCell>
                    <CTableDataCell className="text-end">{item.quantity_received}</CTableDataCell>
                    <CTableDataCell className="text-end">{item.price}</CTableDataCell>
                  </CTableRow>
                ))}
              </CTableBody>
            </CTable>
          </>
        )}
      </CModalBody>
    </CModal>
  );
};

OrderModal.propTypes = {
  visible: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  order: PropTypes.object
};

export default OrderModal;