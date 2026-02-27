import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { useTranslation } from 'react-i18next'
import { AgGridReact } from 'ag-grid-react'
import { ModuleRegistry } from 'ag-grid-community'
import {
  AllEnterpriseModule,
  AllCommunityModule,
  colorSchemeDarkBlue,
  colorSchemeLightWarm,
  themeQuartz,
} from 'ag-grid-enterprise'

import {
  CModal,
  CModalHeader,
  CModalTitle,
  CModalBody,
  CSpinner,
} from '@coreui/react'
import { useColorModes } from '@coreui/react'
import http from '../services/http'

// Register AG Grid modules
ModuleRegistry.registerModules([AllEnterpriseModule, AllCommunityModule])

const themeLightWarm = themeQuartz.withPart(colorSchemeLightWarm);
const themeDarkBlue = themeQuartz.withPart(colorSchemeDarkBlue);

const StockErrorsModal = ({ visible, onClose }) => {
  const { t } = useTranslation()
  const [loading, setLoading] = useState(true)
  const [rowData, setRowData] = useState([])
  const { colorMode } = useColorModes('coreui-free-react-admin-template-theme')
  const [currentTheme, setCurrentTheme] = useState(() => colorMode === 'dark' ? themeDarkBlue : themeLightWarm)  

  const columnDefs = [
    { field: 'code', headerName: t('stockErrors.code'), sortable: true, filter: true },
    { field: 'name', headerName: t('stockErrors.name'), sortable: true, filter: true },
    { field: 'supplier', headerName: t('stockErrors.supplier'), sortable: true, filter: true },
    { field: 'section', headerName: t('stockErrors.section'), sortable: true, filter: true },
    { field: 'subsection', headerName: t('stockErrors.subsection'), sortable: true, filter: true },
    // { field: 'nivel5', headerName: t('stockErrors.nivel5'), sortable: true, filter: true },
    { field: 'store', headerName: t('stockErrors.store'), sortable: true, filter: true },
    {
      field: 'stock_available',
      headerName: t('stockErrors.stockAvailable'),
      sortable: true,
      filter: 'agNumberColumnFilter',
      cellClass: 'ag-right-aligned-cell',
      valueGetter: (params) => {
        const value = params.data.stock_available;
        return value === undefined || value === null ? null : Number(value);
      }
    },
    {
      field: 'cost_price',
      headerName: t('stockErrors.costPrice'),
      sortable: true,
      filter: 'agNumberColumnFilter',
      cellClass: 'ag-right-aligned-cell',
      valueGetter: (params) => {
        const value = params.data.cost_price;
        return value === undefined || value === null ? null : Number(value);
      }
    },
    {
      headerName: t('stockErrors.totalCost'),
      field: 'total_cost',
      cellClass: 'ag-right-aligned-cell',
      filter: 'agNumberColumnFilter',
      valueGetter: (params) => {
        const stock = Number(params.data.stock_available);
        const cost = Number(params.data.cost_price);
        if (isNaN(stock) || isNaN(cost)) return '';
        return stock * cost;
      },
      valueFormatter: (params) => {
        if (params.value === '' || params.value === undefined) return '';
        return Number(params.value).toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
      }
    },
    { field: 'stock_available_on', headerName: t('stockErrors.stockAvailableOn'), sortable: true, filter: true, valueFormatter: (params) => {
        if (!params.value) return ''
        const date = new Date(params.value)
        return date.toLocaleDateString('pt-BR')  // dd/mm/yyyy
      }
    },
  ]

  useEffect(() => {
    if (visible) {
      setLoading(true)
      http.get('/items/stock-errors/')
        .then((response) => {
          setRowData(response.data)
          setLoading(false)
        })
        .catch((error) => {
          console.error('Error fetching stock errors:', error)
          setLoading(false)
        })
    }
  }, [visible])

  const defaultColDef = {
    flex: 1,
    minWidth: 100,
    resizable: true,
  }

  return (
    <CModal
      visible={visible}
      onClose={onClose}
      size="xl"
      scrollable
      alignment="center"
    >
      <CModalHeader>
        <CModalTitle className="text-secondary">{t('stockErrors.title')}</CModalTitle>
      </CModalHeader>
      <CModalBody>
        {loading ? (
          <div className="d-flex justify-content-center">
            <CSpinner />
          </div>
        ) : (
          <div className="ag-theme-quartz" style={{ height: '500px', width: '100%' }}>
            <AgGridReact
              rowData={rowData}
              theme={currentTheme}
              columnDefs={columnDefs}
              masterDetail={false}
              defaultColDef={{
                flex: 1,
                minWidth: 60,
                enableRowGroup: true,
                enablePivot: false,
                enableValue: true,
                sortable: true,
                filter: true,
                resizable: true
              }}              
              rowHeight={25}
              headerHeight={30}              
              animateRows={true}
              groupDisplayType={'groupRows'}
              rowGroupPanelShow={'always'}     
              onGridReady={(params) => {
                if (params.api) {
                  setTimeout(() => {
                    params.api.sizeColumnsToFit();
                  }, 100);
                }
              }}              
              paginationPageSize={50}
            />
          </div>
        )}
      </CModalBody>
    </CModal>
  )
}

StockErrorsModal.propTypes = {
  visible: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired
}

export default StockErrorsModal