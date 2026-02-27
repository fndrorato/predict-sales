import React, { useMemo, useEffect, useState } from 'react';
import PropTypes from 'prop-types';
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
import { useTranslation } from 'react-i18next';
import { useColorModes } from '@coreui/react';

// Register AG Grid modules
ModuleRegistry.registerModules([AllEnterpriseModule, AllCommunityModule])

const ItemStockGrid = ({ stockData, onDataChange }) => {
  const { t } = useTranslation();
  const { colorMode } = useColorModes('coreui-free-react-admin-template-theme');
  
  const currentTheme = useMemo(() => {
    const themeLightWarm = themeQuartz.withPart(colorSchemeLightWarm);
    const themeDarkBlue = themeQuartz.withPart(colorSchemeDarkBlue);
    return colorMode === 'dark' ? themeDarkBlue : themeLightWarm;
  }, [colorMode]);

  const agGridThemeClass = useMemo(() => (
    colorMode === 'dark' ? 'ag-theme-quartz-dark' : 'ag-theme-quartz'
  ), [colorMode]);

  const parsedStockData = useMemo(() => (
    stockData.map(stock => ({
      ...stock,
      stock_min: parseFloat(stock.stock_min),
      stock_max: parseFloat(stock.stock_max),
      stock_available: parseFloat(stock.stock_available),
    }))
  ), [stockData]);
 
  const onCellValueChanged = (params) => {
    if (params.newValue < 0) {
      params.node.setDataValue(params.column.colId, params.oldValue);
      return;
    }
    const updatedData = [];
    params.api.forEachNode(node => {
      updatedData.push(node.data);
    });
    onDataChange(updatedData);
  };

  const columnDefs = useMemo(() => [
    { field: 'store', headerName: t('items.store'), sortable: false, filter: false },
    { 
      field: 'days_stock', 
      headerName: t('items.daysStock'), 
      sortable: false, 
      filter: false, 
      cellStyle: () => getColumnStyle('days_stock'),
      editable: true,
      type: 'numericColumn',
      valueParser: (params) => Number(params.newValue)
    },
    {
      field: 'stock_min',
      headerName: t('items.stockMin'),
      sortable: false,
      filter: false,
      valueFormatter: (params) => (typeof params.value === 'number' ? params.value.toFixed(2) : '0.00'),
      cellStyle: () => getColumnStyle('stock_min'),
      editable: true,
      type: 'numericColumn',
      valueParser: (params) => Number(params.newValue)
    },
    {
      field: 'stock_max',
      headerName: t('items.stockMax'),
      sortable: false,
      filter: false,
      valueFormatter: (params) => (typeof params.value === 'number' ? params.value.toFixed(2) : '0.00')
    },
    {
      field: 'stock_available',
      headerName: t('items.stockAvailable'),
      sortable: false,
      filter: false,
      valueFormatter: (params) => (typeof params.value === 'number' ? params.value.toFixed(2) : '0.00')
    },
    {
      field: 'stock_available_on',
      headerName: t('items.stockAvailableOn'),
      sortable: false,
      filter: false,
      valueFormatter: (params) => {
        const date = new Date(params.value);
        return date.toLocaleDateString();
      }
    }
  ], [t]);

  const defaultColDef = useMemo(() => ({
    flex: 1,
    resizable: true,
    minWidth: 100,
    suppressMenu: true,
    suppressHeaderMenuButton: true,
    menuTabs: []
  }), []);

  const getColumnStyle = (field) => {
    if (field === 'stock_min' || field === 'days_stock') {
      return { backgroundColor: '#e6f3ff', color: '#1d222b' };
    }
    return null;
  };

  return (
    <div key={agGridThemeClass} className={agGridThemeClass} style={{ height: '400px', width: '100%' }}>
      <AgGridReact
        rowData={parsedStockData}
        columnDefs={columnDefs}
        defaultColDef={defaultColDef}
        animateRows={true}
        enableRangeSelection={true}
        pagination={false}
        paginationAutoPageSize={true}
        theme={currentTheme}
        rowHeight={30}
        onCellValueChanged={onCellValueChanged}
      />
    </div>
  );
};

ItemStockGrid.propTypes = {
  stockData: PropTypes.arrayOf(
    PropTypes.shape({
      store: PropTypes.number.isRequired,
      days_stock: PropTypes.number.isRequired,
      stock_min: PropTypes.number.isRequired,
      stock_max: PropTypes.number.isRequired,
      stock_available: PropTypes.number.isRequired,
      stock_available_on: PropTypes.string.isRequired
    })
  ).isRequired,
  onDataChange: PropTypes.func.isRequired
};

export default ItemStockGrid;