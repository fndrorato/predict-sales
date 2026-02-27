// Configuração da API
export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000/api/v1',
  COMPANY_ID: process.env.REACT_APP_COMPANY_ID || '1',
}

// Função para obter a URL da empresa
export const getCompanyEndpoint = () => {
  return `${API_CONFIG.BASE_URL}/company/${API_CONFIG.COMPANY_ID}/`
}

// Armazenamento para as configurações da empresa
export let COMPANY_SETTINGS = {}

// Função para buscar e armazenar as configurações da empresa
export const fetchCompanySettings = async (http) => {
  try {
    const response = await http.get(`/company/settings/${API_CONFIG.COMPANY_ID}/`)
    if (response.data && response.data.id) {
      COMPANY_SETTINGS = response.data
      return response.data
    }
  } catch (error) {
    console.error('Erro ao buscar configurações da empresa:', error)
    // Se o erro for 404, consideramos como configurações vazias com id=0
    if (error.response && error.response.status === 404) {
      COMPANY_SETTINGS = { id: 0 }
      return COMPANY_SETTINGS
    }
  }
  return null
}
