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
  CFormSelect,
  CRow,
  CToast,
  CToastBody,
  CToastHeader,
  CToaster,
  CSpinner,
} from '@coreui/react'
import http from 'src/services/http'
import CIcon from '@coreui/icons-react'
import { cilArrowRight, cilArrowLeft } from '@coreui/icons'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'

const GroupForm = ({ group }) => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [allPermissions, setAllPermissions] = useState([])
  const [groupPermissions, setGroupPermissions] = useState([])
  const [groupName, setGroupName] = useState('')
  const [toast, setToast] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [nameError, setNameError] = useState(false)

  useEffect(() => {
    const fetchPermissions = async () => {
      try {
        const response = await http.get('/permissions/')
        console.log('group:', group)
        console.log('response.data', response.data)
        if (group?.permissions) {
          const groupPermIds = group.permissions.map(p => p.id)
          
          setAllPermissions(response.data.results.filter(p => !groupPermIds.includes(p.id)))
          setGroupPermissions(group.permissions)
          setGroupName(group.name)
        } else {
          setAllPermissions(response.data.results)
        }
      } catch (error) {
        console.error('Error fetching permissions:', error)
      }
    }

    fetchPermissions()
  }, [group])

  const sortPermissions = (permissions) =>
    permissions.slice().sort((a, b) => a.description.localeCompare(b.description))
  

  return (
    <CRow>
      <CCol xs={12}>
        <CCard className="mb-4">
          <CCardHeader>
            <strong>{t('groups.groupInfo')}</strong>
          </CCardHeader>
          <CCardBody>
            <CForm onSubmit={async (e) => {
              e.preventDefault()
              if (!groupName.trim()) {
                setNameError(true)
                return
              }
              setNameError(false)
              setIsLoading(true)
              try {
                const data = {
                  name: groupName,
                  permission_ids: groupPermissions.map(p => p.id)
                }
                if (group?.id) {
                  await http.put(`/groups/${group.id}/`, data)
                } else {
                  await http.post('/groups/', data)
                }
                setToast({
                  visible: true,
                  color: 'success',
                  message: t('common.savedSuccessfully')
                })
                setTimeout(() => navigate('/admin/groups'), 1500)
              } catch (error) {
                console.error('Error saving group:', error)
                setToast({
                  visible: true,
                  color: 'danger',
                  message: t('common.errorSaving')
                })
              } finally {
                setIsLoading(false)
              }
            }}>
            <CRow className="mb-3">
                <CFormLabel htmlFor="inputEmail3" className="col-sm-2 col-form-label">
                {t('groups.groupName')}
                </CFormLabel>
                <CCol sm={10}>
                <CFormInput 
                  type="text" 
                  id="groupName" 
                  value={groupName}
                  onChange={(e) => {
                    setGroupName(e.target.value)
                    setNameError(false)
                  }}
                  invalid={nameError}
                  disabled={isLoading}
                />
                {nameError && (
                  <div className="invalid-feedback d-block">
                    {t('groups.nameRequired')}
                  </div>
                )}
                </CCol>
            </CRow>
            <CRow className="mb-3">
                <CFormLabel htmlFor="inputPassword3" className="col-sm-2 col-form-label">
                    {t('groups.permissions')}
                </CFormLabel>
                <CCol sm={4}>
                    <CFormLabel>{t('groups.allPermissions')}</CFormLabel>
                    <CFormSelect
                      key={allPermissions.map(p => p.id).join('-')} // força o rerender
                      multiple
                      size="xs"
                      aria-label="Todas as Permissões"
                      style={{ height: '200px' }}
                      disabled={isLoading}
                      options={
                        allPermissions.map(permission => ({
                          value: permission.id,
                          label: permission.description,
                        }))
                      }
                    />
                </CCol>
                <CCol sm={1} className="d-flex flex-column justify-content-center align-items-center">
                    <CButton
                      color="primary"
                      className="mb-2"
                      disabled={isLoading}
                      onClick={() => {
                        const select = document.querySelector('select[aria-label="Todas as Permissões"]')
                        const selectedValues = Array.from(select.selectedOptions).map(option => ({
                          id: option.value,
                          description: option.label
                        }))
                        const updatedAll = allPermissions.filter(
                          permission => !selectedValues.some(selected => selected.id == permission.id)
                        )
                        const updatedGroup = [
                          ...groupPermissions,
                          ...selectedValues.filter(
                            permission => !groupPermissions.some(p => p.id == permission.id)
                          )
                        ]
                        
                        setAllPermissions(sortPermissions(updatedAll))
                        setGroupPermissions(sortPermissions(updatedGroup))
                        
                      }}
                    >
                      <CIcon icon={cilArrowRight} />
                    </CButton>
                    <CButton
                      color="primary"
                      disabled={isLoading}
                      onClick={() => {
                        const select = document.querySelector('select[aria-label="Permissões do Grupo"]')
                        const selectedValues = Array.from(select.selectedOptions).map(option => ({
                          id: option.value,
                          description: option.label
                        }))
                        // Remove as permissões selecionadas da lista de permissões do grupo
                        const updatedGroup = groupPermissions.filter(
                          permission => !selectedValues.some(selected => selected.id == permission.id)
                        )
                        const updatedAll = [
                          ...allPermissions,
                          ...selectedValues.filter(
                            permission => !allPermissions.some(p => p.id == permission.id)
                          )
                        ]
                        
                        setGroupPermissions(sortPermissions(updatedGroup))
                        setAllPermissions(sortPermissions(updatedAll))
                        
                      }}
                    >
                      <CIcon icon={cilArrowLeft} />
                    </CButton>
                </CCol>
                <CCol sm={4}>
                    <CFormLabel>{t('groups.groupPermissions')}</CFormLabel>
                    <CFormSelect
                      key={groupPermissions.map(p => p.id).join('-')} // força o rerender
                      multiple
                      size="xs"
                      aria-label="Permissões do Grupo"
                      style={{ height: '200px' }}
                      disabled={isLoading}
                      options={
                        groupPermissions.map(permission => ({
                          value: permission.id,
                          label: permission.description,
                        }))
                      }
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

GroupForm.propTypes = {
  group: PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    name: PropTypes.string,
    permissions: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
        description: PropTypes.string.isRequired
      })
    )
  })
}

GroupForm.defaultProps = {
  group: null
}

export default GroupForm
