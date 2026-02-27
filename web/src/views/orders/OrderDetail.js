import React, { useEffect, useRef, useState } from 'react';
import PropTypes from 'prop-types';
import Handsontable from 'handsontable/base';
import { registerAllModules } from 'handsontable/registry';
import { HotTable } from '@handsontable/react-wrapper';
import 'handsontable/styles/handsontable.min.css';
import '../../scss/_handsontable-theme.scss';
import { useColorModes, CToast, CToastBody, CToastHeader, CToaster } from '@coreui/react';
import CIcon from '@coreui/icons-react';
import { cilChartLine } from '@coreui/icons';
import http from '../../services/http';
import ItemStatsModal from './ItemStatsModal';
import { COMPANY_SETTINGS } from '../../config';

// Registra todos os módulos do Handsontable
registerAllModules();

const OrderDetail = ({ orderData, store, setTotalAmount, statusId }) => {
  const data = orderData || [];
  const { colorMode } = useColorModes('coreui-free-react-admin-template-theme');
  const hotRef = useRef(null);
  const [itemStats, setItemStats] = useState(null);
  const [showStatsModal, setShowStatsModal] = useState(false);
  const [toast, setToast] = useState(null);

  const handleItemClick = async (row) => {
    const rowData = data[row];
    try {
      const response = await http.get('sales/item-stats', {
        params: { item: rowData.item_code, store }
      });
      setItemStats(response.data);
      setShowStatsModal(true);
    } catch (error) {
      console.error('Erro ao carregar estatísticas do item:', error);
    }
  };

  const calculateSuggestedQuantity = (row) => {
    if (!row.sale_prediction) return 0;
  
    const startDate = new Date(document.getElementById('start_date_prediction').value);
    const endDate = new Date(document.getElementById('end_date_prediction').value);
    const daysStockDesired = row.days_stock || 0;
    const packSize = row.pack_size || 0;
  
    const daysDiff = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
    if (daysDiff <= 0 || daysStockDesired <= 0) return 0;
  
    let calculatedValue = (row.sale_prediction / daysDiff * daysStockDesired) - (row.stock_available || 0);
  
    if (calculatedValue <= 0) return 0;
  
    // Se houver packSize, arredonda para o múltiplo superior
    if (packSize > 0) {
      return Math.ceil(calculatedValue / packSize) * packSize;
    }
  
    // Caso contrário, arredonda normalmente
    return Math.round(calculatedValue);
  };

  const calculateStockDays = (row) => {
    if (!row.stock_available || !row.sale_prediction) return '';
    const startDate = new Date(document.getElementById('start_date_prediction').value);
    const endDate = new Date(document.getElementById('end_date_prediction').value);
    const daysDiff = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
    if (daysDiff <= 0 || row.sale_prediction <= 0) return '';
    const dailySales = row.sale_prediction / daysDiff;
    return dailySales > 0 ? Math.round(row.stock_available / dailySales) : '';
  };

  const columns = [
    {
      title: '',
      readOnly: true,
      width: 30,
      renderer: (instance, td, row) => {
        td.innerHTML = '<div style="cursor: pointer; display: flex; justify-content: center;"><svg width="16" height="16" viewBox="0 0 512 512"><path fill="currentColor" d="M496 384H64V80c0-8.84-7.16-16-16-16H16C7.16 64 0 71.16 0 80v336c0 17.67 14.33 32 32 32h464c8.84 0 16-7.16 16-16v-32c0-8.84-7.16-16-16-16zM464 96H345.94c-21.38 0-32.09 25.85-16.97 40.97l32.4 32.4L288 242.75l-73.37-73.37c-12.5-12.5-32.76-12.5-45.25 0l-68.69 68.69c-6.25 6.25-6.25 16.38 0 22.63l22.62 22.62c6.25 6.25 16.38 6.25 22.63 0L192 237.25l73.37 73.37c12.5 12.5 32.76 12.5 45.25 0l96-96 32.4 32.4c15.12 15.12 40.97 4.41 40.97-16.97V112c.01-8.84-7.15-16-15.99-16z"/></svg></div>';
        // Verifica se a configuração view_sales_last_weeks está habilitada antes de adicionar o event listener
        if (COMPANY_SETTINGS.view_sales_last_weeks) {
          td.addEventListener('click', () => handleItemClick(row));
        }
        return td;
      }
    },
    { data: 'item_code', title: 'Código', readOnly: true },
    { data: 'item_name', title: 'Descrição', readOnly: true },
    { data: 'days_stock', title: 'DS', readOnly: true },
    { data: 'pack_size', title: 'Bulto', readOnly: true },  
    { data: 'date_last_purchase', title: 'Fecha', readOnly: true },
    { data: 'quantity_last_purchase', title: 'Cant.', type: 'numeric', readOnly: true },
    { data: 'sale_prediction', title: 'Venda', type: 'numeric', readOnly: true },
    { 
      data: 'quantity_suggested', 
      title: 'Sug', 
      type: 'numeric', 
      readOnly: true,
      className: 'htRight',
      renderer: (instance, td, row, col, prop, value, cellProperties) => {
        td.innerHTML = calculateSuggestedQuantity(instance.getSourceDataAtRow(row));
        return td;
      }
    },
    { 
      data: 'cantCompra', 
      title: 'Cant.', 
      type: 'numeric',
      readOnly: statusId === '3',
      validator: function(value, callback) {
        if (value < 0) {
          setToast({
            visible: true,
            color: 'danger',
            message: 'O valor não pode ser negativo'
          });
          callback(false);
        } else {
          callback(true);
        }
      }
    },
    { 
      data: 'bonificaciones', 
      title: 'Bonific.', 
      type: 'numeric',
      readOnly: statusId === '3',
      validator: function(value, callback) {
        if (value < 0) {
          setToast({
            visible: true,
            color: 'danger',
            message: 'O valor não pode ser negativo'
          });
          callback(false);
        } else {
          callback(true);
        }
      }
    },    
    { 
      data: 'descuento', 
      title: 'Desc', 
      type: 'numeric', 
      suffix: '%',
      readOnly: statusId === '3',
      validator: function(value, callback) {
        callback(value >= 0);
      }
    },
    { data: 'stock_available', title: 'Stock', type: 'numeric', readOnly: true },
    { 
      data: 'current_stock_days', 
      title: 'Actual', 
      readOnly: true,
      className: 'htRight',
      renderer: (instance, td, row, col, prop, value, cellProperties) => {
        td.innerHTML = calculateStockDays(instance.getSourceDataAtRow(row));
        return td;
      }
    },
    { 
      data: 'rotacionCompra', 
      title: '+ Compra', 
      readOnly: true,
      className: 'htRight',
      renderer: (instance, td, row, col, prop, value, cellProperties) => {
        const rowData = instance.getSourceDataAtRow(row);
        const cantCompra = parseFloat(rowData.cantCompra) || 0;
        const bonificaciones = parseFloat(rowData.bonificaciones) || 0;
        const startDate = new Date(document.getElementById('start_date_prediction').value);
        const endDate = new Date(document.getElementById('end_date_prediction').value);
        const daysDiff = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
        
        if (daysDiff <= 0) {
          td.innerHTML = '';
          return td;
        }
        
        const stockDays = calculateStockDays(rowData);
        const rotacion = ((cantCompra + bonificaciones) / daysDiff) + (parseFloat(stockDays) || 0);
        td.innerHTML = rotacion.toFixed(1);
        return td;
      }
    },
    { data: 'purchase_price', title: 'P.Costo', type: 'numeric', readOnly: true },    
    { 
      data: 'total', 
      title: 'Total', 
      type: 'numeric',
      readOnly: true,
      className: 'htRight',
      renderer: (instance, td, row, col, prop, value, cellProperties) => {
        const rowData = instance.getSourceDataAtRow(row);
        const cantCompra = parseFloat(rowData.cantCompra) || 0;
        const purchasePrice = parseFloat(rowData.purchase_price) || 0;
        const total = Math.round(cantCompra * purchasePrice);
        td.innerHTML = total.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
        return td;
      }
    }    
  ];

  // Função para verificar a diferença percentual entre cantCompra e quantity_suggested
  const checkQuantityDifference = (row) => {
    const cantCompra = parseFloat(row.cantCompra);
    
    // Verifica se cantCompra é negativo
    if (cantCompra < 0) {
      return 'danger';
    }
    
    const suggestedQty = calculateSuggestedQuantity(row);
    
    if (!cantCompra || cantCompra <= 0 || !suggestedQty || suggestedQty <= 0) {
      return 'normal';
    }
    
    // Calcula a diferença percentual usando o módulo da diferença
    const diff = Math.abs(cantCompra - suggestedQty) / suggestedQty * 100;
    
    if (diff < 10) {
      return 'normal';
    } else if (diff >= 10 && diff <= 30) {
      return 'warning';
    } else {
      return 'danger';
    }
  };

  const settings = {
    licenseKey: 'non-commercial-and-evaluation',
    data,
    columns,
    colHeaders: true,
    height: 400,
    width: '100%',
    stretchH: 'all',
    autoWrapRow: true,
    manualRowResize: true,
    manualColumnResize: true,
    filters: true,
    dropdownMenu: true,
    contextMenu: false,
    stripes: true,
    allowInsertRow: false,
    allowRemoveRow: false,
    allowInsertColumn: false,
    allowRemoveColumn: false,
    rowHeights: [30, 23],
    readOnly: statusId === '3',
    cells: function(row, col) {
      const cellProperties = {};
      const rowData = this.instance.getSourceDataAtRow(row);
      if (rowData) {
        const status = checkQuantityDifference(rowData);
        if (status === 'warning') {
          cellProperties.className = 'hot-row-warning';
        } else if (status === 'danger') {
          cellProperties.className = 'hot-row-danger';
        }
      }
      return cellProperties;
    },
    nestedHeaders: [
      [
        { label: '', colspan: 1 },
        { label: '', colspan: 4 },
        { label: 'Últ. Compra', colspan: 2 },
        { label: 'Previsão', colspan: 2 },
        { label: 'Compras', colspan: 3 },
        { label: '', colspan: 1 },
        { label: 'Rotación', colspan: 2 },
        { label: 'Costo', colspan: 3 },
        { label: '', colspan: 1 },        
      ],
      columns.map(col => ({ label: col.title }))
    ],
    afterRender: () => {
      // Garante que o tema continue aplicado após renderizações dinâmicas
      const hotElement = hotRef.current?.hotInstance?.rootElement;
      if (hotElement) {
        hotElement.classList.remove('hot-theme-light', 'hot-theme-dark');
        hotElement.classList.add(colorMode === 'dark' ? 'hot-theme-dark' : 'hot-theme-light');
        
        // Aplica formatação condicional às linhas
        const instance = hotRef.current?.hotInstance;
        if (instance) {
          const tbody = hotElement.querySelector('.htCore tbody');
          if (tbody) {
            const rows = tbody.querySelectorAll('tr');
            rows.forEach((row, index) => {
              // Remove classes anteriores
              row.classList.remove('hot-row-warning', 'hot-row-danger');
              
              // Obtém os dados da linha
              const rowData = instance.getSourceDataAtRow(index);
              if (rowData) {
                // Usa a função checkQuantityDifference para determinar o status
                const status = checkQuantityDifference(rowData);
                
                if (status === 'warning') {
                  row.classList.add('hot-row-warning');
                } else if (status === 'danger') {
                  row.classList.add('hot-row-danger');
                }
              }
            });
          }
        }
      }
    },
    afterChange: (changes, source) => {
      if (!changes || source === 'loadData') return;
  
      const updatedData = hotRef.current.hotInstance.getSourceData(); // ou use o state
      const totalAmount = updatedData.reduce((acc, row) => {
        const cantCompra = parseFloat(row.cantCompra) || 0;
        const purchasePrice = parseFloat(row.purchase_price) || 0;
        return acc + (cantCompra * purchasePrice);
      }, 0);
  
      setTotalAmount(Math.round(totalAmount));
    }    
  };

  // Calcula o total_amount quando os dados são carregados
  useEffect(() => {
    if (data && data.length > 0) {
      const totalAmount = data.reduce((acc, row) => {
        const cantCompra = parseFloat(row.cantCompra) || 0;
        const purchasePrice = parseFloat(row.purchase_price) || 0;
        return acc + (cantCompra * purchasePrice);
      }, 0);
      setTotalAmount(Math.round(totalAmount));
    }
  }, [data, setTotalAmount]);

  // Também atualiza no efeito (ex: ao trocar tema manualmente)
  useEffect(() => {
    const hotElement = hotRef.current?.hotInstance?.rootElement;
    if (hotElement) {
      hotElement.classList.remove('hot-theme-light', 'hot-theme-dark');
      hotElement.classList.add(colorMode === 'dark' ? 'hot-theme-dark' : 'hot-theme-light');

      // Força o re-render do Handsontable para aplicar o estilo nas novas linhas
      hotRef.current?.hotInstance?.render();
    }
  }, [colorMode]);
  // ref={hotRef}
  return (
    <div id="order-detail">
      <HotTable ref={hotRef} {...settings} />
      <ItemStatsModal
        visible={showStatsModal}
        onClose={() => setShowStatsModal(false)}
        itemStats={itemStats}
      />
      {toast && (
        <CToaster placement="top-end">
          <CToast visible={toast.visible} color={toast.color} onClose={() => setToast(null)} autohide delay={1500}>
            <CToastHeader closeButton>Atenção</CToastHeader>
            <CToastBody>{toast.message}</CToastBody>
          </CToast>
        </CToaster>
      )}
    </div>
  );
};

OrderDetail.propTypes = {
  orderData: PropTypes.array,
  store: PropTypes.number.isRequired,
  setTotalAmount: PropTypes.func.isRequired,
  statusId: PropTypes.number
};

export default OrderDetail;
