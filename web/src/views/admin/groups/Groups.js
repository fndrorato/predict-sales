import React, { useEffect, useState } from 'react'
import {
  CButton,
  CCard,
  CCardBody,
  CCardHeader,
  CCol,
  CListGroup,
  CListGroupItem,
  CRow,
  CSpinner,
} from '@coreui/react'
import { cilPlus } from '@coreui/icons'
import CIcon from '@coreui/icons-react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import http from 'src/services/http'

const Groups = () => {
  const { t } = useTranslation()
  const [groups, setGroups] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchGroups = async () => {
      try {
        const response = await http.get('/groups/')
        setGroups(response.data.results)
      } catch (err) {
        setError(t('common.errorLoadingGroups'))
      } finally {
        setLoading(false)
      }
    }

    fetchGroups()
  }, [t])

  return (
    <CRow>
      <CCol xs={12} className="mb-4">
        <Link to="/admin/groups/new">
          <CButton color="primary">
            <CIcon icon={cilPlus} className="me-2" />
            {t('common.newGroup')}
          </CButton>
        </Link>
      </CCol>
      <CCol xs={12}>
        <CCard className="mb-4">
          <CCardHeader>
            <strong>{t('common.groups')}</strong>
          </CCardHeader>
          <CCardBody>
            {loading ? (
              <div className="text-center">
                <CSpinner />
              </div>
            ) : error ? (
              <div className="text-danger">{error}</div>
            ) : (
              <CListGroup>
                {groups.map((group) => (
                  <CListGroupItem key={group.id} as={Link} to={`/admin/groups/${group.id}`}>
                    {group.name}
                  </CListGroupItem>
                ))}
              </CListGroup>
            )}
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>
  )
}

export default Groups
