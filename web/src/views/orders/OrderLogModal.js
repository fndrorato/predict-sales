import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import './OrderLogModal.css'  // Importe o CSS aqui
import {
  CModal,
  CModalHeader,
  CModalTitle,
  CModalBody,
  CModalFooter,
  CButton,
  CSpinner,
  CCard,
  CCardBody,
  CBadge
} from '@coreui/react'
import http from 'src/services/http'

const OrderLogModal = ({ visible, onClose, orderId }) => {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchLogs = async () => {
      if (!orderId || !visible) return
      
      setLoading(true)
      setError(null)
      
      try {
        const response = await http.get(`/orders/logs/${orderId}/`)
        setLogs(response.data)
      } catch (err) {
        console.error('Erro ao carregar logs:', err)
        setError('Não foi possível carregar os logs. Tente novamente mais tarde.')
      } finally {
        setLoading(false)
      }
    }

    fetchLogs()
  }, [orderId, visible])

  const formatDate = (dateString) => {
    if (!dateString) return ''
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date)
  }

  const getActionBadge = (action) => {
    switch (action) {
      case 'created':
        return <CBadge color="success">Criação</CBadge>
      case 'status_changed':
        return <CBadge color="primary">Status Alterado</CBadge>
      case 'item_modified':
        return <CBadge color="warning">Item Modificado</CBadge>
      case 'item_added':
        return <CBadge color="info">Item Adicionado</CBadge>
      case 'item_removed':
        return <CBadge color="danger">Item Removido</CBadge>
      default:
        return <CBadge color="secondary">{action}</CBadge>
    }
  }

  const getLogDetails = (log) => {
    if (log.action === 'created') {
      return <p>{log.notes}</p>
    }
    
    if (log.action === 'status_changed') {
      return (
        <p>
          Status alterado de <strong>{log.previous_status}</strong> para <strong>{log.new_status}</strong>
          {log.notes && <><br />{log.notes}</>}
        </p>
      )
    }
    
    if (log.action === 'item_modified') {
      return (
        <div>
          <p>
            <strong>Item:</strong> {log.item_name} (Código: {log.item})
            <br />
            <strong>Campo alterado:</strong> {log.field_changed}
            <br />
            <strong>Valor anterior:</strong> {log.previous_value}
            <br />
            <strong>Novo valor:</strong> {log.new_value}
          </p>
        </div>
      )
    }
    
    return <p>{log.notes || 'Sem detalhes adicionais'}</p>
  }

  return (
    <CModal visible={visible} onClose={onClose} size="lg">
      <CModalHeader onClose={onClose}>
        <CModalTitle>Histórico de Logs - Ordem {orderId}</CModalTitle>
      </CModalHeader>
      <CModalBody>
        {loading ? (
          <div className="text-center my-3">
            <CSpinner />
            <p className="mt-2">Carregando logs...</p>
          </div>
        ) : error ? (
          <div className="text-center text-danger my-3">{error}</div>
        ) : logs.length === 0 ? (
          <div className="text-center my-3">Nenhum log encontrado para esta ordem.</div>
        ) : (
          <div className="timeline">
            {logs.map((log) => (
              <div key={log.id} className="timeline-item">
                <div className="timeline-left">
                  <div className="timeline-date">{formatDate(log.timestamp)}</div>
                  <div className="timeline-user">{log.user_name}</div>
                </div>
                <div className="timeline-badge">
                  {getActionBadge(log.action)}
                </div>
                <CCard className="timeline-content">
                  <CCardBody>
                    {getLogDetails(log)}
                  </CCardBody>
                </CCard>
              </div>
            ))}
          </div>
        )}
      </CModalBody>

    </CModal>
  )
}

OrderLogModal.propTypes = {
  visible: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  orderId: PropTypes.string
}

export default OrderLogModal