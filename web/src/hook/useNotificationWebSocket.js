import { useEffect, useState } from 'react'
import http from '../services/http'

const buildWsBase = () => {
  // 1) se veio do .env, usa
  const envUrl = process.env.REACT_APP_WS_URL;
  if (envUrl) return envUrl.replace(/\/$/, '');

  // 2) senão, monta dinamicamente com base na página
  const isHttps = window.location.protocol === 'https:';
  const proto = isHttps ? 'wss' : 'ws';
  const host = window.location.hostname;

  // se estiver rodando React em :3000, o backend (Daphne) está em :5001
  const port = window.location.port === '3000' ? '5001' : window.location.port;

  return `${proto}://${host}${port ? `:${port}` : ''}`;
};

const useNotificationWebSocket = (userId, token) => {
  const [notifications, setNotifications] = useState([])
  const WS_BASE = buildWsBase();

  useEffect(() => {
    if (!userId || !token) return
    console.log('🔔 Iniciando WebSocket para notificações do usuário:', userId)
    console.log('com o token:', token)

    // Buscar notificações existentes da API
    const fetchNotifications = async () => {
      try {
        const response = await http.get('/notifications/')
        if (response.data && Array.isArray(response.data)) {
          setNotifications(response.data)
        }
      } catch (error) {
        console.error('Erro ao buscar notificações:', error)
      }
    }

    fetchNotifications()

    // Configurar WebSocket para notificações em tempo real
    const socket = new WebSocket(`${WS_BASE}/ws/notifications/?token=${token}`)

    socket.onopen = () => {
      console.log("✅ WebSocket conectado com sucesso")
    }
    
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      console.log("📨 Nova notificação recebida:", data)
      if (data.notification) {
        setNotifications((prev) => [data.notification, ...prev])
      }
    }
    
    socket.onclose = () => {
      console.warn("❌ WebSocket desconectado")
    }
    
    socket.onerror = (err) => {
      console.error("🔥 Erro no WebSocket:", err)
    }

    return () => socket.close()
  }, [userId, token])

  return notifications
}

export default useNotificationWebSocket
