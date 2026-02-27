import React, { useState } from 'react'
import PropTypes from 'prop-types'
import {
  CModal,
  CModalHeader,
  CModalTitle,
  CModalBody,
  CButton,
  CFormInput,
  CTable,
  CTableHead,
  CTableRow,
  CTableHeaderCell,
  CTableBody,
  CTableDataCell,
  CSpinner,
} from '@coreui/react'
import http from 'src/services/http'

const ItemModal = ({ visible, onClose, onSelect }) => {
  const [searchQuery, setSearchQuery] = useState('')
  const [items, setItems] = useState([])
  const [isLoading, setIsLoading] = useState(false)

  const handleSearch = async () => {
    if (!searchQuery.trim()) return

    setIsLoading(true)
    try {
      const response = await http.get(`/item/?query=${searchQuery}`)
      setItems(response.data)
    } catch (error) {
      console.error('Erro ao buscar itens:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  const handleSelect = (item) => {
    onSelect(item.code)
    onClose()
  }

  return (
    <CModal visible={visible} onClose={onClose} size="lg">
      <CModalHeader>
        <CModalTitle className="text-secondary">Pesquisar Produto</CModalTitle>
      </CModalHeader>
      <CModalBody>
        <div className="d-flex mb-3">
          <CFormInput
            type="text"
            placeholder="Digite para pesquisar..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            className="me-2"
          />
          <CButton color="primary" onClick={handleSearch} disabled={isLoading}>
            {isLoading ? <CSpinner size="sm" /> : 'Pesquisar'}
          </CButton>
        </div>

        <CTable hover responsive className="mt-2 table-sm small-font-table">
          <CTableHead className='text-small small-text'>
            <CTableRow>
              <CTableHeaderCell scope="col" style={{ width: '80px' }}>Selecionar</CTableHeaderCell>
              <CTableHeaderCell scope="col" style={{ width: '80px' }}>Código</CTableHeaderCell>
              <CTableHeaderCell scope="col">Nome</CTableHeaderCell>
            </CTableRow>
          </CTableHead>
          <CTableBody className="text-small small-text">
            {items.map((item) => (
              <CTableRow key={item.code}>
                <CTableDataCell>
                  <CButton
                    color="primary"
                    size="sm"
                    onClick={() => handleSelect(item)}
                  >
                    Selecionar
                  </CButton>
                </CTableDataCell>
                <CTableDataCell>{item.code}</CTableDataCell>
                <CTableDataCell>{item.name}</CTableDataCell>
              </CTableRow>
            ))}
          </CTableBody>
        </CTable>
      </CModalBody>
    </CModal>
  )
}

ItemModal.propTypes = {
  visible: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onSelect: PropTypes.func.isRequired
}

export default ItemModal