import React from 'react';
import PropTypes from 'prop-types';
import {
  CModal,
  CModalHeader,
  CModalTitle,
  CModalBody,
  CRow,
  CCol,
  CCard,
  CCardBody,
} from '@coreui/react';
import { CChart } from '@coreui/react-chartjs';

const ItemStatsModal = ({ visible, onClose, itemStats }) => {
  if (!itemStats) return null;

  return (
    <CModal 
      visible={visible} 
      onClose={onClose}
      size="lg"
    >
      <CModalHeader>
        <CModalTitle className="text-body-secondary">Estatísticas do Item</CModalTitle>
      </CModalHeader>
      <CModalBody>
        <CRow>
          <CCol xs={12}>
            <h4 className="text-body-secondary">{itemStats.item_name}</h4>
          </CCol>
          <CCol xs={12} md={4}>
            <CCard className="mb-4">
              <CCardBody className="text-center">
                <div className="h4 mb-0">{itemStats.total_last_30_days}</div>
                <small className="text-body-secondary">Total últimos 30 dias</small>
              </CCardBody>
            </CCard>
          </CCol>
          <CCol xs={12} md={4}>
            <CCard className="mb-4">
              <CCardBody className="text-center">
                <div className="h4 mb-0">{itemStats.average_last_30_days.toFixed(2)}</div>
                <small className="text-body-secondary">Média diária últimos 30 dias</small>
              </CCardBody>
            </CCard>
          </CCol>
          <CCol xs={12} md={4}>
            <CCard className="mb-4">
              <CCardBody className="text-center">
                <div className="h4 mb-0">{itemStats.average_daily_last_8_weeks.toFixed(2)}</div>
                <small className="text-body-secondary">Média diária últimas 8 semanas</small>
              </CCardBody>
            </CCard>
          </CCol>          
          <CCol xs={12}>
            <CCard className="mb-4">
              <CCardBody>
                <h4 className="card-title mb-4">Vendas Semanais (Últimas 8 Semanas)</h4>
                <CChart
                  type="line"
                  data={{
                    labels: itemStats.weekly_sales_last_8_weeks.map(week => week.week),
                    datasets: [
                      {
                        label: 'Vendas',
                        backgroundColor: 'rgba(0, 123, 255, 0.1)',
                        borderColor: 'rgba(0, 123, 255, 1)',
                        pointBackgroundColor: 'rgba(0, 123, 255, 1)',
                        pointBorderColor: '#fff',
                        data: itemStats.weekly_sales_last_8_weeks.map(week => parseFloat(week.total)),
                        fill: true,
                        tension: 0.4,
                      },
                    ],
                  }}
                  options={{
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        display: false,
                      },
                      tooltip: {
                        position: 'nearest',
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        padding: 10,
                        displayColors: true
                      },
                    },
                    scales: {
                      x: {
                        grid: {
                          drawOnChartArea: false,
                        },
                      },
                      y: {
                        beginAtZero: true,
                        grid: {
                          drawOnChartArea: true,
                        },
                      },
                    },
                  }}
                  style={{ height: '300px' }}
                />
              </CCardBody>
            </CCard>
          </CCol>
        </CRow>
      </CModalBody>
    </CModal>
  );
};

ItemStatsModal.propTypes = {
  visible: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  itemStats: PropTypes.shape({
    item_name: PropTypes.string.isRequired,
    total_last_30_days: PropTypes.number.isRequired,
    average_last_30_days: PropTypes.number.isRequired,
    average_daily_last_8_weeks: PropTypes.number.isRequired,
    weekly_sales_last_8_weeks: PropTypes.arrayOf(
      PropTypes.shape({
        week: PropTypes.string.isRequired,
        total: PropTypes.string.isRequired,
      })
    ).isRequired,
  }),
};

export default ItemStatsModal;