import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types';
import { CCol, CFormInput, CFormLabel, CRow, CInputGroup, CButton, CButtonGroup, CFormSelect, CCard, CCardHeader, CCardBody, CSpinner, CToast, CToastBody, CToastHeader, CToaster } from '@coreui/react'
import CIcon from '@coreui/icons-react'
import { cilSearch, cilList, cilSave, cilX } from '@coreui/icons'
import { CChartLine } from '@coreui/react-chartjs'

import http from 'src/services/http'
import ItemModal from 'src/components/ItemModal'

const SalesForecastForm = () => {
  const formatNumber = (number) => {
    return number?.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return dateStr;
    const [day, month, year] = dateStr.split('/');
    return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
  };

  const [currentDate, setCurrentDate] = useState('');

  const [stores, setStores] = useState([]);
  const [storeName, setStoreName] = useState('');
  const [itemName, setItemName] = useState('');
  const [toast, setToast] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [dateError, setDateError] = useState('');
  const [daysStockDesired, setDaysStockDesired] = useState('');
  const [chartData, setChartData] = useState(null);
  const [showItemModal, setShowItemModal] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'F9' && document.activeElement.id === 'item') {
        e.preventDefault();
        setShowItemModal(true);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  useEffect(() => {
    const today = new Date();
    const sixMonthsAgo = new Date(today);
    sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);
    sixMonthsAgo.setDate(1); // Primeiro dia do mês
    
    const lastDayOfLastMonth = new Date(today.getFullYear(), today.getMonth(), 0);
    
    const formattedStartDate = sixMonthsAgo.toISOString().split('T')[0];
    const formattedEndDate = lastDayOfLastMonth.toISOString().split('T')[0];
    
    setStartDate(formattedStartDate);
    setEndDate(formattedEndDate);

    const fetchData = async () => {
      try {
        const response = await http.get('/stores/');
        setStores(response.data);
      } catch (error) {
        console.error('Erro ao buscar lojas:', error);
        setToast({
          visible: true,
          color: 'danger',
          message: 'Erro ao carregar lista de lojas'
        });
      }
    };

    fetchData();
  }, []);



  const handleItemSelect = async (itemCode) => {
    try {
      const response = await http.get(`/item/?code=${itemCode}`);
      if (response.data && response.data.length > 0) {
        setItemName(response.data[0].name);
        document.getElementById('item').value = itemCode;
      }
    } catch (error) {
      console.error('Erro ao buscar informações do produto:', error);
      setToast({
        visible: true,
        color: 'danger',
        message: 'Erro ao buscar informações do produto'
      });
    }
  };

  return (
    <>
      <CCard className="mb-1">
        <CCardHeader className="py-2 d-flex justify-content-between align-items-center">
          <strong>Previsão de Vendas</strong>

        </CCardHeader>
        <CCardBody className="py-2">   
        <CRow className="mb-1 g-2">
          <CFormLabel htmlFor="name" className="col-sm-1 col-form-label col-form-label-sm text-body">
            Sucursal
          </CFormLabel>
          <CCol sm={1}>
            <CFormInput
              type="text"
              className="form-control form-control-sm"
              id="store"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  const store = stores.find(s => s.code.toString() === e.target.value);
                  if (store) {
                    setStoreName(store.name);
                  } else {
                    setStoreName('');
                  }
                  // Move o foco para o campo supplier
                  document.getElementById('item').focus();
                }
              }}
            />          
          </CCol>
          <CCol sm={4}>
            <CFormInput
              type="text"
              className="form-control form-control-sm"
              id="store_name"
              value={storeName}
              disabled
            />
          </CCol>

          <CFormLabel htmlFor="item" className="col-sm-1 col-form-label col-form-label-sm text-body" style={{ paddingRight: 0 }}>
            Produto
          </CFormLabel>
          <CCol sm={1}>
            <CFormInput
              type="text"
              className="form-control form-control-sm"
              id="item"
              onKeyDown={async (e) => {
                if (e.key === 'Enter' || e.key === 'Tab') {
                  e.preventDefault();
                  const itemValue = e.target.value;

                  try {
                    const response = await http.get(`/item/?code=${itemValue}`);
                    if (response.data && response.data.length > 0) {
                      setItemName(response.data[0].name);
                    } else {
                      setItemName('');
                      setToast({
                        visible: true,
                        color: 'danger',
                        message: 'Produto não encontrado'
                      });
                    }
                  } catch (error) {
                    console.error('Erro ao buscar informações do produto:', error);
                    setItemName('');
                    setToast({
                      visible: true,
                      color: 'danger',
                      message: 'Produto não encontrado'
                    });
                  }
                }
              }}
            />
          </CCol>
          <CCol sm={4}>
          <CFormInput
              type="text"
              className="form-control form-control-sm"
              id="item_name"
              value={itemName}
              disabled
            />
          </CCol>    
        </CRow>
        <CRow className="mb-1 g-2">

          <CFormLabel htmlFor="start_date" className="col-sm-1 col-form-label col-form-label-sm text-body">
            Data Inicial
          </CFormLabel>
          <CCol sm={2}>
            <CFormInput
              type="date"
              className="form-control form-control-sm"
              id="start_date"
              value={startDate}
              min={new Date(new Date().setDate(new Date().getDate() + 1)).toISOString().split('T')[0]}
              onChange={(e) => {
                const newStartDate = e.target.value;
                setStartDate(newStartDate);
                setDateError('');
                
                if (endDate && newStartDate >= endDate) {
                  setDateError('A data inicial deve ser menor que a data final');
                }
              }}
              required
            />
          </CCol>

          <CFormLabel htmlFor="end_date" className="col-sm-1 col-form-label col-form-label-sm text-body">
            Data Final
          </CFormLabel>
          <CCol sm={2}>
            <CFormInput
              type="date"
              className="form-control form-control-sm"
              id="end_date"
              value={endDate}
              min={startDate}
              onChange={(e) => {
                const newEndDate = e.target.value;
                setEndDate(newEndDate);
                setDateError('');
                
                if (startDate && newEndDate <= startDate) {
                  setDateError('A data final deve ser maior que a data inicial');
                }
              }}
              required
            />
            {dateError && (
              <div className="text-danger small mt-1">{dateError}</div>
            )}
          </CCol>   
          <CCol sm={1}>
            <CButton
              color="primary"
              size="sm"
              className="w-100"
              disabled={isLoading || !startDate || !endDate || dateError || !document.getElementById('store').value || !document.getElementById('item').value}
              onClick={async () => {
                setIsLoading(true);
                try {
                  const storeValue = document.getElementById('store').value;
                  const itemValue = document.getElementById('item').value;
                  const response = await http.get(`/sales/reports/item-prediction?end_date=${endDate}&item=${itemValue}&start_date=${startDate}&store=${storeValue}`);
                  
                  if (response.data) {
                    const labels = response.data.map(item => item.week);
                    const salesData = response.data.map(item => item.sales);
                    const predictionData = response.data.map(item => item.prediction);

                    setChartData({
                      labels,
                      datasets: [
                        {
                          label: 'Vendas',
                          backgroundColor: 'rgba(0, 123, 255, 0.1)',
                          borderColor: 'rgb(0, 123, 255)',
                          pointBackgroundColor: 'rgb(0, 123, 255)',
                          data: salesData,
                        },
                        {
                          label: 'Previsão',
                          backgroundColor: 'rgba(40, 167, 69, 0.1)',
                          borderColor: 'rgb(40, 167, 69)',
                          pointBackgroundColor: 'rgb(40, 167, 69)',
                          data: predictionData,
                        },
                      ],
                    });
                  }
                } catch (error) {
                  console.error('Erro ao processar pedido:', error);
                  setToast({
                    visible: true,
                    color: 'danger',
                    message: 'Erro ao carregar dados da previsão'
                  });
                } finally {
                  setIsLoading(false);
                }
              }}
            >
              {isLoading ? <CSpinner size="sm" /> : 'Processar'}
            </CButton>
          </CCol>                       
        </CRow>

      </CCardBody>
    </CCard>


      {chartData && (
        <CCard className="mt-3">
          <CCardHeader className="py-2">
            <strong>Gráfico Comparativo: Vendas x Previsão</strong>
          </CCardHeader>
          <CCardBody>
            <CChartLine
              data={chartData}
              options={{
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    display: true,
                  }
                },
                scales: {
                  x: {
                    grid: {
                      drawOnChartArea: false,
                    },
                  },
                  y: {
                    beginAtZero: true,
                    grid: {
                      drawOnChartArea: true,
                    },
                  },
                },
              }}
              style={{ height: '400px' }}
            />
          </CCardBody>
        </CCard>
      )}
      <ItemModal
        visible={showItemModal}
        onClose={() => setShowItemModal(false)}
        onSelect={handleItemSelect}
      />

      {toast && (
        <CToaster placement="top-end">
          <CToast
            visible
            color={toast.color}
            className="text-white align-items-center"
            onClose={() => setToast(null)}
          >
            <div className="d-flex">
              <CToastBody>{toast.message}</CToastBody>
            </div>
          </CToast>
        </CToaster>
      )}
    </>
  )
}

export default SalesForecastForm;
