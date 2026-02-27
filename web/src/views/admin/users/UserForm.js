import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import {
  CButton,
  CCard,
  CCardBody,
  CCardHeader,
  CCol,
  CForm,
  CFormInput,
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
import { useNavigate } from 'react-router-dom'

const UserForm = ({ user }) => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [username, setUsername] = useState(user?.username || '')
  const [email, setEmail] = useState(user?.email || '')
  const [firstName, setFirstName] = useState(user?.first_name || '')
  const [lastName, setLastName] = useState(user?.last_name || '')
  const [isActive, setIsActive] = useState(user?.is_active ?? true)
  const [toast, setToast] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [usernameError, setUsernameError] = useState(false)
  const [emailError, setEmailError] = useState(false)
  const [firstNameError, setFirstNameError] = useState(false)
  const [lastNameError, setLastNameError] = useState(false)
  const [groups, setGroups] = useState([])
  const [selectedGroup, setSelectedGroup] = useState(user?.group_id_read || '')
  const [groupError, setGroupError] = useState(false)

  useEffect(() => {
    const fetchGroups = async () => {
      try {
        const response = await http.get('/groups/')
        setGroups(response.data.results)
      } catch (error) {
        console.error('Error fetching groups:', error)
      }
    }
    fetchGroups()
  }, [])



  return (
    <CRow>
      <CCol xs={12}>
        <CCard className="mb-4">
          <CCardHeader>
            <strong>{user ? t('users.editUser') : t('users.newUser')}</strong>
          </CCardHeader>
          <CCardBody>
            <CForm onSubmit={async (e) => {
              e.preventDefault()
              let hasError = false

              if (!username.trim()) {
                setUsernameError(true)
                hasError = true
              }
              if (!email.trim()) {
                setEmailError(true)
                hasError = true
              }
              if (!firstName.trim()) {
                setFirstNameError(true)
                hasError = true
              }
              if (!lastName.trim()) {
                setLastNameError(true)
                hasError = true
              }
              if (!selectedGroup) {
                setGroupError(true)
                hasError = true
              }

              if (hasError) return

              setIsLoading(true)
              try {
                const data = {
                  username,
                  email,
                  first_name: firstName,
                  last_name: lastName,
                  is_active: isActive,
                  group_id: parseInt(selectedGroup)
                }

                if (!user?.id) {
                  data.password = 'cambiar@123'
                }
                
                if (user?.id) {
                  await http.put(`/users/${user.id}/`, data)
                } else {
                  await http.post('/users/', data)
                }
                
                setToast({
                  visible: true,
                  color: 'success',
                  message: t('common.savedSuccessfully')
                })
                setTimeout(() => navigate('/admin/users'), 1500)
              } catch (error) {
                console.error('Error saving user:', error)
                console.error('Error response data:', error.response?.data)
                if (error.response?.data) {
                  const errorData = error.response.data
                  if (errorData.username) {
                    setUsernameError(errorData.username[0])
                    setToast({
                      visible: true,
                      color: 'danger',
                      message: errorData.username[0]
                    })
                  } else if (errorData.email) {
                    setEmailError(errorData.email[0])
                    setToast({
                      visible: true,
                      color: 'danger',
                      message: errorData.email[0]
                    })
                  } else {
                    setToast({
                      visible: true,
                      color: 'danger',
                      message: t('common.errorSaving')
                    })
                  }
                } else {
                  setToast({
                    visible: true,
                    color: 'danger',
                    message: t('common.errorSaving')
                  })
                }
              } finally {
                setIsLoading(false)
              }
            }}>
            <CRow className="mb-3">
                <CFormLabel htmlFor="username" className="col-sm-2 col-form-label">
                    {t('users.username')}
                </CFormLabel>
                <CCol sm={10}>
                    <CFormInput 
                    type="text" 
                    id="username" 
                    value={username}
                    onChange={(e) => {
                        setUsername(e.target.value)
                        setUsernameError(false)
                    }}
                    invalid={usernameError}
                    disabled={isLoading}
                    />
                    {usernameError && (
                        <div className="invalid-feedback d-block">
                            {typeof usernameError === 'string' ? usernameError : t('users.usernameRequired')}
                        </div>
                    )}
                </CCol>
            </CRow>

            <CRow className="mb-3">
                <CFormLabel htmlFor="email" className="col-sm-2 col-form-label">
                    {t('users.email')}
                </CFormLabel>
                <CCol sm={10}>
                    <CFormInput 
                    type="email" 
                    id="email" 
                    value={email}
                    onChange={(e) => {
                        setEmail(e.target.value)
                        setEmailError(false)
                    }}
                    invalid={emailError}
                    disabled={isLoading}
                    />
                    {emailError && (
                        <div className="invalid-feedback d-block">
                            {typeof emailError === 'string' ? emailError : t('users.emailRequired')}
                        </div>
                    )}
                </CCol>
            </CRow>

            <CRow className="mb-3">
                <CFormLabel htmlFor="firstName" className="col-sm-2 col-form-label">
                    {t('users.firstName')}
                </CFormLabel>
                <CCol sm={10}>
                    <CFormInput 
                    type="text" 
                    id="firstName" 
                    value={firstName}
                    onChange={(e) => {
                        setFirstName(e.target.value)
                        setFirstNameError(false)
                    }}
                    invalid={firstNameError}
                    disabled={isLoading}
                    />
                    {firstNameError && (
                        <div className="invalid-feedback d-block">
                            {t('users.firstNameRequired')}
                        </div>
                    )}
                </CCol>
            </CRow>

            <CRow className="mb-3">
                <CFormLabel htmlFor="lastName" className="col-sm-2 col-form-label">
                    {t('users.lastName')}
                </CFormLabel>
                <CCol sm={10}>
                    <CFormInput 
                    type="text" 
                    id="lastName" 
                    value={lastName}
                    onChange={(e) => {
                        setLastName(e.target.value)
                        setLastNameError(false)
                    }}
                    invalid={lastNameError}
                    disabled={isLoading}
                    />
                    {lastNameError && (
                        <div className="invalid-feedback d-block">
                            {t('users.lastNameRequired')}
                        </div>
                    )}
                </CCol>
            </CRow>

            <CRow className="mb-3">
                <CFormLabel htmlFor="group" className="col-sm-2 col-form-label">
                    {t('users.group')}
                </CFormLabel>
                <CCol sm={10}>
                    <CFormSelect
                        id="group"
                        value={selectedGroup}
                        onChange={(e) => {
                            setSelectedGroup(e.target.value)
                            setGroupError(false)
                        }}
                        invalid={groupError}
                        disabled={isLoading}
                    >
                        <option value="">{t('users.selectGroup')}</option>
                        {groups.map((group) => (
                            <option key={group.id} value={group.id}>
                                {group.name}
                            </option>
                        ))}
                    </CFormSelect>
                    {groupError && (
                        <div className="invalid-feedback d-block">
                            {t('users.groupRequired')}
                        </div>
                    )}
                </CCol>
            </CRow>

            <CRow className="mb-3">
                <CFormLabel htmlFor="isActive" className="col-sm-2 col-form-label">
                    {t('users.isActive')}
                </CFormLabel>
                <CCol sm={10}>
                    <CFormCheck
                        id="isActive"
                        checked={isActive}
                        onChange={(e) => setIsActive(e.target.checked)}
                        disabled={isLoading}
                    />
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

UserForm.propTypes = {
  user: PropTypes.shape({
    id: PropTypes.number,
    username: PropTypes.string,
    email: PropTypes.string,
    first_name: PropTypes.string,
    last_name: PropTypes.string,
    is_active: PropTypes.bool,
    group_id_read: PropTypes.number
  })
}

export default UserForm
