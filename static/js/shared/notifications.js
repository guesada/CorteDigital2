// ===== SISTEMA DE NOTIFICAÇÕES EM TEMPO REAL =====

let notificationCheckInterval = null;
let lastNotificationCheck = Date.now();
let notificationSound = null;

// Inicializar som de notificação
function initNotificationSound() {
  // Criar um beep simples usando Web Audio API
  const audioContext = new (window.AudioContext || window.webkitAudioContext)();
  
  return function playNotificationSound() {
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = 800;
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.5);
  };
}

// Controle de som para evitar spam
let lastSoundPlay = 0;
const SOUND_COOLDOWN = 2000; // 2 segundos entre sons

// Mostrar notificação visual
function showVisualNotification(title, message, type = 'info') {
  // Criar notificação no topo da tela
  const notification = document.createElement('div');
  notification.className = `visual-notification visual-notification-${type}`;
  notification.innerHTML = `
    <div class="visual-notification-icon">
      <i class="fas ${type === 'new-appointment' ? 'fa-calendar-plus' : 'fa-bell'}"></i>
    </div>
    <div class="visual-notification-content">
      <div class="visual-notification-title">${title}</div>
      <div class="visual-notification-message">${message}</div>
    </div>
    <button class="visual-notification-close" onclick="this.parentElement.remove()">
      <i class="fas fa-times"></i>
    </button>
  `;
  
  document.body.appendChild(notification);
  
  // Animar entrada
  setTimeout(() => notification.classList.add('show'), 10);
  
  // Tocar som apenas se passou tempo suficiente desde o último som
  const now = Date.now();
  if (notificationSound && (now - lastSoundPlay) > SOUND_COOLDOWN) {
    try {
      notificationSound();
      lastSoundPlay = now;
    } catch(e) {
      console.warn('Erro ao tocar som:', e);
    }
  }
  
  // Auto-remover após 10 segundos
  setTimeout(() => {
    notification.classList.remove('show');
    setTimeout(() => notification.remove(), 300);
  }, 10000);
}

// Armazenar IDs de notificações já mostradas
let shownNotificationIds = new Set();

// Verificar novas notificações
async function checkNewNotifications() {
  try {
    const response = await fetch('/api/notifications/check', {
      credentials: 'include',
      headers: {
        'X-Last-Check': lastNotificationCheck
      }
    });
    
    // Se não autenticado, parar polling
    if (response.status === 401) {
      console.log('Não autenticado, parando verificação de notificações');
      stopNotificationPolling();
      return;
    }
    
    if (!response.ok) {
      console.warn('Erro ao verificar notificações:', response.status);
      return;
    }
    
    const data = await response.json();
    
    if (data.notifications && data.notifications.length > 0) {
      // Filtrar apenas notificações que ainda não foram mostradas
      const newNotifications = data.notifications.filter(notif => {
        const notifId = notif.id || `${notif.title}-${notif.message}`;
        if (shownNotificationIds.has(notifId)) {
          return false;
        }
        shownNotificationIds.add(notifId);
        return true;
      });
      
      // Mostrar apenas notificações novas
      if (newNotifications.length > 0) {
        newNotifications.forEach(notif => {
          showVisualNotification(
            notif.title || 'Nova Notificação',
            notif.message || '',
            notif.type || 'info'
          );
        });
      }
      
      // Atualizar badge de notificações
      updateNotificationBadge(data.unreadCount || 0);
    }
    
    lastNotificationCheck = Date.now();
  } catch(error) {
    console.warn('Erro ao verificar notificações:', error);
  }
}

// Atualizar badge de notificações
function updateNotificationBadge(count) {
  const badge = document.querySelector('.notification-count');
  if (badge) {
    if (count > 0) {
      badge.textContent = count > 99 ? '99+' : count;
      badge.style.display = 'flex';
    } else {
      badge.style.display = 'none';
    }
  }
}

// Iniciar verificação periódica
function startNotificationPolling() {
  if (notificationCheckInterval) return;
  
  // Verificar a cada 10 segundos
  notificationCheckInterval = setInterval(checkNewNotifications, 10000);
  
  // Verificar imediatamente
  checkNewNotifications();
}

// Parar verificação
function stopNotificationPolling() {
  if (notificationCheckInterval) {
    clearInterval(notificationCheckInterval);
    notificationCheckInterval = null;
  }
}

// Inicializar quando o documento estiver pronto
document.addEventListener('DOMContentLoaded', () => {
  // Inicializar som
  notificationSound = initNotificationSound();
  
  // Iniciar polling se for barbeiro
  const isBarbeiro = document.getElementById('dashboard-barbeiro');
  if (isBarbeiro) {
    startNotificationPolling();
  }
});

// Exportar funções
window.showVisualNotification = showVisualNotification;
window.checkNewNotifications = checkNewNotifications;
window.startNotificationPolling = startNotificationPolling;
window.stopNotificationPolling = stopNotificationPolling;
