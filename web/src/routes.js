import React from 'react'
import PrivateRoute from './components/PrivateRoute'

const Dashboard = React.lazy(() => import('./views/dashboard/Dashboard'))

// Users Admin
const Groups = React.lazy(() => import('./views/admin/groups/Groups'))
const NewGroup = React.lazy(() => import('./views/admin/groups/NewGroup'))
const DetailGroup = React.lazy(() => import('./views/admin/groups/DetailGroup'))
const Users = React.lazy(() => import('./views/admin/users/Users'))
const NewUser = React.lazy(() => import('./views/admin/users/NewUser'))
const DetailUser = React.lazy(() => import('./views/admin/users/DetailUser'))

// System Config
const SystemConfig = React.lazy(() => import('./views/admin/system/SystemConfig'))

// Items
const Items = React.lazy(() => import('./views/items/Items'))

// Compras
const Orders = React.lazy(() => import('./views/orders/Orders'))
const PendingApproval = React.lazy(() => import('./views/orders/pending/PendingApproval'))

// Reportes
const SalesForecast = React.lazy(() => import('./views/sales/forecast/SalesForecast'))

// Chatbot
const Chatbot = React.lazy(() => import('./views/chatbot/Chatbot'))


const routes = [
  { path: '/', exact: true, name: 'Home' },
  { path: '/dashboard', name: 'Dashboard', element: <PrivateRoute element={<Dashboard />} /> },
  { path: '/admin/users', name: 'Users', element: <PrivateRoute element={<Users />} /> },
  { path: '/admin/users/new', name: 'Users', element: <PrivateRoute element={<NewUser />} /> },
  { path: '/admin/users/:id', name: 'Users', element: <PrivateRoute element={<DetailUser />} /> },
  { path: '/admin/users', name: 'Users', element: <PrivateRoute element={<Users />} /> },
  { path: '/admin/groups', name: 'Groups', element: <PrivateRoute element={<Groups />} /> },
  { path: '/admin/groups/new', name: 'New Group', element: <PrivateRoute element={<NewGroup />} /> },
  { path: '/admin/groups/:id', name: 'Detail Group', element: <PrivateRoute element={<DetailGroup />} /> },
  { path: '/admin/system/config', name: 'Configurações do Sistema', element: <PrivateRoute element={<SystemConfig />} /> },
  { path: '/items', name: 'Produtos', element: <PrivateRoute element={<Items />} /> },
  { path: '/orders', name: 'Compras', element: <PrivateRoute element={<Orders />} /> },
  { path: '/orders/pending', name: 'Pendente Aprovação', element: <PrivateRoute element={<PendingApproval />} /> },
  { path: '/reports/sales/forecast', name: 'Previsão de Vendas', element: <PrivateRoute element={<SalesForecast />} /> },
  { path: '/chatbot', name: 'Chatbot', element: <PrivateRoute element={<Chatbot />} /> },
  
  
]

export default routes
