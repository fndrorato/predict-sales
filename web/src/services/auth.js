import { API_CONFIG } from '../config';

export const login = async (username, password) => {
  try {
    const response = await fetch(`${API_CONFIG.BASE_URL}/auth/token/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username,
        password,
      }),
    });

    if (!response.ok) {
      throw new Error('Falha na autenticação');
    }

    const data = await response.json();
    // Armazena os tokens e informações do usuário no localStorage
    localStorage.setItem('userId', data.user_id);
    localStorage.setItem('accessToken', data.access);
    localStorage.setItem('refreshToken', data.refresh);
    localStorage.setItem('firstName', data.first_name);
    localStorage.setItem('lastName', data.last_name);
    localStorage.setItem('permissions', JSON.stringify(data.permissions));
    return data;
  } catch (error) {
    throw error;
  }
};

export const getAccessToken = () => {
  return localStorage.getItem('accessToken');
};

export const getRefreshToken = () => {
  return localStorage.getItem('refreshToken');
};

export const getFirstName = () => {
  return localStorage.getItem('firstName');
};

export const getUserId = () => {
  return localStorage.getItem('userId');
};

export const getLastName = () => {
  return localStorage.getItem('lastName');
};

export const getPermissions = () => {
  const permissions = localStorage.getItem('permissions');
  return permissions ? JSON.parse(permissions) : [];
};

export const logout = async () => {
  try {
    const response = await fetch(`${API_CONFIG.BASE_URL}/auth/token/logout/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${getAccessToken()}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Falha ao realizar logout');
    }

    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('firstName');
    localStorage.removeItem('lastName');
    localStorage.removeItem('permissions');
  } catch (error) {
    throw error;
  }
};
