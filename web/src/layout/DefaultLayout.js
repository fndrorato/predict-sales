import React, { useEffect } from 'react'
import { AppContent, AppSidebar, AppFooter, AppHeader } from '../components/index'
import { getCompanyEndpoint, fetchCompanySettings } from '../config'
import http from '../services/http'

const DefaultLayout = () => {
  useEffect(() => {
    const fetchCompanyData = async () => {
      try {
        // Buscar dados básicos da empresa
        const response = await fetch(getCompanyEndpoint())
        const data = await response.json()
        document.title = data.name
        const favicon = document.querySelector('link[rel="icon"]')
        if (favicon) {
          favicon.href = data.logo_icon
        }

        // Buscar configurações da empresa
        await fetchCompanySettings(http)
      } catch (error) {
        console.error('Error fetching company data:', error)
      }
    }

    fetchCompanyData()
  }, [])
  return (
    <div>
      <AppSidebar />
      <div className="wrapper d-flex flex-column min-vh-100 ">
        <AppHeader />
        <div className="body flex-grow-1">
          <AppContent />
        </div>
      </div>
    </div>
  )
}

export default DefaultLayout
