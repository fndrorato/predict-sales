import React, { useState, useEffect } from 'react';
import { CContainer } from '@coreui/react';
import OrderForm from './OrderForm';
import OrderDetail from './OrderDetail';

const Orders = () => {
  const [orderData, setOrderData] = useState([]);
  const [selectedStore, setSelectedStore] = useState(null);
  const [totalAmount, setTotalAmount] = useState(0);
  const [statusId, setStatusId] = useState(null);

  const handleOrderDataReceived = (data, store, totalAmount, statusIdValue) => {
    const results = Array.isArray(data) ? data : data?.results || [];
    setOrderData(results);    
    setSelectedStore(store);
    setStatusId(statusIdValue);
    // setTotalAmount(totalAmount);

    if (Array.isArray(data) && data.length === 0) {
      setTotalAmount(0);
    } 
  };

  return (
    <CContainer fluid>
      <OrderForm onOrderDataReceived={handleOrderDataReceived} totalAmount={totalAmount} />
      <OrderDetail orderData={orderData} store={selectedStore} setTotalAmount={setTotalAmount} statusId={statusId} />
    </CContainer>
  );
};

export default Orders;
