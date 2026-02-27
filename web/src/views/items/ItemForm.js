import React from 'react'
import PropTypes from 'prop-types';
import { CCol, CFormInput, CFormLabel, CRow } from '@coreui/react'

const ItemForm = ({ item }) => {
  return (
    <>
      <CRow className="mb-2">
        <CFormLabel htmlFor="code" className="col-sm-1 col-form-label col-form-label-sm text-body">
          Código
        </CFormLabel>
        <CCol sm={3}>
          <CFormInput
            type="text"
            className="form-control form-control-sm"
            id="code"
            value={item.code}
            disabled
          />
        </CCol>
        <CFormLabel htmlFor="is_active_purchase" className="col-sm-2 col-form-label col-form-label-sm text-body">
          Ativo Compra
        </CFormLabel>
        <CCol sm={2}>
          <CFormInput
            type="checkbox"
            className="form-check-input mt-2"
            id="is_active_purchase"
            checked={item.is_active_purchase}
            disabled
          />
        </CCol>
        <CFormLabel htmlFor="is_active" className="col-sm-2 col-form-label col-form-label-sm text-body">
          Ativo
        </CFormLabel>
        <CCol sm={2}>
          <CFormInput
            type="checkbox"
            className="form-check-input mt-2"
            id="is_active"
            checked={item.is_active}
            disabled
          />
        </CCol>
      </CRow>    
      <CRow className="mb-2">
        <CFormLabel htmlFor="name" className="col-sm-1 col-form-label col-form-label-sm text-body">
          Nome
        </CFormLabel>
        <CCol sm={3}>
          <CFormInput
            type="text"
            className="form-control form-control-sm"
            id="name"
            value={item.name}
            disabled
          />
        </CCol>
        <CFormLabel htmlFor="brand" className="col-sm-2 col-form-label col-form-label-sm text-body">
          Marca
        </CFormLabel>
        <CCol sm={2}>
          <CFormInput
            type="text"
            className="form-control form-control-sm"
            id="brand"
            value={item.brand}
            disabled
          />
        </CCol>
        <CFormLabel htmlFor="unit_of_measure" className="col-sm-2 col-form-label col-form-label-sm text-body">
          Unidade
        </CFormLabel>
        <CCol sm={2}>
          <CFormInput
            type="text"
            className="form-control form-control-sm"
            id="unit_of_measure"
            value={item.unit_of_measure}
            disabled
          />
        </CCol>
      </CRow>
      <CRow className="mb-2">
        <CFormLabel htmlFor="supplier" className="col-sm-1 col-form-label col-form-label-sm text-body">
          Fornecedor
        </CFormLabel>
        <CCol sm={3}>
          <CFormInput
            type="text"
            className="form-control form-control-sm"
            id="supplier"
            value={item.supplier}
            disabled
          />
        </CCol>
        <CFormLabel htmlFor="category" className="col-sm-2 col-form-label col-form-label-sm text-body">
          Categoria
        </CFormLabel>
        <CCol sm={2}>
          <CFormInput
            type="text"
            className="form-control form-control-sm"
            id="category"
            value={item.category}
            disabled
          />
        </CCol>
        <CFormLabel htmlFor="subcategory" className="col-sm-2 col-form-label col-form-label-sm text-body">
          Subcategoria
        </CFormLabel>
        <CCol sm={2}>
          <CFormInput
            type="text"
            className="form-control form-control-sm"
            id="subcategory"
            value={item.subcategory}
            disabled
          />
        </CCol>
      </CRow>
    </>
  )
}


ItemForm.propTypes = {
  item: PropTypes.shape({
    code: PropTypes.string,
    name: PropTypes.string,
    pack_size: PropTypes.number,
    min_size: PropTypes.number,
    unit_of_measure: PropTypes.string,
    supplier: PropTypes.string,
    category: PropTypes.string,
    subcategory: PropTypes.string,
    nivel3: PropTypes.string,
    nivel4: PropTypes.string,
    nivel5: PropTypes.string,
    brand: PropTypes.string,
    is_active_purchase: PropTypes.bool,
    is_active: PropTypes.bool,
    matriz_price: PropTypes.number,
  }).isRequired,
};


export default ItemForm;