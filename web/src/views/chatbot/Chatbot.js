import React, { useState, useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import {
  CCard,
  CCardBody,
  CCardHeader,
  CCol,
  CRow,
  CFormInput,
  CButton,
  CSpinner,
  CAlert
} from '@coreui/react'
import CIcon from '@coreui/icons-react'
import { cilSend, cilUser, cilBolt } from '@coreui/icons'

// Services
import http from '../../services/http'

// Config
import { COMPANY_SETTINGS } from '../../config'

const Chatbot = () => {
  const { t } = useTranslation()
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const messagesEndRef = useRef(null)

  // Verifica se o chatbot está habilitado nas configurações
  const isChatbotEnabled = COMPANY_SETTINGS && COMPANY_SETTINGS.enable_chatbot

  // Função para rolar para a última mensagem
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  // Rola para a última mensagem quando as mensagens são atualizadas
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Função para enviar mensagem para a API
  const sendMessage = async () => {
    if (!newMessage.trim()) return

    // Adiciona a mensagem do usuário à lista
    const userMessage = {
      id: Date.now(),
      text: newMessage,
      sender: 'user',
      timestamp: new Date().toISOString()
    }

    setMessages(prevMessages => [...prevMessages, userMessage])
    setNewMessage('')
    setIsLoading(true)
    setError(null)

    try {
      // Envia a pergunta para a API
      const response = await http.post('/chatbot/ask/', {
        question: newMessage
      })

      // Adiciona a resposta do chatbot à lista
      const botMessage = {
        id: Date.now() + 1,
        text: response.data.answer,
        sender: 'bot',
        timestamp: new Date().toISOString()
      }

      setMessages(prevMessages => [...prevMessages, botMessage])
    } catch (err) {
      console.error('Erro ao enviar mensagem:', err)
      setError(t('chatbot.errorSending'))
    } finally {
      setIsLoading(false)
    }
  }

  // Função para lidar com o envio do formulário
  const handleSubmit = (e) => {
    e.preventDefault()
    sendMessage()
  }

  // Função para lidar com a tecla Enter
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  // Renderiza uma mensagem individual
  const renderMessage = (message) => {
    const isUser = message.sender === 'user'
    const icon = isUser ? cilUser : cilBolt
    const alignClass = isUser ? 'justify-content-end' : 'justify-content-start'
    const bgColor = isUser ? 'bg-light' : 'bg-primary'
    const textColor = isUser ? 'text-dark' : 'text-white'

    return (
      <CRow className={`mb-2 ${alignClass}`} key={message.id}>
        <CCol xs="auto" className="d-flex align-items-end">
          {!isUser && <CIcon icon={icon} size="lg" className="me-2" />}
        </CCol>
        <CCol xs="auto" style={{ maxWidth: '75%' }}>
          <div className={`p-3 rounded ${bgColor} ${textColor}`} style={{ whiteSpace: 'pre-wrap' }}>
            {message.text}
          </div>
          <small className="text-muted">
            {new Date(message.timestamp).toLocaleTimeString()}
          </small>
        </CCol>
        <CCol xs="auto" className="d-flex align-items-end">
          {isUser && <CIcon icon={icon} size="lg" className="ms-2" />}
        </CCol>
      </CRow>
    )
  }

  // Se o chatbot não estiver habilitado, exibe uma mensagem
  if (!isChatbotEnabled) {
    return (
      <CCard className="mb-4">
        <CCardHeader>
          <strong>{t('chatbot.title')}</strong>
        </CCardHeader>
        <CCardBody>
          <CAlert color="info">
            {t('chatbot.disabled')}
          </CAlert>
        </CCardBody>
      </CCard>
    )
  }

  return (
    <CCard className="mb-4">
      <CCardHeader>
        <strong>{t('chatbot.title')}</strong>
      </CCardHeader>
      <CCardBody>
        <div className="chat-container" style={{ height: '70vh', overflowY: 'auto', marginBottom: '1rem' }}>
          {messages.length === 0 ? (
            <div className="text-center text-muted my-5">
              <CIcon icon={cilBolt} size="3xl" className="mb-3" />
              <h5>{t('chatbot.welcome')}</h5>
              <p>{t('chatbot.instructions')}</p>
            </div>
          ) : (
            messages.map(message => renderMessage(message))
          )}
          {isLoading && (
            <CRow className="justify-content-start mb-3">
              <CCol xs="auto">
                <CSpinner size="sm" color="primary" />
              </CCol>
            </CRow>
          )}
          {error && (
            <CAlert color="danger" className="mt-3">
              {error}
            </CAlert>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit}>
          <CRow>
            <CCol>
              <CFormInput
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={t('chatbot.placeholder')}
                disabled={isLoading}
                autoFocus
              />
            </CCol>
            <CCol xs="auto">
              <CButton color="primary" type="submit" disabled={isLoading || !newMessage.trim()}>
                {isLoading ? (
                  <CSpinner size="sm" color="light" />
                ) : (
                  <CIcon icon={cilSend} />
                )}
              </CButton>
            </CCol>
          </CRow>
        </form>
      </CCardBody>
    </CCard>
  )
}

export default Chatbot