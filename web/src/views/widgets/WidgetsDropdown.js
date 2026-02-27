import React, { useEffect, useRef, useState } from 'react'
import PropTypes from 'prop-types'
import { useTranslation } from 'react-i18next'
import http from '../../services/http'
import StockErrorsModal from 'src/components/StockErrorsModal'

import {
  CRow,
  CCol,
  CDropdown,
  CDropdownMenu,
  CDropdownItem,
  CDropdownToggle,
  CWidgetStatsA,
  CSpinner,
} from '@coreui/react'
import { getStyle } from '@coreui/utils'
import CIcon from '@coreui/icons-react'
import { cilArrowBottom, cilArrowTop, cilOptions } from '@coreui/icons'

const WidgetsDropdown = (props) => {
  const widgetChartRef1 = useRef(null)
  const widgetChartRef2 = useRef(null)
  const { t } = useTranslation()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showStockErrorsModal, setShowStockErrorsModal] = useState(false)

  useEffect(() => {
    http.get('/stats/')
      .then((response) => {
        setStats(response.data)
        setLoading(false)
      })
      .catch((error) => {
        console.error('Error fetching stats:', error)
        setLoading(false)
      })
  }, [])

  useEffect(() => {
    document.documentElement.addEventListener('ColorSchemeChange', () => {
      if (widgetChartRef1.current) {
        setTimeout(() => {
          widgetChartRef1.current.data.datasets[0].pointBackgroundColor = getStyle('--cui-primary')
          widgetChartRef1.current.update()
        })
      }

      if (widgetChartRef2.current) {
        setTimeout(() => {
          widgetChartRef2.current.data.datasets[0].pointBackgroundColor = getStyle('--cui-info')
          widgetChartRef2.current.update()
        })
      }
    })
  }, [widgetChartRef1, widgetChartRef2])

  return (
    <CRow className={props.className} xs={{ gutter: 4 }}>
      <CCol sm={6} xl={4} xxl={3}>
      <CWidgetStatsA
          color="primary"
          value={
            <>
              {loading ? (
                <CSpinner size="sm" />
              ) : (
                <>
                  {stats?.items_error_stock || '0'}{' '}
                </>
              )}
            </>
          }
          title={t('widgets.errorStock')}
          onClick={() => setShowStockErrorsModal(true)}
          style={{ cursor: 'pointer' }}
        />
        <StockErrorsModal
          visible={showStockErrorsModal}
          onClose={() => setShowStockErrorsModal(false)}
        />
      </CCol>
      <CCol sm={6} xl={4} xxl={3}>
        <CWidgetStatsA
          color="info"
          value={
            <>
              {loading ? (
                <CSpinner size="sm" />
              ) : (
                <>
                  {stats?.oc_overdue || '0'}{' '}
                </>
              )}
            </>
          }
          title={t('widgets.monthlyPunctuality')}

        />
      </CCol>
      <CCol sm={6} xl={4} xxl={3}>
        <CWidgetStatsA
          color="warning"
          value={
            <>
              {loading ? (
                <CSpinner size="sm" />
              ) : (
                <>
                  {stats?.oc_complete || '0'}{' '}

                </>
              )}
            </>
          }
          title={t('widgets.monthlyServiceRate')}

        />
      </CCol>
      <CCol sm={6} xl={4} xxl={3}>
        <CWidgetStatsA
          color="danger"
          value={
            <>
              {loading ? (
                <CSpinner size="sm" />
              ) : (
                <>
                  {stats?.oc_awaiting || '0'}{' '}
                </>
              )}
            </>
          }
          title={t('widgets.problemPurchaseOrders')}
        />
      </CCol>
    </CRow>
  )
}

WidgetsDropdown.propTypes = {
  className: PropTypes.string,
  withCharts: PropTypes.bool,
}

export default WidgetsDropdown
