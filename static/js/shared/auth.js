// ===== AUTHENTICATION FUNCTIONS =====

async function fazerLogin(e, destino) {
  e.preventDefault();
  const form = e.target;
  const email = form.querySelector('input[type="email"]').value;
  const password = form.querySelector('input[type="password"]').value;

  try {
    const response = await fetch(`${API_BASE}/users/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ email, password })
    });

    const data = await response.json();
    if (data.success) {
      const userType = data.user?.userType || destino;
      window.location.href = userType === 'barbeiro' ? '/barbeiro' : '/cliente';
    } else {
      if (typeof showNotificationToast === 'function') {
        showNotificationToast(data.message || 'Não foi possível entrar', 'error');
      } else {
        alert(data.message || 'Não foi possível entrar');
      }
    }
  } catch (error) {
    console.error('Login error:', error);
    if (typeof showNotificationToast === 'function') {
      showNotificationToast('Erro ao fazer login', 'error');
    } else {
      alert('Erro ao fazer login');
    }
  }
}

async function fazerCadastro(e, tipo) {
  e.preventDefault();
  const form = e.target;
  const name = form.querySelector('input[name="name"]').value;
  const email = form.querySelector('input[type="email"]').value;
  const password = form.querySelector('input[type="password"]').value;
  const phone = form.querySelector('input[name="phone"]')?.value || '';

  try {
    const response = await fetch(`${API_BASE}/users/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ name, email, password, phone, userType: tipo })
    });

    const data = await response.json();
    if (data.success) {
      if (typeof showNotificationToast === 'function') {
        showNotificationToast('Cadastro realizado com sucesso!', 'success');
      }
      setTimeout(() => {
        window.location.href = tipo === 'barbeiro' ? '/barbeiro' : '/cliente';
      }, 1000);
    } else {
      if (typeof showNotificationToast === 'function') {
        showNotificationToast(data.message || 'Erro ao cadastrar', 'error');
      } else {
        alert(data.message || 'Erro ao cadastrar');
      }
    }
  } catch (error) {
    console.error('Register error:', error);
    if (typeof showNotificationToast === 'function') {
      showNotificationToast('Erro ao fazer cadastro', 'error');
    } else {
      alert('Erro ao fazer cadastro');
    }
  }
}

async function logout() {
  try {
    await fetch(`${API_BASE}/users/logout`, {
      method: 'POST',
      credentials: 'include'
    });
    window.location.href = '/';
  } catch (error) {
    console.error('Logout error:', error);
    window.location.href = '/';
  }
}

// Export
window.fazerLogin = fazerLogin;
window.fazerCadastro = fazerCadastro;
window.logout = logout;
