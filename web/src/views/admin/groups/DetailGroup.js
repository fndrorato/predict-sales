import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { CRow } from '@coreui/react'
import http from 'src/services/http'
import GroupForm from './GroupForm'

const DetailGroup = () => {
  const { id } = useParams()
  const [group, setGroup] = useState(null)

  useEffect(() => {
    const fetchGroup = async () => {
      try {
        const response = await http.get(`/groups/${id}/`)
        console.log('group:', response.data)
        setGroup(response.data)
      } catch (error) {
        console.error('Error fetching group:', error)
      }
    }

    if (id) {
      fetchGroup()
    }
  }, [id])

  return (
    <CRow>
      <GroupForm group={group} />
    </CRow>
  )
}

export default DetailGroup