import React, { useEffect, useState, useMemo } from 'react'
// AG Grid imports
import { AgGridReact } from 'ag-grid-react'
import { ModuleRegistry } from 'ag-grid-community'
import {
  AllEnterpriseModule,
  AllCommunityModule,
  colorSchemeDarkBlue,
  colorSchemeLightWarm,
  themeQuartz,
} from 'ag-grid-enterprise'
import { useNavigate } from 'react-router-dom'
import {
  CButton,
  CCard,
  CCardBody,
  CCardHeader,
  CCol,
  CRow,
  CSpinner,
} from '@coreui/react'
import { cilPlus, cilPencil } from '@coreui/icons'
import CIcon from '@coreui/icons-react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import http from 'src/services/http'
import { useColorModes } from '@coreui/react';

// Register AG Grid modules
ModuleRegistry.registerModules([AllEnterpriseModule, AllCommunityModule])

const Users = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const { colorMode } = useColorModes()

  const currentTheme = useMemo(() => {
    const themeLightWarm = themeQuartz.withPart(colorSchemeLightWarm);
    const themeDarkBlue = themeQuartz.withPart(colorSchemeDarkBlue);
    return colorMode === 'dark' ? themeDarkBlue : themeLightWarm;
  }, [colorMode]);

  const agGridThemeClass = useMemo(() => (
    colorMode === 'dark' ? 'ag-theme-quartz-dark' : 'ag-theme-quartz'
  ), [colorMode]);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await http.get('/users/')
        setUsers(response.data.results)
      } catch (err) {
        setError(t('common.errorLoadingGroups'))
      } finally {
        setLoading(false)
      }
    }

    fetchUsers()
  }, [t])

  const columnDefs = useMemo(() => [
    { field: 'first_name', headerName: t('users.firstName'), sortable: true, filter: true, enableRowGroup: true, rowGroup: false },
    { field: 'last_name', headerName: t('users.lastName'), sortable: true, filter: true, enableRowGroup: true, rowGroup: false },
    { field: 'username', headerName: t('users.username'), sortable: true, filter: true },
    { field: 'email', headerName: t('users.email'), sortable: true, filter: true },
    { 
      field: 'is_active', 
      headerName: t('users.isActive'), 
      sortable: true, 
      filter: true,
      cellRenderer: (params) => params.value ? '✓' : '✗'
    },
    { 
      field: 'group_name', 
      headerName: t('users.groups'), 
      sortable: true, 
      filter: true,
      enableRowGroup: true,
      rowGroup: false
    },
    {
      headerName: 'Editar',
      field: 'actions',
      sortable: false,
      filter: false,
      enableRowGroup: false,
      suppressMovable: true,
      minWidth: 100,
      maxWidth: 100,
      cellRenderer: (params) => (
        <CButton
          color="info"
          size="sm"
          onClick={() => navigate(`/admin/users/${params.data.id}`)}
        >
          <CIcon icon={cilPencil} />
        </CButton>
      )
    }
  ], [t]);

  const defaultColDef = useMemo(() => ({
    flex: 1,
    resizable: true,
    minWidth: 100,
    suppressMenu: false,
    suppressHeaderMenuButton: false,
    menuTabs: ['filterMenuTab', 'generalMenuTab']
  }), []);  

  return (
    <CRow>
      <CCol xs={12} className="mb-4">
        <Link to="/admin/users/new">
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
                <div key={agGridThemeClass} className={agGridThemeClass} style={{ height: '400px', width: '100%' }}>
                <AgGridReact
                  rowData={users}
                  columnDefs={columnDefs}
                  defaultColDef={defaultColDef}
                  animateRows={true}
                  enableRangeSelection={true}
                  pagination={false}
                  paginationAutoPageSize={true}
                  theme={currentTheme}
                  rowHeight={30}
                  groupDisplayType="multipleColumns"
                  rowGroupPanelShow="always"
                />
              </div>
            )}
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>
  )
}

export default Users
