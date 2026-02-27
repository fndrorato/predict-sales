import React from 'react'
import CIcon from '@coreui/icons-react'
import {
  cilBarcode,
  cilAddressBook,
  cilPuzzle,
  cilSpeedometer,
  cilSettings,
  cibMessenger
} from '@coreui/icons'
import { CNavGroup, CNavItem, CNavTitle } from '@coreui/react'

const _nav = [
  {
    component: CNavItem,
    name: 'Dashboard',
    to: '/dashboard',
    icon: <CIcon icon={cilSpeedometer} customClassName="nav-icon" />,
  },
  {
    component: CNavTitle,
    name: 'Definições',
  },
  {
    component: CNavItem,
    name: 'Produtos',
    to: '/items',
    icon: <CIcon icon={cilBarcode} customClassName="nav-icon" />,
  },
  {
    component: CNavTitle,
    name: 'Compras',
  },
  {
    component: CNavGroup,
    name: 'Ordem de Compras',
    to: '/orders',
    icon: <CIcon icon={cilPuzzle} customClassName="nav-icon" />,
    items: [
      {
        component: CNavItem,
        name: 'Registros de Compras',
        to: '/orders',
      },
      {
        component: CNavItem,
        name: 'Pendentes de Aprovação',
        to: '/orders/pending',
      },
    ],
  },
  // {
  //   component: CNavTitle,
  //   name: 'Relatórios',
  // },
  // {
  //   component: CNavGroup,
  //   name: 'Vendas',
  //   to: '/reports/sales',
  //   icon: <CIcon icon={cilAddressBook} customClassName="nav-icon" />,
  //   items: [
  //     {
  //       component: CNavItem,
  //       name: 'Previsão de Vendas',
  //       to: '/reports/sales/forecast',
  //     }
  //   ],
  // },    
  {
    component: CNavTitle,
    name: 'Assistente Virtual',
  },
  {
    component: CNavItem,
    name: 'Chatbot',
    to: '/chatbot',
    icon: <CIcon icon={cibMessenger} customClassName="nav-icon" />,
  },   
  {
    component: CNavTitle,
    name: 'Configurações',
  },
  {
    component: CNavGroup,
    name: 'Gestão de Usuários',
    to: '/admin',
    icon: <CIcon icon={cilAddressBook} customClassName="nav-icon" />,
    items: [
      {
        component: CNavItem,
        name: 'Usuários',
        to: '/admin/users',
      },
      {
        component: CNavItem,
        name: 'Grupos',
        to: '/admin/groups',
      }
    ],
  },  
  {
    component: CNavItem,
    name: 'Configurar Sistema',
    to: '/admin/system/config',
    icon: <CIcon icon={cilSettings} customClassName="nav-icon" />,
  },


]

export default _nav
