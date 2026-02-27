import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { logout, getFirstName, getLastName } from '../../services/auth';
import {
  CAvatar,
  CBadge,
  CDropdown,
  CDropdownDivider,
  CDropdownHeader,
  CDropdownItem,
  CDropdownMenu,
  CDropdownToggle,
  CModal,
  CModalHeader,
  CModalTitle,
  CModalBody,
  CModalFooter,
  CButton,
  CForm,
  CFormInput,
  CAlert,
} from '@coreui/react';
import {
  cilBell,
  cilCommentSquare,
  cilLockLocked,
  cilShieldAlt,
  cilAccountLogout,
} from '@coreui/icons';
import CIcon from '@coreui/icons-react';
import http from 'src/services/http'


const AppHeaderDropdown = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [visible, setVisible] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const isDark = document.body.classList.contains('dark-theme');

  const [theme, setTheme] = useState('light');

  useEffect(() => {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-coreui-theme') || 'light';
    setTheme(currentTheme);
  }, [visible]); 

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    if (newPassword.length < 8) {
      setError('A nova senha deve ter no mínimo 8 caracteres');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('A confirmação da senha não corresponde à nova senha');
      return;
    }

    try {
      const response = await http.patch('/user/change-password/', {
        current_password: currentPassword,
        new_password: newPassword,
      });

      if (response.status === 200) {
        setSuccess(true);
        setTimeout(() => {
          setVisible(false);
          setCurrentPassword('');
          setNewPassword('');
          setConfirmPassword('');
          setSuccess(false);
        }, 2000);
      }
    } catch (error) {
      const errorData = error.response?.data;
      if (errorData) {
        if (errorData.current_password) {
          setError(errorData.current_password[0]);
        } else if (errorData.new_password) {
          setError(errorData.new_password[0]);
        } else if (errorData.detail) {
          setError(errorData.detail);
        } else {
          setError('Erro ao atualizar a senha. Por favor, tente novamente.');
        }
      } else {
        setError('Erro ao atualizar a senha. Por favor, tente novamente.');
      }
    }
  };
  return (
    <CDropdown variant="nav-item">
      <CDropdownToggle placement="bottom-end" className="py-0 pe-0" caret={false}>
        <CAvatar size="md" color="primary" className="bg-primary text-white">
          {getFirstName()?.charAt(0)?.toUpperCase()}
          {getLastName()?.charAt(0)?.toUpperCase()}
        </CAvatar>
      </CDropdownToggle>
      <CDropdownMenu className="pt-0" placement="bottom-end">
        <CDropdownHeader className="bg-body-secondary fw-semibold mb-2">
          {t('header.account')}
        </CDropdownHeader>
        <CDropdownItem href="#">
          <CIcon icon={cilBell} className="me-2" />
          {t('header.updates')}
          <CBadge color="info" className="ms-2">
            42
          </CBadge>
        </CDropdownItem>

        {/* <CDropdownItem href="#">
          <CIcon icon={cilCommentSquare} className="me-2" />
          {t('header.comments')}
          <CBadge color="warning" className="ms-2">
            42
          </CBadge>
        </CDropdownItem> */}
        <CDropdownHeader className="bg-body-secondary fw-semibold my-2">
          {t('header.settings')}
        </CDropdownHeader>
        <CDropdownItem onClick={() => setVisible(true)} style={{ cursor: 'pointer' }}>
          <CIcon icon={cilShieldAlt} className="me-2" />
          {t('header.changePassword')}
        </CDropdownItem>
        <CModal
          visible={visible}
          onClose={() => setVisible(false)}
          aria-labelledby="ChangePasswordModal"
          alignment="center"
        >
          <CModalHeader className={theme === 'dark' ? 'bg-dark text-white' : ''}>
            <CModalTitle>{t('header.changePassword')}</CModalTitle>
          </CModalHeader>

          <CModalBody className={theme === 'dark' ? 'bg-dark text-white' : ''}>
            <CForm onSubmit={handlePasswordChange}>
              {error && <CAlert color="danger">{error}</CAlert>}
              {success && <CAlert color="success">Senha atualizada com sucesso!</CAlert>}

              <div className="mb-3">
                <CFormInput
                  type="password"
                  label="Senha Atual"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  required
                  className={theme === 'dark' ? 'bg-dark text-white' : ''}
                />
              </div>
              <div className="mb-3">
                <CFormInput
                  type="password"
                  label="Nova Senha"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  className={theme === 'dark' ? 'bg-dark text-white' : ''}
                />
              </div>
              <div className="mb-3">
                <CFormInput
                  type="password"
                  label="Confirmar Nova Senha"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  className={theme === 'dark' ? 'bg-dark text-white' : ''}
                />
              </div>

              <CModalFooter className={theme === 'dark' ? 'bg-dark' : ''}>
                <CButton color="secondary" onClick={() => setVisible(false)}>
                  Cancelar
                </CButton>
                <CButton color="primary" type="submit">
                  Salvar
                </CButton>
              </CModalFooter>
            </CForm>
          </CModalBody>
        </CModal>

        <CDropdownDivider />
        <CDropdownItem href="#">
          <CIcon icon={cilLockLocked} className="me-2" />
          {t('header.lockAccount')}
        </CDropdownItem>
        <CDropdownItem
          className="cursor-pointer"
          onClick={async () => {
            try {
              await logout();
            } catch (error) {
              console.error('Erro ao fazer logout:', error);
            } finally {
              localStorage.removeItem('accessToken');
              localStorage.removeItem('refreshToken');
              navigate('/login');
            }
          }}
        >
          <CIcon icon={cilAccountLogout} className="me-2" />
          {t('header.logout')}
        </CDropdownItem>
      </CDropdownMenu>
    </CDropdown>
  );
};

export default AppHeaderDropdown;
