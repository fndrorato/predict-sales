import React, { useState, useEffect } from 'react';
import {
  CContainer,
  CRow,
  CCol,
  CFormInput,
  CFormLabel,
  CFormSelect,
  CFormCheck,
  CButton,
  CTable,
  CTableHead,
  CTableRow,
  CTableHeaderCell,
  CTableBody,
  CTableDataCell,
  CCard,
  CCardHeader,
  CCardBody,
  CToast,
  CToastBody,
  CToaster
} from '@coreui/react';
import CIcon from '@coreui/icons-react';
import http from 'src/services/http';
import SupplierModal from 'src/components/SupplierModal';
import { cilCloudDownload } from '@coreui/icons'

const PendingApproval = () => {
    const [stores, setStores] = useState([]);
    const [storeName, setStoreName] = useState('');
    const [supplier, setSupplier] = useState('');
    const [supplierName, setSupplierName] = useState('');
    const [buyer, setBuyer] = useState('');
    const [section, setSection] = useState('');
    const [pendingOnly, setPendingOnly] = useState(true);
    const [orders, setOrders] = useState([]);
    const [showSupplierModal, setShowSupplierModal] = useState(false);
    const [buyers, setBuyers] = useState([]);
    const [sections, setSections] = useState([]);
    const [toast, setToast] = useState(null);
    const [store, setStore] = useState('');
    const [selectedOrderIds, setSelectedOrderIds] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [buyersResponse, sectionsResponse, storesResponse] = await Promise.all([
          http.get('/users/'),
          http.get('/items/sections/'),
          http.get('/stores/')
        ]);
        console.log(buyersResponse.data);
        setBuyers(buyersResponse.data.results); 
        setSections(sectionsResponse.data.results);
        setStores(storesResponse.data.results);
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



  const handleSupplierSelect = (supplierData) => {
    setSupplier(supplierData.code);
    setSupplierName(supplierData.name);
    setShowSupplierModal(false);
  };

  const formatNumber = (number) => {
    return number?.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const [year, month, day] = dateStr.split('-');
    return `${day}/${month}/${year}`;
  };

  const handleSearch = async () => {
    try {
      const params = {
        store,
        supplier,
        buyer,
        section,
        pending_only: pendingOnly
      };
      console.log(params)
      const response = await http.get('/orders/list-pending', { params });
      setOrders(response.data.results);
    } catch (error) {
      console.error('Erro ao buscar ordens:', error);
    }
  };

    return (
        <CContainer fluid>
            {toast && (
                <CToaster placement="top-end">
                    <CToast
                        visible={toast.visible}
                        color={toast.color}
                        className="text-white align-items-center"
                    >
                        <CToastBody>{toast.message}</CToastBody>
                    </CToast>
                </CToaster>
            )}
            <CCard className="mb-3">
                <CCardHeader>
                    <strong>Filtros de Pesquisa</strong>
                </CCardHeader>
                <CCardBody>
                    <CRow className="mb-1 g-2">
                        <CFormLabel htmlFor="store" className="col-sm-1 col-form-label col-form-label-sm text-body">
                            Sucursal
                        </CFormLabel>
                        <CCol sm={1}>
                            <CFormInput
                                type="text"
                                className="form-control form-control-sm"
                                id="store"
                                value={store}
                                onChange={(e) => setStore(e.target.value)}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter' || e.key === 'Tab') {
                                    const storeObj = stores.find(s => s.code.toString() === e.target.value);
                                    if (storeObj) {
                                        setStoreName(storeObj.name);
                                        setStore(e.target.value);
                                    } else {
                                        setStoreName('');
                                        setStore('');
                                    }
                                    document.getElementById('supplier').focus();
                                    }
                                }}
                            />  
                        </CCol>
                        <CCol sm={4}>
                            <CFormInput
                                value={storeName}
                                disabled
                            />
                        </CCol>
                        <CFormLabel htmlFor="name" className="col-sm-1 col-form-label col-form-label-sm text-body">
                            Proveedor
                        </CFormLabel>
                        <CCol sm={1}>
                            <CFormInput
                                type="text"
                                className="form-control form-control-sm"
                                id="supplier"
                                onKeyDown={async (e) => {
                                    if (e.key === 'Enter' || e.key === 'Tab') {
                                    e.preventDefault();
                                    const supplierValue = e.target.value;

                                    try {
                                        const response = await http.get(`/suppliers/?code=${supplierValue}`)

                                        if (response.data && response.data.length > 0) {
                                            setSupplier(response.data[0].code);
                                            setSupplierName(response.data[0].name);
                                        }
                                        document.getElementById('section').focus();
                                    } catch (error) {
                                        console.error('Erro ao buscar informações do fornecedor:', error);
                                        setSupplierName('');
                                        setSupplier('');
                                        document.getElementById('buyer').focus();
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
                        <CFormLabel htmlFor="buyer" className="col-sm-1 col-form-label col-form-label-sm text-body">
                            Comprador
                        </CFormLabel>
                        <CCol sm={3}>
                            <CFormSelect
                                id="buyer"
                                value={buyer}
                                onChange={(e) => setBuyer(e.target.value)}
                            >
                                <option value="">Selecione...</option>
                                {buyers.map(b => (
                                <option key={b.id} value={b.id}>{b.first_name} {b.last_name}</option>
                                ))}
                            </CFormSelect>
                        </CCol>
                        {/* <CFormLabel htmlFor="section" className="col-sm-1 col-form-label col-form-label-sm text-body">
                            Seção
                        </CFormLabel>
                        <CCol sm={3}>
                            <CFormSelect
                                id="section"
                                value={section}
                                onChange={(e) => setSection(e.target.value)}
                            >
                                <option value="">Selecione...</option>
                                {sections.map(s => (
                                <option key={s.id} value={s.id}>{s.name}</option>
                                ))}
                            </CFormSelect>
                        </CCol> */}
                        <CCol sm={2} className="d-flex align-items-end text-body">
                            <CFormCheck
                                id="pendingOnly"
                                label="Apenas Pendentes"
                                checked={pendingOnly}
                                onChange={(e) => setPendingOnly(e.target.checked)}
                            />
                        </CCol>
                        <CCol sm={1}>
                            <CButton color="primary" onClick={handleSearch}>
                                Buscar
                            </CButton>
                        </CCol>
                        <CCol sm={3} className="d-flex align-items-end">
                            <CButton color="secondary" variant="outline" disabled={selectedOrderIds.length === 0} onClick={async () => {
                                try {
                                    await http.put('/orders/update-status/', { ids: selectedOrderIds });
                                    setToast({ visible: true, color: 'success', message: 'Ordens aprovadas com sucesso!' });
                                    setSelectedOrderIds([]);
                                    handleSearch();
                                } catch (error) {
                                    setToast({ visible: true, color: 'danger', message: 'Erro ao aprovar ordens.' });
                                }
                            }}>
                                Aprovar Ordens Selecionadas
                            </CButton>
                        </CCol>                        
                    </CRow>
                </CCardBody>
            </CCard>

            <CTable small striped className="mt-2 table-sm ">
                <CTableHead>
                <CTableRow>
                    <CTableHeaderCell></CTableHeaderCell>
                    <CTableHeaderCell>ID</CTableHeaderCell>
                    <CTableHeaderCell>Status</CTableHeaderCell>
                    <CTableHeaderCell>Sucursal</CTableHeaderCell>
                    <CTableHeaderCell>Fornecedor</CTableHeaderCell>
                    <CTableHeaderCell>Comprador</CTableHeaderCell>
                    <CTableHeaderCell>Data</CTableHeaderCell>
                    <CTableHeaderCell className="text-end">Valor Total</CTableHeaderCell>
                    <CTableHeaderCell></CTableHeaderCell>
                </CTableRow>
                </CTableHead>
                <CTableBody>
                {orders.map((order) => (
                    <CTableRow key={order.id}>
                      <CTableDataCell>
                        <CFormCheck
                          checked={selectedOrderIds.includes(order.id)}
                          onChange={e => {
                            if (e.target.checked) {
                              setSelectedOrderIds([...selectedOrderIds, order.id]);
                            } else {
                              setSelectedOrderIds(selectedOrderIds.filter(id => id !== order.id));
                            }
                          }}
                        />
                      </CTableDataCell>
                    <CTableDataCell>{order.id}</CTableDataCell>
                    <CTableDataCell>{order.status_name}</CTableDataCell>
                    <CTableDataCell>{order.store_name}</CTableDataCell>
                    <CTableDataCell>{order.supplier_name}</CTableDataCell>
                    <CTableDataCell>{order.buyer_name}</CTableDataCell>
                    <CTableDataCell>{formatDate(order.date)}</CTableDataCell>
                    <CTableDataCell className="text-end">{formatNumber(order.total_amount)}</CTableDataCell>
                    <CTableDataCell>
                        <CButton
                        color="primary"
                        size="sm"
                        onClick={() => window.open(`/#/orders?id=${order.id}`, '_blank')}
                        >
                        Abrir OC
                        </CButton>
                        {order.status === 3 && (
                        <CButton
                          color="success"
                          size="sm"
                          className="ms-2 text-white"
                          title="Exportar Excel"
                          onClick={async () => {
                            try {
                              const response = await http.get(`/orders/${order.id}/export-excel/`, { responseType: 'blob' });
                              const url = window.URL.createObjectURL(new Blob([response.data]));
                              const link = document.createElement('a');
                              link.href = url;
                              link.setAttribute('download', `OC_${order.id}.xlsx`);
                              document.body.appendChild(link);
                              link.click();
                              link.parentNode.removeChild(link);
                            } catch (error) {
                              setToast({ visible: true, color: 'danger', message: 'Erro ao exportar Excel.' });
                            }
                          }}
                        >
                          <CIcon icon={cilCloudDownload} style={{ fontSize: '1.2rem' }} title="Download file" />
                        </CButton>
                        )}
                    </CTableDataCell>
                    </CTableRow>
                ))}
                </CTableBody>
            </CTable>

            <SupplierModal
                visible={showSupplierModal}
                onClose={() => setShowSupplierModal(false)}
                onSelect={handleSupplierSelect}
            />
        </CContainer>
    );
};

export default PendingApproval;