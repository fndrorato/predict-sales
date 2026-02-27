import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { getCompanyEndpoint } from 'src/config'
import { login } from 'src/services/auth'
import {
  CButton,
  CCard,
  CCardBody,
  CCardGroup,
  CCol,
  CContainer,
  CForm,
  CFormInput,
  CInputGroup,
  CInputGroupText,
  CRow,
  CSpinner,
} from '@coreui/react'
import CIcon from '@coreui/icons-react'
import { cilLockLocked, cilUser } from '@coreui/icons'

const Login = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [companyData, setCompanyData] = useState(null)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    const fetchCompanyData = async () => {
      try {
        const response = await fetch(getCompanyEndpoint())
        const data = await response.json()
        setCompanyData(data)
        document.title = data.name
        const favicon = document.querySelector('link[rel="icon"]')
        if (favicon) {
          favicon.href = data.logo_icon
        }
      } catch (error) {
        console.error('Error fetching company data:', error)
      }
    }

    fetchCompanyData()
  }, [])
  return (
    <div className="bg-body-tertiary min-vh-100 d-flex flex-row align-items-center">
      <CContainer>
        <CRow className="justify-content-center">
          <CCol md={8}>
            <CCardGroup>
              <CCard className="p-4">
                <CCardBody>
                  <CForm onSubmit={async (e) => {
                    e.preventDefault()
                    setIsLoading(true)
                    setError('')
                    try {
                      await login(username, password)
                      navigate('/dashboard')
                    } catch (err) {
                      setError('Usuário ou senha inválidos')
                    } finally {
                      setIsLoading(false)
                    }
                  }}>
                    <h1>{t('login.title')}</h1>
                    <p className="text-body-secondary">{t('login.signIn')}</p>
                    {error && <div className="text-danger mb-3">{error}</div>}
                    <CInputGroup className="mb-3">
                      <CInputGroupText>
                        <CIcon icon={cilUser} />
                      </CInputGroupText>
                      <CFormInput
                        placeholder={t('login.username')}
                        autoComplete="username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                      />
                    </CInputGroup>
                    <CInputGroup className="mb-4">
                      <CInputGroupText>
                        <CIcon icon={cilLockLocked} />
                      </CInputGroupText>
                      <CFormInput
                        type="password"
                        placeholder={t('login.password')}
                        autoComplete="current-password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                      />
                    </CInputGroup>
                    <CRow>
                      <CCol xs={6}>
                        <CButton type="submit" color="primary" className="px-4" disabled={isLoading}>
                          {isLoading ? <CSpinner size="sm" /> : t('login.loginButton')}
                        </CButton>
                      </CCol>
                      <CCol xs={6} className="text-right">
                        <CButton color="link" className="px-0">
                          {t('login.forgotPassword')}
                        </CButton>
                      </CCol>
                    </CRow>
                  </CForm>
                </CCardBody>
              </CCard>
              <CCard className="text-white bg-white py-5" style={{ width: '44%' }}>
                <CCardBody className="text-center">
                  <div>
                    {companyData && (
                      <img
                        src={companyData.logo_login}
                        alt={companyData.name}
                        style={{ maxWidth: '80%', height: 'auto', marginBottom: '1rem' }}
                      />
                    )}
                  </div>
                </CCardBody>
              </CCard>
            </CCardGroup>
          </CCol>
        </CRow>
      </CContainer>
    </div>
  )
}

export default Login
