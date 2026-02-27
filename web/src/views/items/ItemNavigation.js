import React, { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { CButtonGroup, CButton, CModal, CModalHeader, CModalTitle, CModalBody, CModalFooter, CFormInput } from '@coreui/react';
import CIcon from '@coreui/icons-react';
import { cilChevronLeft, cilChevronRight, cilChevronDoubleLeft, cilChevronDoubleRight, cilSave, cilSearch, cilX } from '@coreui/icons';

const ItemNavigation = ({ onNavigate, nextUrl, prevUrl, firstUrl, lastUrl, onSave, canSave, onSearch, onReset }) => {
  const [visible, setVisible] = useState(false);
  const [code, setCode] = useState('');
  const inputRef = useRef(null);

  const handleSearch = () => {
    if (code.trim()) {
      onSearch(code);
      setVisible(false);
      setCode('');
    }
  };

  const isDark = document.body.classList.contains('dark-theme');

  const [theme, setTheme] = useState('light');

  useEffect(() => {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-coreui-theme') || 'light';
    setTheme(currentTheme);

    const handleKeyDown = (event) => {
      if (event.key === 'F9') {
        event.preventDefault();
        setVisible(true);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  useEffect(() => {
    if (visible && inputRef.current) {
      setTimeout(() => {
        inputRef.current.focus();
      }, 100);
    }
  }, [visible]);

  return (
    <CButtonGroup className="mb-3">
      <CButton 
        color="primary" 
        variant="outline"
        size="sm"
        onClick={() => onNavigate(firstUrl)}
        disabled={!firstUrl}
      >
        <CIcon icon={cilChevronDoubleLeft} />
      </CButton>
      <CButton 
        color="primary" 
        variant="outline"
        size="sm"
        onClick={() => onNavigate(prevUrl)}
        disabled={!prevUrl}
      >
        <CIcon icon={cilChevronLeft} />
      </CButton>
      <CButton 
        color="primary" 
        variant="outline"
        size="sm"
        onClick={() => onNavigate(nextUrl)}
        disabled={!nextUrl}
      >
        <CIcon icon={cilChevronRight} />
      </CButton>
      <CButton 
        color="primary" 
        variant="outline"
        size="sm"
        onClick={() => onNavigate(lastUrl)}
        disabled={!lastUrl}
      >
        <CIcon icon={cilChevronDoubleRight} />
      </CButton>
      <CButton 
        color="primary" 
        size="sm"
        disabled={!canSave}
        onClick={onSave}
      >
        <CIcon icon={cilSave} />
      </CButton>
      <CButton 
        color="primary" 
        variant="outline"
        size="sm"
        onClick={() => setVisible(true)}
      >
        <CIcon icon={cilSearch} />
      </CButton>
      <CButton 
        color="danger" 
        variant="outline"
        size="sm"
        onClick={onReset}
      >
        <CIcon icon={cilX} />
      </CButton>

      <CModal visible={visible} onClose={() => setVisible(false)}>
        <CModalHeader className={theme === 'dark' ? 'bg-dark text-white' : ''}>
          <CModalTitle>Pesquisar Item</CModalTitle>
        </CModalHeader>
        <CModalBody className={theme === 'dark' ? 'bg-dark text-white' : ''}>
          <CFormInput
            type="text"
            placeholder="Digite o código do item"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleSearch();
              }
            }}
            ref={inputRef}
            required
          />
        </CModalBody>
        <CModalFooter>
          <CButton color="secondary" onClick={() => setVisible(false)}>
            Cancelar
          </CButton>
          <CButton color="primary" onClick={handleSearch}>
            Pesquisar
          </CButton>
        </CModalFooter>
      </CModal>
    </CButtonGroup>
  );
};

ItemNavigation.propTypes = {
  onNavigate: PropTypes.func.isRequired,
  nextUrl: PropTypes.string,
  prevUrl: PropTypes.string,
  firstUrl: PropTypes.string,
  lastUrl: PropTypes.string,
  onSave: PropTypes.func.isRequired,
  canSave: PropTypes.bool.isRequired,
  onSearch: PropTypes.func.isRequired,
  onReset: PropTypes.func.isRequired
};

export default ItemNavigation;