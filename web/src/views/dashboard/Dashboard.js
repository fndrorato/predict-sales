import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'

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

// Services
import http from '../../services/http'

// Config
import { COMPANY_SETTINGS } from '../../config'

// CoreUI components and hooks
import { useColorModes } from '@coreui/react'
import {
  CCard,
  CCardBody,
  CSpinner
} from '@coreui/react'

// Components
import WidgetsDropdown from '../widgets/WidgetsDropdown'

// Register AG Grid modules
ModuleRegistry.registerModules([AllEnterpriseModule, AllCommunityModule])

const themeLightWarm = themeQuartz.withPart(colorSchemeLightWarm);
const themeDarkBlue = themeQuartz.withPart(colorSchemeDarkBlue);

const Dashboard = () => {
  const [rowData, setRowData] = useState([])
  const [purchaseOrdersData, setPurchaseOrdersData] = useState([])
  const [stockErrorsData, setStockErrorsData] = useState([])
  const [loading, setLoading] = useState(true)
  const { colorMode } = useColorModes('coreui-free-react-admin-template-theme')
  const [currentTheme, setCurrentTheme] = useState(() => colorMode === 'dark' ? themeDarkBlue : themeLightWarm)
  const { t } = useTranslation()


  const [columnDefs] = useState([
    {
      field: 'store',
      headerName: 'Sucursal',
      sortable: true,
      filter: 'agSetColumnFilter',
      enableRowGroup: true,
      rowGroup: false
    },    
    { 
      field: 'product_code', 
      headerName: 'Código', 
      grow: true,
      sortable: true, 
      filter: true,
      enableRowGroup: true,
      rowGroup: false
    },
    { 
      field: 'product_name', 
      headerName: 'Nome do Produto', 
      sortable: true, 
      filter: true,
      enableRowGroup: true,
      rowGroup: false,
      flex: 0,
      autoSize: true,
      suppressSizeToFit: true,
      minWidth: 200
    },
    {
      field: 'category',
      headerName: 'Categoria',
      sortable: true,
      enableRowGroup: true,
      rowGroup: false
    },
    { 
      field: 'stock', 
      headerName: 'Estoque', 
      sortable: true, 
      filter: 'agNumberColumnFilter', 
      type: 'number',
      enableValue: true
    },
    { 
      field: 'sales_frequency', 
      headerName: 'Frec', 
      sortable: true, 
      filter: 'agNumberColumnFilter', 
      type: 'number',
      enableValue: true
    },
    { 
      field: 'no_sales_since', 
      headerName: 'Última Venta', 
      sortable: true, 
      filter: true,
      enableRowGroup: true,
      rowGroup: false,
      valueFormatter: (params) => {
        if (!params.value) return ''
        const date = new Date(params.value)
        return date.toLocaleDateString('pt-BR')  // dd/mm/yyyy
      }         
    },
  ]);
  
  useEffect(() => {
    setCurrentTheme(colorMode === 'dark' ? themeDarkBlue : themeLightWarm)
  }, [colorMode])

  const detailCellRenderer = (params) => {
    const data = params.data.details || [];
    return (
      <div style={{ padding: '20px' }}>
        <h6>Produtos do Pedido</h6>
        <div className="ag-theme-quartz" style={{ height: '200px', width: '100%' }}>
          <AgGridReact
            rowData={data}
            columnDefs={[
              { field: 'product_code', headerName: 'Código' },
              { field: 'product_name', headerName: 'Nome do Produto' },
              { field: 'quantity', headerName: 'Quantidade' },
              { field: 'received', headerName: 'Recebido' }
            ]}
            defaultColDef={{
              flex: 1,
              sortable: true,
              filter: true
            }}
          />
        </div>
      </div>
    );
  };

  const [purchaseOrdersColumnDefs] = useState([
    { 
      field: 'order_number', 
      headerName: 'Número do Pedido',
      minSize: 100,
      maxSize: 250,
      grow: true,
      sortable: true, 
      filter: true,
      cellRenderer: 'agGroupCellRenderer'
    },
    { 
      field: 'store', 
      headerName: 'Filial',
      grow: true,
      minSize: 80,
      maxSize: 120,
      sortable: true, 
      filter: true,
      cellRenderer: 'agGroupCellRenderer'
    },
    { 
      field: 'supplier', 
      headerName: 'Fornecedor',
      grow: true,
      minSize: 150,
      maxSize: 250,
      sortable: true, 
      filter: true,
      cellRenderer: 'agGroupCellRenderer'
    },
    { 
      field: 'date_created', 
      headerName: 'Data de Criação',
      minSize: 100,
      maxSize: 150,
      sortable: true, 
      grow: true,
      filter: true,
      valueFormatter: (params) => {
        if (!params.value) return ''
        const date = new Date(params.value)
        return date.toLocaleDateString('pt-BR')  // dd/mm/yyyy
      }      
    },
    { 
      field: 'date_expected', 
      headerName: 'Data Esperada',
      minSize: 100,
      maxSize: 150,
      grow: true,
      sortable: true, 
      filter: true,
      valueFormatter: (params) => {
        if (!params.value) return ''
        const date = new Date(params.value)
        return date.toLocaleDateString('pt-BR')  // dd/mm/yyyy
      }
    },
    { 
      field: 'complete_delivery',
      headerName: 'Entrega Completa',
      minSize: 100,
      maxSize: 150,
      sortable: true,
      grow: true,
      filter: true,
      cellRenderer: (params) => params.value ? 'Sim' : 'Não'
    }
  ]);

  const [stockErrorsColumnDefs] = useState([
    { field: 'code', headerName: t('stockErrors.code'), sortable: true, filter: true },
    { field: 'name', headerName: t('stockErrors.name'), sortable: true, filter: true },
    { field: 'supplier', headerName: t('stockErrors.supplier'), sortable: true, filter: true },
    { field: 'section', headerName: t('stockErrors.section'), sortable: true, filter: true },
    { field: 'subsection', headerName: t('stockErrors.subsection'), sortable: true, filter: true },
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
    { 
      field: 'stock_available_on', 
      headerName: t('stockErrors.stockAvailableOn'), 
      sortable: true, 
      filter: true, 
      valueFormatter: (params) => {
        if (!params.value) return ''
        const date = new Date(params.value)
        return date.toLocaleDateString('pt-BR')  // dd/mm/yyyy
      }
    },
  ]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const [productsResponse, purchaseOrdersResponse, stockErrorsResponse] = await Promise.all([
          http.get('/stats/no-sales/'),
          http.get('/stats/oc-awaiting/'),
          http.get('/items/stock-errors/')
        ])
        setRowData(productsResponse.data)
        setPurchaseOrdersData(purchaseOrdersResponse.data)
        setStockErrorsData(stockErrorsResponse.data)
      } catch (error) {
        console.error('Erro ao buscar dados:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  return (
    <>
      {/* <WidgetsDropdown className="mb-4" /> */}
      {COMPANY_SETTINGS && COMPANY_SETTINGS.report_items_with_stock_no_sales && (
        <CCard className="mb-4" name="noSalesProducts">
          <CCardBody>
            <h5 className="mb-3">{t('widgets.noSalesProducts')}</h5>
            <div className="ag-theme-quartz" style={{ height: 400, width: '100%' }}>
              <AgGridReact
                key={colorMode}
                rowData={rowData}
                columnDefs={columnDefs}
                theme={currentTheme}
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
                groupDisplayType={'groupRows'}
                rowGroupPanelShow={'always'}              
                rowHeight={25}
                headerHeight={30}
                sideBar={{
                  toolPanels: ['filters'],
                  defaultToolPanel: undefined
                }}
                enableRangeSelection={true}
                statusBar={{
                  statusPanels: [
                    { statusPanel: 'agTotalAndFilteredRowCountComponent', align: 'left' },
                    { statusPanel: 'agAggregationComponent' }
                  ]
                }}
                getRowStyle={(params) => ({
                  background: params.node.rowIndex % 2 === 0 ? 'var(--cui-tertiary-bg)' : 'var(--cui-body-bg)'
                })}
                enableCharts={true}
                getContextMenuItems={(params) => [
                  'autoSizeAll',
                  'separator',
                  'expandAll',
                  'contractAll',
                  'separator',
                  'export'
                ]}
                sizeColumnsToFit={true}
                allowContextMenuWithControlKey={true}
                onGridReady={(params) => {
                  params.api.sizeColumnsToFit();
                  if (rowData.length > 0) {
                    params.api.setDomLayout('autoHeight');
                    params.columnApi.autoSizeAllColumns();
                  }
                }}
                localeText={{
                  contains: t('agGrid.contains'),
                  notContains: t('agGrid.notContains'),
                  equals: t('agGrid.equals'),
                  notEqual: t('agGrid.notEqual'),
                  startsWith: t('agGrid.startsWith'),
                  endsWith: t('agGrid.endsWith'),
                  filterOoo: t('agGrid.filterOoo'),
                  loadingOoo: t('agGrid.loadingOoo'),
                  searchOoo: t('agGrid.searchOoo'),
                  selectAll: t('agGrid.selectAll'),
                  selectAllSearchResults: t('agGrid.selectAllSearchResults'),
                  clearFilter: t('agGrid.clearFilter'),
                  clearSearch: t('agGrid.clearSearch'),
                  blanks: t('agGrid.blanks'),
                  noMatches: t('agGrid.noMatches'),
                  greaterThan: t('agGrid.greaterThan'),
                  greaterThanOrEqual: t('agGrid.greaterThanOrEqual'),
                  lessThan: t('agGrid.lessThan'),
                  lessThanOrEqual: t('agGrid.lessThanOrEqual'),
                  between: t('agGrid.between')
                }}
              />
            </div>
          </CCardBody>
        </CCard>
      )}

      {COMPANY_SETTINGS && COMPANY_SETTINGS.report_orders_awaiting_confirmation && (
        <CCard className="mb-4" name="purchaseOrders">
          <CCardBody>
            <h5 className="mb-3">{t('widgets.problemPurchaseOrders')}</h5>
            <div
              style={{ height: 600, width: '100%' }}
            >
              <AgGridReact
                rowData={purchaseOrdersData}
                columnDefs={purchaseOrdersColumnDefs}
                theme={currentTheme}
                masterDetail={true}
                detailCellRenderer={detailCellRenderer}
                defaultColDef={{
                  flex: 1,
                  minWidth: 80,
                  enableRowGroup: true,
                  enablePivot: false,
                  enableValue: true,
                  sortable: true,
                  filter: true,
                  resizable: true
                }}
                rowHeight={25}
                headerHeight={30}
                sideBar={{
                  toolPanels: ['filters'],
                  defaultToolPanel: undefined
                }}
                groupDisplayType={'groupRows'}
                rowGroupPanelShow={'always'}
                enableRangeSelection={true}
                statusBar={{
                  statusPanels: [
                    { statusPanel: 'agTotalAndFilteredRowCountComponent', align: 'left' },
                    { statusPanel: 'agAggregationComponent' }
                  ]
                }}
                getRowStyle={(params) => ({
                  background: params.node.rowIndex % 2 === 0 ? 'var(--cui-tertiary-bg)' : 'var(--cui-body-bg)'
                })}
                enableCharts={true}
                getContextMenuItems={(params) => [
                  'autoSizeAll',
                  'separator',
                  'expandAll',
                  'contractAll',
                  'separator',
                  'export'
                ]}
                sizeColumnsToFit={true}
                allowContextMenuWithControlKey={true}
                onGridReady={(params) => {
                  params.api.sizeColumnsToFit();
                  if (purchaseOrdersData.length > 0) {
                    params.api.setDomLayout('autoHeight');
                    params.columnApi.autoSizeAllColumns();
                  }
                }}
                localeText={{
                  contains: t('agGrid.contains'),
                  notContains: t('agGrid.notContains'),
                  equals: t('agGrid.equals'),
                  notEqual: t('agGrid.notEqual'),
                  startsWith: t('agGrid.startsWith'),
                  endsWith: t('agGrid.endsWith'),
                  filterOoo: t('agGrid.filterOoo'),
                  loadingOoo: t('agGrid.loadingOoo'),
                  searchOoo: t('agGrid.searchOoo'),
                  selectAll: t('agGrid.selectAll'),
                  selectAllSearchResults: t('agGrid.selectAllSearchResults'),
                  clearFilter: t('agGrid.clearFilter'),
                  clearSearch: t('agGrid.clearSearch'),
                  blanks: t('agGrid.blanks'),
                  noMatches: t('agGrid.noMatches'),
                  greaterThan: t('agGrid.greaterThan'),
                  greaterThanOrEqual: t('agGrid.greaterThanOrEqual'),
                  lessThan: t('agGrid.lessThan'),
                  lessThanOrEqual: t('agGrid.lessThanOrEqual'),
                  between: t('agGrid.between')
                }}
              />
            </div>
          </CCardBody>
        </CCard>
      )}

      {COMPANY_SETTINGS && COMPANY_SETTINGS.report_negative_availability && (
        <CCard className="mb-4" name="stockErrors">
          <CCardBody>
            <h5 className="mb-3">{t('stockErrors.title')}</h5>
            {loading ? (
              <div className="d-flex justify-content-center">
                <CSpinner />
              </div>
            ) : (
              <div className="ag-theme-quartz" style={{ height: 500, width: '100%' }}>
                <AgGridReact
                  rowData={stockErrorsData}
                  columnDefs={stockErrorsColumnDefs}
                  theme={currentTheme}
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
                  sideBar={{
                    toolPanels: ['filters'],
                    defaultToolPanel: undefined
                  }}
                  enableRangeSelection={true}
                  statusBar={{
                    statusPanels: [
                      { statusPanel: 'agTotalAndFilteredRowCountComponent', align: 'left' },
                      { statusPanel: 'agAggregationComponent' }
                    ]
                  }}
                  getRowStyle={(params) => ({
                    background: params.node.rowIndex % 2 === 0 ? 'var(--cui-tertiary-bg)' : 'var(--cui-body-bg)'
                  })}
                  enableCharts={true}
                  getContextMenuItems={(params) => [
                    'autoSizeAll',
                    'separator',
                    'expandAll',
                    'contractAll',
                    'separator',
                    'export'
                  ]}
                  sizeColumnsToFit={true}
                  allowContextMenuWithControlKey={true}
                  onGridReady={(params) => {
                    if (params.api) {
                      setTimeout(() => {
                        params.api.sizeColumnsToFit();
                      }, 100);
                    }
                  }}
                  localeText={{
                    contains: t('agGrid.contains'),
                    notContains: t('agGrid.notContains'),
                    equals: t('agGrid.equals'),
                    notEqual: t('agGrid.notEqual'),
                    startsWith: t('agGrid.startsWith'),
                    endsWith: t('agGrid.endsWith'),
                    filterOoo: t('agGrid.filterOoo'),
                    loadingOoo: t('agGrid.loadingOoo'),
                    searchOoo: t('agGrid.searchOoo'),
                    selectAll: t('agGrid.selectAll'),
                    selectAllSearchResults: t('agGrid.selectAllSearchResults'),
                    clearFilter: t('agGrid.clearFilter'),
                    clearSearch: t('agGrid.clearSearch'),
                    blanks: t('agGrid.blanks'),
                    noMatches: t('agGrid.noMatches'),
                    greaterThan: t('agGrid.greaterThan'),
                    greaterThanOrEqual: t('agGrid.greaterThanOrEqual'),
                    lessThan: t('agGrid.lessThan'),
                    lessThanOrEqual: t('agGrid.lessThanOrEqual'),
                    between: t('agGrid.between')
                  }}
                  paginationPageSize={50}
                />
              </div>
            )}
          </CCardBody>
        </CCard>
      )}
    </>
  )
}

export default Dashboard
