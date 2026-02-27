import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { CRow } from '@coreui/react'
import http from 'src/services/http'
import UserForm from './UserForm'

const DetailUser = () => {
  const { id } = useParams()
  const [user, setUser] = useState(null)

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await http.get(`/users/${id}/`)
        console.log('Dados User:', response.data) // Add thi
        setUser(response.data)
      } catch (error) {
        console.error('Error fetching user:', error)
      }
    }

    if (id) {
        fetchUser()
    }
  }, [id])

  return (
    <CRow>
      {user ? <UserForm user={user} /> : <div>Carregando...</div>}
    </CRow>
  )
}

export default DetailUser