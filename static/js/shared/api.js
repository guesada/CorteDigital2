// ===== API CONFIGURATION =====
const API_BASE = '/api';
const API = {
  appointments: '/api/appointments',
  barbers: '/api/barbers',
  services: '/api/services',
  notifications: '/api/notifications',
  products: '/api/products',
  users: '/api/users'
};

// ===== API HELPERS =====
async function apiRequest(url, options = {}) {
  const defaultOptions = {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    }
  };

  try {
    const response = await fetch(url, { ...defaultOptions, ...options });
    const data = await response.json();
    return { success: response.ok, data, status: response.status };
  } catch (error) {
    console.error('API Error:', error);
    return { success: false, error: error.message };
  }
}

// Export
window.API_BASE = API_BASE;
window.API = API;
window.apiRequest = apiRequest;
