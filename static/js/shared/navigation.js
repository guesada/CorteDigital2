// ===== NAVIGATION FUNCTIONS =====

function showScreen(screenId) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  const targetScreen = document.getElementById(screenId);
  if (targetScreen) targetScreen.classList.add('active');
}

function selectUserType(type) {
  showScreen(`login-${type}`);
}

function showLogin(type) {
  showScreen(`login-${type}`);
}

function showRegister(type) {
  showScreen(`register-${type}`);
}

function goBack() {
  showScreen('user-selection');
}

function showSection(id) {
  document.querySelectorAll('.content-section, .section').forEach(s => s.classList.remove('active'));
  const tgt = document.getElementById(id);
  if (tgt) tgt.classList.add('active');
  
  // Trigger specific section loads
  if (id === 'historico-cliente' && typeof loadHistoricoCliente === 'function') {
    loadHistoricoCliente();
  }
  if (id === 'perfil-cliente' && typeof loadUserProfile === 'function') {
    setTimeout(loadUserProfile, 100);
  }
}

function switchTab(tabId, event) {
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
  
  if (event && event.target) {
    event.target.closest('.tab-btn')?.classList.add('active');
  } else {
    const targetBtn = Array.from(document.querySelectorAll('.tab-btn')).find(btn => 
      btn.getAttribute('onclick')?.includes(tabId)
    );
    if (targetBtn) targetBtn.classList.add('active');
  }
  
  document.getElementById(tabId)?.classList.add('active');
  
  // Trigger specific tab loads
  if (tabId === 'novo-agendamento' && typeof initNovoAgendamento === 'function') {
    setTimeout(() => initNovoAgendamento(), 100);
  }
  
  if (tabId === 'meus-agendamentos' && typeof carregarAgendamentos === 'function') {
    carregarAgendamentos();
  }
}

// Export
window.showScreen = showScreen;
window.selectUserType = selectUserType;
window.showLogin = showLogin;
window.showRegister = showRegister;
window.goBack = goBack;
window.showSection = showSection;
window.switchTab = switchTab;
