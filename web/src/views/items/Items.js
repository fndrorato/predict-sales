import React, { useState, useEffect, useCallback } from 'react';
import { CContainer } from '@coreui/react';
import http from '../../services/http';
import ItemForm from './ItemForm';
import ItemStockGrid from './ItemStockGrid';
import ItemNavigation from './ItemNavigation';
import { API_URL } from '../../config';

const Items = () => {
  const [item, setItem] = useState(null);
  const [nextUrl, setNextUrl] = useState(null);
  const [prevUrl, setPrevUrl] = useState(null);
  const [firstUrl, setFirstUrl] = useState(null);
  const [lastUrl, setLastUrl] = useState(null);
  const [hasChanges, setHasChanges] = useState(false);
  const [stockData, setStockData] = useState([]);
  const [isSearchMode, setIsSearchMode] = useState(false);

  // 👇 fetchItem com cursor opcional ou código
  const fetchItem = useCallback(async (cursor = null, code = null) => {
    try {
      let url;
      if (code) {
        url = `/items/?code=${code}`;
      } else {
        url = cursor ? `/items/?cursor=${cursor}` : `/items/`;
      }
      const response = await http.get(url);
      setItem(response.data.results?.[0] ?? response.data);
      setNextUrl(response.data.next);
      setPrevUrl(response.data.previous);
      setFirstUrl(response.data.first);
      setLastUrl(response.data.last);
    } catch (error) {
      console.error('Erro ao buscar item:', error);
    }
  }, []);

  useEffect(() => {
    fetchItem();
  }, [fetchItem]);

  useEffect(() => {
    if (item?.item_control_stock) {
      setStockData(item.item_control_stock);
    }
  }, [item]);

  // 👇 teclado ainda funciona sem alterar URL
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'ArrowRight' && nextUrl) {
        const cursor = new URL(nextUrl).searchParams.get('cursor');
        fetchItem(cursor);
      } else if (event.key === 'ArrowLeft' && prevUrl) {
        const cursor = new URL(prevUrl).searchParams.get('cursor');
        fetchItem(cursor);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [nextUrl, prevUrl, fetchItem]);

  // 👇 clique nos botões: busca o item, sem alterar a URL
  const handleNavigate = (url) => {
    if (url) {
      const cursor = new URL(url).searchParams.get('cursor');
      fetchItem(cursor);
    }
  };

  const handleSearch = (code) => {
    setIsSearchMode(true);
    fetchItem(null, code);
  };

  const handleReset = () => {
    setIsSearchMode(false);
    fetchItem();
  };

  const handleStockDataChange = (newData) => {
    setStockData(newData);
    setHasChanges(true);
  };

  const handleSave = async () => {
    try {
      const payload = stockData.map(row => ({
        store: row.store,
        days_stock: row.days_stock,
        stock_min: row.stock_min
      }));

      await http.put(`/items/control-stock/${item.code}/`, payload);
      setHasChanges(false);
    } catch (error) {
      console.error('Erro ao salvar alterações:', error);
    }
  };

  if (!item) {
    return <div>Carregando...</div>;
  }

  return (
    <CContainer fluid>
      <ItemNavigation
        onNavigate={handleNavigate}
        nextUrl={!isSearchMode ? nextUrl : null}
        prevUrl={!isSearchMode ? prevUrl : null}
        firstUrl={!isSearchMode ? firstUrl : null}
        lastUrl={!isSearchMode ? lastUrl : null}
        onSave={handleSave}
        canSave={hasChanges}
        onSearch={handleSearch}
        onReset={handleReset}
      />
      <ItemForm item={item} />
      <ItemStockGrid stockData={stockData} onDataChange={handleStockDataChange} />
    </CContainer>
  );
};

export default Items;
