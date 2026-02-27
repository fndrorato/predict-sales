import React, { useState, useEffect } from 'react'
import {
  CButton,
  CCard,
  CCardBody,
  CCardHeader,
  CCol,
  CForm,
  CFormLabel,
  CFormCheck,
  CFormSelect,
  CRow,
  CToast,
  CToastBody,
  CToastHeader,
  CToaster,
  CSpinner,
} from '@coreui/react'
import http from 'src/services/http'
import { useTranslation } from 'react-i18next'
import { API_CONFIG, COMPANY_SETTINGS } from 'src/config'

const SystemConfig = () => {
  const { t } = useTranslation()
  const [isLoading, setIsLoading] = useState(false)
  const [toast, setToast] = useState(null)
  const [settings, setSettings] = useState({
    id: 0,
    company: parseInt(API_CONFIG.COMPANY_ID),
    enable_notifications: true,
    report_negative_availability: true,
    report_orders_awaiting_confirmation: true,
    open_default_page: 'dashboard',
    enable_chatbot: true,
    chatbot_allowed_groups: [],
  })
  const [groups, setGroups] = useState([])
  const [defaultPageOptions] = useState([
    { value: 'dashboard', label: 'Dashboard' },
    { value: 'orders', label: 'Ordens de Compra' },
    { value: 'items', label: 'Itens' },
  ])

  // Buscar configurações existentes e grupos disponíveis
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true)
      try {
        // Verificar se já temos as configurações carregadas globalmente
        if (COMPANY_SETTINGS && COMPANY_SETTINGS.id) {
          setSettings(COMPANY_SETTINGS)
        }

        // Buscar grupos disponíveis
        const groupsResponse = await http.get('/company/groups/')
        if (groupsResponse.data && Array.isArray(groupsResponse.data)) {
          setGroups(groupsResponse.data)
        }  
      } catch (error) {
        console.error('Erro ao buscar dados:', error)
        setToast({
          visible: true,
          color: 'danger',
          message: t('systemConfig.errorLoading'),
        })
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      // Se o ID for 0, é uma nova configuração (POST), caso contrário é uma atualização (PUT)
      if (settings.id === 0) {
        const response = await http.post('/company/settings/', settings)
        setSettings(response.data)
        // Atualizar as configurações globais
        Object.assign(COMPANY_SETTINGS, response.data)
      } else {
        await http.put(`/company/settings/${settings.id}/`, settings)
        // Atualizar as configurações globais
        Object.assign(COMPANY_SETTINGS, settings)
      }

      setToast({
        visible: true,
        color: 'success',
        message: t('common.savedSuccessfully'),
      })
    } catch (error) {
      console.error('Erro ao salvar configurações:', error)
      setToast({
        visible: true,
        color: 'danger',
        message: t('common.errorSaving'),
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleCheckboxChange = (field) => (e) => {
    setSettings({
      ...settings,
      [field]: e.target.checked,
    })
  }

  const handleSelectChange = (field) => (e) => {
    setSettings({
      ...settings,
      [field]: e.target.value,
    })
  }

  const handleMultiSelectChange = (e) => {
    const selectedOptions = Array.from(e.target.selectedOptions, (option) => parseInt(option.value))
    setSettings({
      ...settings,
      chatbot_allowed_groups: selectedOptions,
    })
  }

  return (
    <CRow>
      <CCol xs={12}>
        <CCard className="mb-4">
          <CCardHeader>
            <strong>{t('systemConfig.title')}</strong>
          </CCardHeader>
          <CCardBody>
            <CForm onSubmit={handleSubmit}>
              {/* Notificações */}
              <CRow className="mb-3">
                <CFormLabel htmlFor="enable_notifications" className="col-sm-4 col-form-label">
                  {t('systemConfig.enableNotifications')}
                </CFormLabel>
                <CCol sm={8}>
                  <CFormCheck
                    id="enable_notifications"
                    checked={settings.enable_notifications}
                    onChange={handleCheckboxChange('enable_notifications')}
                    disabled={isLoading}
                  />
                </CCol>
              </CRow>

              {/* Relatório de Items com Stock sem vendas */}
              <CRow className="mb-3">
                <CFormLabel htmlFor="report_items_with_stock_no_sales" className="col-sm-4 col-form-label">
                  {t('systemConfig.reportItemsWithStockNoSales')}
                </CFormLabel>
                <CCol sm={8}>
                  <CFormCheck
                    id="report_items_with_stock_no_sales"
                    checked={settings.report_items_with_stock_no_sales}
                    onChange={handleCheckboxChange('report_items_with_stock_no_sales')}
                    disabled={isLoading}
                  />
                </CCol>
              </CRow>              

              {/* Relatório de Disponibilidade Negativa */}
              <CRow className="mb-3">
                <CFormLabel htmlFor="report_negative_availability" className="col-sm-4 col-form-label">
                  {t('systemConfig.reportNegativeAvailability')}
                </CFormLabel>
                <CCol sm={8}>
                  <CFormCheck
                    id="report_negative_availability"
                    checked={settings.report_negative_availability}
                    onChange={handleCheckboxChange('report_negative_availability')}
                    disabled={isLoading}
                  />
                </CCol>
              </CRow>

              {/* Relatório de Ordens Aguardando Confirmação */}
              <CRow className="mb-3">
                <CFormLabel htmlFor="report_orders_awaiting_confirmation" className="col-sm-4 col-form-label">
                  {t('systemConfig.reportOrdersAwaitingConfirmation')}
                </CFormLabel>
                <CCol sm={8}>
                  <CFormCheck
                    id="report_orders_awaiting_confirmation"
                    checked={settings.report_orders_awaiting_confirmation}
                    onChange={handleCheckboxChange('report_orders_awaiting_confirmation')}
                    disabled={isLoading}
                  />
                </CCol>
              </CRow>

              {/* Relatório de Ordens Aguardando Confirmação */}
              <CRow className="mb-3">
                <CFormLabel htmlFor="view_sales_last_weeks" className="col-sm-4 col-form-label">
                  {t('systemConfig.view_sales_last_weeks')}
                </CFormLabel>
                <CCol sm={8}>
                  <CFormCheck
                    id="view_sales_last_weeks"
                    checked={settings.view_sales_last_weeks}
                    onChange={handleCheckboxChange('view_sales_last_weeks')}
                    disabled={isLoading}
                  />
                </CCol>
              </CRow>              

              {/* Página Padrão */}
              <CRow className="mb-3">
                <CFormLabel htmlFor="open_default_page" className="col-sm-4 col-form-label">
                  {t('systemConfig.openDefaultPage')}
                </CFormLabel>
                <CCol sm={8}>
                  <CFormSelect
                    id="open_default_page"
                    value={settings.open_default_page}
                    onChange={handleSelectChange('open_default_page')}
                    disabled={isLoading}
                  >
                    {defaultPageOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </CFormSelect>
                </CCol>
              </CRow>

              {/* Habilitar Chatbot */}
              <CRow className="mb-3">
                <CFormLabel htmlFor="enable_chatbot" className="col-sm-4 col-form-label">
                  {t('systemConfig.enableChatbot')}
                </CFormLabel>
                <CCol sm={8}>
                  <CFormCheck
                    id="enable_chatbot"
                    checked={settings.enable_chatbot}
                    onChange={handleCheckboxChange('enable_chatbot')}
                    disabled={isLoading}
                  />
                </CCol>
              </CRow>

              {/* Grupos Permitidos para Chatbot */}
              <CRow className="mb-3">
                <CFormLabel htmlFor="chatbot_allowed_groups" className="col-sm-4 col-form-label">
                  {t('systemConfig.chatbotAllowedGroups')}
                </CFormLabel>
                <CCol sm={8}>
                  <CFormSelect
                    id="chatbot_allowed_groups"
                    multiple
                    value={settings.chatbot_allowed_groups.map(String)}
                    onChange={handleMultiSelectChange}
                    disabled={isLoading || !settings.enable_chatbot}
                    size="5"
                  >
                    {groups.map((group) => (
                      <option key={group.id} value={group.id}>
                        {group.name}
                      </option>
                    ))}
                  </CFormSelect>
                  <small className="text-muted">
                    {t('systemConfig.selectMultipleGroups')}
                  </small>
                </CCol>
              </CRow>

              <CButton color="primary" type="submit" disabled={isLoading}>
                {isLoading ? <CSpinner size="sm" className="me-2" /> : null}
                {t('common.save')}
              </CButton>
            </CForm>
          </CCardBody>
        </CCard>
      </CCol>

      {toast && (
        <CToaster placement="top-end">
          <CToast visible={toast.visible} color={toast.color} onClose={() => setToast(null)} autohide delay={1500}>
            <CToastHeader closeButton>
              {toast.color === 'success' ? t('common.success') : t('common.error')}
            </CToastHeader>
            <CToastBody>{toast.message}</CToastBody>
          </CToast>
        </CToaster>
      )}
    </CRow>
  )
}

export default SystemConfig