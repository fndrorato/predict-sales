import React from 'react'
import PropTypes from 'prop-types'
import { Navigate } from 'react-router-dom'
import { getAccessToken } from '../services/auth'

const PrivateRoute = ({ element: Component }) => {
  const isAuthenticated = () => {
    const token = getAccessToken()
    return !!token
  }

  return isAuthenticated() ? Component : <Navigate to="/login" replace />
}

PrivateRoute.propTypes = {
  element: PropTypes.element.isRequired
}

export default PrivateRoute