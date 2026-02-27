import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types';
import { CCol, CFormInput, CFormLabel, CRow, CInputGroup, CButton, CButtonGroup, CFormSelect, CCard, CCardHeader, CCardBody, CSpinner, CToast, CToastBody, CToastHeader, CToaster } from '@coreui/react'
import OrderModal from './OrderModal'
import OrderLogModal from './OrderLogModal'
import CIcon from '@coreui/icons-react'
import { cilSearch, cilList, cilSave, cilX, cilCloudDownload } from '@coreui/icons'
import { getFirstName, getLastName } from 'src/services/auth'
import http from 'src/services/http'
import SupplierModal from 'src/components/SupplierModal'

const OrderForm = ({ onOrderDataReceived, totalAmount }) => {
  const [orderId, setOrderId] = useState(() => {
    const hash = window.location.hash;
    const queryString = hash.includes('?') ? hash.split('?')[1] : '';
    const params = new URLSearchParams(queryString);
    return params.get('id');
  });

  const getIdFromHash = () => {
    const hash = window.location.hash; // exemplo: "#/orders?id=3"
    const queryString = hash.includes('?') ? hash.split('?')[1] : '';
    const params = new URLSearchParams(queryString);
    return params.get('id');
  };

  useEffect(() => {
    const handleHashChange = () => {
      const newOrderId = getIdFromHash();
      setOrderId(newOrderId);
    };

    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  useEffect(() => {
    if (orderId && orderId.trim()) {
      document.getElementById('id').value = orderId;
      const searchButton = document.getElementById('search-button');
      if (searchButton) {
        searchButton.click();
      }
    } else {
      // Limpa os campos quando não houver ID
      setStoreName('');
      setSupplierName('');
      setOcNumbersPending([]);
      setSelectedSection('');
      setSelectedSubsection('');
      // setDaysStockDesired('');
      setDaysStockError('');
      setIsIdDisabled(false);
      setDateError('');
      setStatusId('');
      setStatusName('');
      document.getElementById('id').value = '';
      document.getElementById('store').value = '';
      document.getElementById('supplier').value = '';
      onOrderDataReceived([], null, '');
    }
  }, [orderId]);

  const formatNumber = (number) => {
    return number?.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return dateStr;
    const [day, month, year] = dateStr.split('/');
    return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
  };
  const [currentDate, setCurrentDate] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [userName, setUserName] = useState('');
  const [sections, setSections] = useState([]);
  const [selectedSection, setSelectedSection] = useState('');
  const [subsections, setSubsections] = useState([]);
  const [selectedSubsection, setSelectedSubsection] = useState('');
  const [stores, setStores] = useState([]);
  const [storeName, setStoreName] = useState('');
  const [supplierName, setSupplierName] = useState('');
  const [ocNumbersPending, setOcNumbersPending] = useState([]);
  const [toast, setToast] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [showSupplierModal, setShowSupplierModal] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [dateError, setDateError] = useState('');
  // const [daysStockDesired, setDaysStockDesired] = useState('');
  const [daysStockError, setDaysStockError] = useState('');
  const [isIdDisabled, setIsIdDisabled] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [orderData, setOrderData] = useState([]);
  const [tableData, setTableData] = useState([]);
  const [statusId, setStatusId] = useState(null);
  const [statusName, setStatusName] = useState('');
  const [isFormDisabled, setIsFormDisabled] = useState(false);
  const [showLogModal, setShowLogModal] = useState(false);

  const resetDates = () => {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1);
    const endDateValue = new Date(tomorrow);
    endDateValue.setDate(tomorrow.getDate() + 30);
  
    const formattedDate = today.toISOString().split('T')[0];
    const formattedTomorrow = tomorrow.toISOString().split('T')[0];
    const formattedEndDate = endDateValue.toISOString().split('T')[0];
  
    setCurrentDate(formattedDate);
    setStartDate(formattedTomorrow);
    setEndDate(formattedEndDate);
  };
  

  useEffect(() => {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1);
    const endDateValue = new Date(tomorrow);
    endDateValue.setDate(tomorrow.getDate() + 30);
    
    const formattedDate = today.toISOString().split('T')[0];
    const formattedTomorrow = tomorrow.toISOString().split('T')[0];
    const formattedEndDate = endDateValue.toISOString().split('T')[0];
    
    setCurrentDate(formattedDate);
    setStartDate(formattedTomorrow);
    setEndDate(formattedEndDate);

    const firstName = getFirstName();
    const lastName = getLastName();
    setUserName(`${firstName} ${lastName}`.trim());

    const fetchData = async () => {
      try {
        const response = await http.get('/order-default/');
        setSections(response.data.sections);
        setStores(response.data.stores);
      } catch (error) {
        console.error('Erro ao carregar dados:', error);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'F9' && document.activeElement.id === 'supplier') {
        e.preventDefault();
        setShowSupplierModal(true);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  useEffect(() => {
    if (selectedSection) {
      const sectionData = sections.find(section => section.id.toString() === selectedSection);
      setSubsections(sectionData?.subsections || []);
    } else {
      setSubsections([]);
    }
    
    // Só limpa a subseção se não houver um orderId
    if (!selectedSubsection) {
      setSelectedSubsection('');
    } 
  }, [selectedSection, sections, orderId, selectedSubsection]);

  return (
    <>
      <CCard className="mb-1">
        <CCardHeader className="py-2 d-flex justify-content-between align-items-center">
          <strong>Ordem de Compra{statusName ? ` - ${statusName}` : ''}</strong>
          <CButtonGroup size="sm" className="d-flex align-items-center">
            <CButton 
              color="info"
              onClick={() => {
                const orderId = document.getElementById('id').value;
                if (!orderId) {
                  setToast({
                    visible: true,
                    color: 'warning',
                    message: 'Por favor, informe o número da OC para visualizar os logs'
                  });
                  return;
                }
                setShowLogModal(true);
              }}
            >
              <CIcon icon={cilList} className="me-1" /> Ver Log
            </CButton>
            <CButton color="secondary" onClick={() => {
              resetDates();
              setStoreName('');
              setSupplierName('');
              setOcNumbersPending([]);
              setSelectedSection('');
              setSelectedSubsection('');
              // setDaysStockDesired('');
              setDaysStockError('');
              setIsIdDisabled(false);
              setDateError('');
              setStatusId('');
              setStatusName('');            
              document.getElementById('id').value = '';
              document.getElementById('store').value = '';
              document.getElementById('supplier').value = '';
              onOrderDataReceived([], null, '');
            }}><CIcon icon={cilX} className="me-1" /> Cancelar</CButton>
            {statusId === 3 && (
              <CButton
                color="success"
                onClick={async () => {
                  try {
                    const orderId = document.getElementById('id').value;
                    if (!orderId) return;
                    const response = await http.get(`/orders/${orderId}/export-excel/`, { responseType: 'blob' });
                    const url = window.URL.createObjectURL(new Blob([response.data]));
                    const link = document.createElement('a');
                    link.href = url;
                    link.setAttribute('download', `ordem_compra_${orderId}.xlsx`);
                    document.body.appendChild(link);
                    link.click();
                    link.parentNode.removeChild(link);
                  } catch (error) {
                    setToast({
                      visible: true,
                      color: 'danger',
                      message: 'Erro ao baixar o arquivo Excel'
                    });
                  }
                }}
              >
                <CIcon icon={cilCloudDownload} className="me-1 handleOrderDataReceived" /> Excel
              </CButton>
            )}
            <CButton 
              color="primary"
              disabled={isSubmitting || statusId === 3}
              onClick={async () => {
                setIsSubmitting(true);
                try {
                  const orderId = document.getElementById('id').value;
                  const storeValue = document.getElementById('store').value;
                  const supplierValue = document.getElementById('supplier').value;
                  if (!tableData || tableData.length === 0) {
                    setToast({
                      visible: true,
                      color: 'danger',
                      message: 'Erro: Não há dados para salvar'
                    });
                    return;
                  }
                  // if (!orderData || orderData.length === 0) {
                  //   setToast({
                  //     visible: true,
                  //     color: 'danger',
                  //     message: 'Erro: Não há dados para salvar'
                  //   });
                  //   return;
                  // }
                  const payload = {
                    supplier: parseInt(supplierValue),
                    store: parseInt(storeValue),
                    section: parseInt(selectedSection),
                    subsection: parseInt(selectedSubsection) || null,
                    sales_date_start: startDate,
                    sales_date_end: endDate,
                    // days_stock_desired: parseInt(daysStockDesired),
                    total_amount: totalAmount.toString(),
                    observation: "",
                    oc_numbers_pending: ocNumbersPending,
                    items_data: tableData.map(row => ({
                      item: row.item_code,
                      days_stock_desired: parseInt(row.days_stock),
                      date_last_purchase: formatDate(row.date_last_purchase),
                      quantity_last_purchase: parseInt(row.quantity_last_purchase),
                      sale_prediction: parseFloat(row.sale_prediction),
                      quantity_suggested: parseInt(row.quantity_suggested),
                      quantity_order: parseInt(row.cantCompra || 0),
                      bonus: parseFloat(row.bonificaciones || 0),
                      discount: parseFloat(row.descuento || 0),
                      price: row.purchase_price?.toString() || "0",
                      stock_available: row.stock_available?.toString() || "0",
                      days_stock_available: parseInt(row.current_stock_days || 0),
                      total_amount: (parseInt(row.cantCompra || 0) * parseFloat(row.purchase_price || 0)).toString()
                    }))                    
                  };
                  

                  
                  const response = orderId
                    ? await http.put(`/orders/${orderId}/`, payload)
                    : await http.post('/orders/', payload);

                  if (!orderId && response.data.order_id) {
                    document.getElementById('id').value = response.data.order_id;
                  }

                  setStatusId(response.data.status_id);
                  setStatusName(response.data.status_name);
                  setToast({
                    visible: true,
                    color: 'success',
                    message: `Ordem de compra ${orderId ? 'atualizada' : 'criada'} com sucesso!`
                  });
                } catch (error) {
                  console.error('Erro ao salvar ordem de compra:', error);
                  setToast({
                    visible: true,
                    color: 'danger',
                    message: 'Erro ao salvar ordem de compra'
                  });
                } finally {
                  setIsSubmitting(false);
                }
              }}
            >
              <CIcon icon={cilSave} className="me-1" /> {isSubmitting ? <CSpinner size="sm" /> : 'Salvar'}</CButton>
            </CButtonGroup>
          </CCardHeader>
          <CCardBody className="py-2">
            <CRow className="mb-1 g-2">
              <CFormLabel htmlFor="code" className="col-sm-1 col-form-label col-form-label-sm text-body">
                OC Nro.
              </CFormLabel>
            <CCol sm={2}>
              <CInputGroup size="sm">
                <CFormInput
                  type="text"
                  id="id"
                  disabled={isIdDisabled || isSubmitting || statusId === 3}
                />
                <CButton
                  id="search-button"
                  color="primary"
                  variant="outline"
                  onClick={async () => {
                    const orderId = document.getElementById('id').value;
                    if (!orderId) {
                      setToast({
                        visible: true,
                        color: 'warning',
                        message: 'Por favor, informe o número da OC'
                      });
                      return;
                    }
                    
                    try {
                      const response = await http.get(`/orders/${orderId}/`);
                      const order = response.data;
                      console.log(order)
                      
                      // Preenche os campos do formulário
                      document.getElementById('store').value = order.store;
                      document.getElementById('supplier').value = order.supplier;
                      setStoreName(order.store_name || '');
                      setSupplierName(order.supplier_name || '');
                      setSelectedSection(order.section.toString());
                      setSelectedSubsection(order.subsection?.toString() || '');
                      console.log('selectedSubsection', order.subsection?.toString() || '')
                      setStartDate(order.sales_date_start);
                      setEndDate(order.sales_date_end);
                      // setDaysStockDesired(order.days_stock_desired.toString());
                      setOcNumbersPending(order.oc_numbers_pending);
                      onOrderDataReceived([], order.store, order.total_amount ? parseFloat(order.total_amount) : 0, order.status_id ? order.status_id.toString() : '');
                      setStatusId(order.status_id);
                      setStatusName(order.status_name);                    
                      // Mapeia os itens para o formato esperado pelo OrderDetail
                      const mappedItems = order.items.map(item => ({
                        item_code: item.item,
                        item_name: item.item_name,
                        days_stock: item.days_stock_desired,
                        pack_size: item.item_pack_size,
                        date_last_purchase: item.date_last_purchase,
                        quantity_last_purchase: item.quantity_last_purchase,
                        sale_prediction: item.sale_prediction,
                        quantity_suggested: item.quantity_suggested,
                        cantCompra: item.quantity_order,
                        bonificaciones: item.bonus,
                        descuento: item.discount,
                        purchase_price: parseFloat(item.price),
                        stock_available: parseInt(item.stock_available),
                        current_stock_days: item.days_stock_available
                      }));
                      
                      // Atualiza os dados da tabela e o valor total
                      setTableData(mappedItems);
                      onOrderDataReceived(mappedItems, order.store, order.total_amount ? parseFloat(order.total_amount) : 0, order.status_id ? order.status_id.toString() : '');
                      setIsIdDisabled(true);
                      
                    } catch (error) {
                      console.error('Erro ao buscar ordem de compra:', error);
                      setToast({
                        visible: true,
                        color: 'danger',
                        message: 'Erro ao buscar ordem de compra'
                      });
                    }
                  }}
                >
                <CIcon icon={cilSearch} />
              </CButton>
            </CInputGroup>
          </CCol>
          <CFormLabel htmlFor="date" className="col-sm-1 col-form-label col-form-label-sm text-body">
            Data
          </CFormLabel>
          <CCol sm={2}>
            <CFormInput
              type="date"
              className="form-control form-control-sm"
              id="date"
              value={currentDate}
              disabled
            />
          </CCol>
          <CFormLabel htmlFor="user" className="col-sm-1 col-form-label col-form-label-sm text-body"  style={{ paddingRight: 0 }}>
            Comprador
          </CFormLabel>
          <CCol sm={2}>
            <CFormInput
              type="text"
              className="form-control form-control-sm"
              id="user"
              value={userName}
              disabled
            />
          </CCol>
          <CFormLabel htmlFor="oc_numbers_pending" className="col-sm-1 col-form-label col-form-label-sm text-body">
            OC Pend.
          </CFormLabel>
          <CCol sm={2}>
            <div className="d-flex flex-wrap gap-1">
            {ocNumbersPending.map((ocNumber) => (
              <a
                key={ocNumber}
                href="#"
                onClick={async (e) => {
                  e.preventDefault();
                  try {
                    const response = await http.get(`/order-system/${ocNumber}/`);
                    setSelectedOrder(response.data);
                    setShowModal(true);
                  } catch (error) {
                    console.error('Erro ao buscar detalhes da OC:', error);
                  }
                }}
                className="text-decoration-none"
              >
                <small className="text-primary">{ocNumber}</small>
                {ocNumber !== ocNumbersPending[ocNumbersPending.length - 1] && ", "}
              </a>
            ))}
          </div>
          </CCol>          
        </CRow>    
        <CRow className="mb-1 g-2">
          <CFormLabel htmlFor="name" className="col-sm-1 col-form-label col-form-label-sm text-body">
            Sucursal
          </CFormLabel>
          <CCol sm={1}>
            <CFormInput
              type="text"
              className="form-control form-control-sm"
              id="store"
              disabled={isSubmitting || statusId === 3}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  const store = stores.find(s => s.code.toString() === e.target.value);
                  if (store) {
                    setStoreName(store.name);
                  } else {
                    setStoreName('');
                  }
                  document.getElementById('supplier').focus();
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

          <CFormLabel htmlFor="supplier" className="col-sm-1 col-form-label col-form-label-sm text-body" style={{ paddingRight: 0 }}>
            Proveedor
          </CFormLabel>
          <CCol sm={1}>
            <CFormInput
              type="text"
              className="form-control form-control-sm"
              id="supplier"
              disabled={isSubmitting || statusId === 3}
              onKeyDown={async (e) => {
                if (e.key === 'Enter' || e.key === 'Tab') {
                  e.preventDefault();
                  const storeValue = document.getElementById('store').value;
                  const supplierValue = e.target.value;

                  try {
                    const response = await http.post('/supplier-info/', {
                      store_code: storeValue,
                      supplier_code: supplierValue
                    });

                    setSupplierName(response.data.supplier_name);
                    setOcNumbersPending(response.data.oc_numbers_pending);
                    document.getElementById('section').focus();
                  } catch (error) {
                    console.error('Erro ao buscar informações do fornecedor:', error);
                    setSupplierName('');
                    setOcNumbersPending([]);
                    setToast({
                      visible: true,
                      color: 'danger',
                      message: 'Fornecedor não encontrado'
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
              id="supplier_name"
              value={supplierName}
              disabled
            />
          </CCol>        
        </CRow>
        <CRow className="mb-1 g-2">
          <CFormLabel htmlFor="section" className="col-sm-1 col-form-label col-form-label-sm text-body">
            Seção
          </CFormLabel>
          <CCol sm={5}>
            <CFormSelect
              id="section"
              className="form-select form-select-sm"
              value={selectedSection}
              disabled={isSubmitting || statusId === 3}
              onChange={(e) => setSelectedSection(e.target.value)}
            >
              <option value="">Selecione a seção</option>
              {sections.map(section => (
                <option key={section.id} value={section.id}>{section.name}</option>
              ))}
            </CFormSelect>
          </CCol>
          

          <CFormLabel htmlFor="subsection" className="col-sm-1 col-form-label col-form-label-sm text-body">
            Subseção
          </CFormLabel>
          <CCol sm={5}>
            <CFormSelect
              id="subsection"
              className="form-select form-select-sm"
              value={selectedSubsection}
              disabled={isSubmitting || statusId === 3}
              onChange={(e) => setSelectedSubsection(e.target.value)}
            >
              <option value="">Selecione a subseção</option>
              {subsections.map(subsection => (
                <option key={subsection.id} value={subsection.id}>{subsection.name}</option>
              ))}
            </CFormSelect>
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
              id="start_date_prediction"
              value={startDate}
              disabled={isSubmitting || statusId === 3}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </CCol>
          <CFormLabel htmlFor="end_date_prediction" className="col-sm-2 col-form-label col-form-label-sm text-body">
            Data Final Prevista
          </CFormLabel>
          <CCol sm={2}>
            <CFormInput
              type="date"
              className="form-control form-control-sm"
              id="end_date_prediction"
              value={endDate}
              disabled={isSubmitting || statusId === 3}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </CCol>
          {/* <CFormLabel htmlFor="days_stock_desired" className="col-sm-1 col-form-label col-form-label-sm text-body">
            Dias Estoque
          </CFormLabel>
          <CCol sm={1}>
            <CFormInput
              type="number"
              className="form-control form-control-sm"
              id="days_stock_desired"
              value={daysStockDesired}
              disabled={isSubmitting || statusId === 3}
              min="1"
              onChange={(e) => {
                const value = e.target.value;
                setDaysStockDesired(value);
                if (!value || value < 1) {
                  setDaysStockError('O valor deve ser maior que 0');
                } else {
                  setDaysStockError('');
                }
              }}
            />
            {daysStockError && (
              <div className="text-danger small mt-1">{daysStockError}</div>
            )}
          </CCol>  */}
          <CFormLabel htmlFor="total_amount" className="col-sm-1 col-form-label col-form-label-sm text-body">
            Valor Total
          </CFormLabel>
          <CCol sm={2}>
            <CFormInput
              type="text"
              className="form-control form-control-sm text-end"
              id="total_amount" 
              value={formatNumber(totalAmount)}
              disabled
              />
          </CCol>             
          <CCol sm={2}>
            <CButton
              color="primary"
              size="sm"
              className="w-100"
              disabled={isLoading || !selectedSection || !startDate || !endDate || dateError || daysStockError}
              onClick={async () => {
                setIsLoading(true);
                try {
                  const storeValue = document.getElementById('store').value;
                  const supplierValue = document.getElementById('supplier').value;
                  const response = await http.get(`/order-default-detail/?section=${selectedSection}&store=${storeValue}&supplier=${supplierValue}&start_date_prediction=${startDate}&end_date_prediction=${endDate}${selectedSubsection ? `&subsection=${selectedSubsection}` : ''}`);
                  setOrderData(response.data);
                  setTableData(response.data.results);
                  onOrderDataReceived(response.data, parseInt(storeValue));
                  setIsIdDisabled(true);
                } catch (error) {
                  console.error('Erro ao processar pedido:', error);
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

    <OrderModal
      visible={showModal}
      onClose={() => setShowModal(false)}
      order={selectedOrder}
    />
      {toast && (
        <CToaster placement="top-end">
          <CToast
            visible={toast.visible}
            color={toast.color}
            className="text-white align-items-center"
            onClose={() => setToast(null)}
            delay={3000}
            autohide
          >
            <CToastBody>{toast.message}</CToastBody>
          </CToast>
        </CToaster>
      )}
      <SupplierModal
        visible={showSupplierModal}
        onClose={() => setShowSupplierModal(false)}
        onSelect={(supplierCode) => {
          document.getElementById('supplier').value = supplierCode;
          const event = new KeyboardEvent('keydown', {
            key: 'Enter',
            code: 'Enter',
            keyCode: 13,
            which: 13,
            bubbles: true
          });
          document.getElementById('supplier').dispatchEvent(event);
        }}
      />

      <OrderLogModal 
        visible={showLogModal}
        onClose={() => setShowLogModal(false)}
        orderId={document.getElementById('id')?.value || ''}
      />      
    </>
  )
}

OrderForm.propTypes = {
  onOrderDataReceived: PropTypes.func.isRequired,
  totalAmount: PropTypes.number.isRequired
};





export default OrderForm;


