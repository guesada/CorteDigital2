// ===== SISTEMA DE NOTIFICAÇÕES EM TEMPO REAL (POLLING) =====
console.log('🔔 Sistema de notificações em tempo real carregado');

let notificationState = {
    polling: false,
    interval: null,
    lastCheck: Date.now(),
    unreadCount: 0,
    checkInterval: 10000, // 10 segundos
    enabled: true
};

// ===== INICIAR POLLING =====
function startNotificationPolling() {
    if (notificationState.polling) {
        console.log('⚠️ Polling já está ativo');
        return;
    }
    
    console.log('🔔 Iniciando polling de notificações (a cada 10s)');
    notificationState.polling = true;
    notificationState.lastCheck = Date.now();
    
    // Verificar imediatamente
    checkNewNotifications();
    
    // Verificar periodicamente
    notificationState.interval = setInterval(() => {
        if (notificationState.enabled) {
            checkNewNotifications();
        }
    }, notificationState.checkInterval);
}

// ===== PARAR POLLING =====
function stopNotificationPolling() {
    if (notificationState.interval) {
        clearInterval(notificationState.interval);
        notificationState.interval = null;
        notificationState.polling = false;
        console.log('🔕 Polling de notificações parado');
    }
}

// ===== VERIFICAR NOVAS NOTIFICAÇÕES =====
async function checkNewNotifications() {
    try {
        const response = await fetch('/api/notifications/check', {
            headers: {
                'X-Last-Check': notificationState.lastCheck.toString()
            }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                // Não autenticado, parar polling
                stopNotificationPolling();
                return;
            }
            throw new Error(`HTTP ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            const { notifications, unreadCount } = result;
            
            // Atualizar contador
            const oldCount = notificationState.unreadCount;
            notificationState.unreadCount = unreadCount;
            updateNotificationBadge(unreadCount);
            
            // Mostrar novas notificações
            if (notifications && notifications.length > 0) {
                console.log(`🔔 ${notifications.length} nova(s) notificação(ões)`);
                
                notifications.forEach(notif => {
                    showInstantNotification(notif);
                });
                
                // Tocar som se houver novas notificações
                if (notifications.length > 0 && oldCount < unreadCount) {
                    playNotificationSound();
                }
            }
            
            // Atualizar timestamp
            notificationState.lastCheck = Date.now();
        }
    } catch (error) {
        console.error('❌ Erro ao verificar notificações:', error);
    }
}

// ===== MOSTRAR NOTIFICAÇÃO INSTANTÂNEA =====
function showInstantNotification(notification) {
    const { id, title, message, type } = notification;
    
    // Criar toast de notificação
    const toast = document.createElement('div');
    toast.className = `instant-notification ${type}`;
    toast.setAttribute('data-notification-id', id);
    
    // Ícone baseado no tipo
    const icons = {
        'preco_alterado': 'fa-dollar-sign',
        'new-appointment': 'fa-calendar-plus',
        'appointment-confirmed': 'fa-check-circle',
        'appointment-cancelled': 'fa-times-circle',
        'info': 'fa-info-circle',
        'success': 'fa-check-circle',
        'warning': 'fa-exclamation-triangle',
        'error': 'fa-exclamation-circle'
    };
    
    const icon = icons[type] || 'fa-bell';
    
    toast.innerHTML = `
        <div class="instant-notification-icon">
            <i class="fas ${icon}"></i>
        </div>
        <div class="instant-notification-content">
            <div class="instant-notification-title">${title}</div>
            <div class="instant-notification-message">${message}</div>
        </div>
        <button class="instant-notification-close" onclick="closeInstantNotification(${id})">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Adicionar ao container
    let container = document.getElementById('instant-notifications-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'instant-notifications-container';
        document.body.appendChild(container);
    }
    
    container.appendChild(toast);
    
    // Animar entrada
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Auto-remover após 8 segundos
    setTimeout(() => {
        closeInstantNotification(id);
    }, 8000);
    
    // Marcar como lida ao clicar
    toast.addEventListener('click', () => {
        markNotificationAsRead(id);
        closeInstantNotification(id);
    });
}

// ===== FECHAR NOTIFICAÇÃO INSTANTÂNEA =====
function closeInstantNotification(notificationId) {
    const toast = document.querySelector(`[data-notification-id="${notificationId}"]`);
    if (toast) {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }
}

// ===== MARCAR COMO LIDA =====
async function markNotificationAsRead(notificationId) {
    try {
        await fetch(`/api/notifications/${notificationId}/read`, {
            method: 'POST'
        });
        
        // Atualizar contador
        if (notificationState.unreadCount > 0) {
            notificationState.unreadCount--;
            updateNotificationBadge(notificationState.unreadCount);
        }
    } catch (error) {
        console.error('❌ Erro ao marcar notificação como lida:', error);
    }
}

// ===== ATUALIZAR BADGE DE NOTIFICAÇÕES =====
function updateNotificationBadge(count) {
    // Atualizar badge no header
    const badge = document.getElementById('notification-badge');
    if (badge) {
        if (count > 0) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.style.display = 'flex';
        } else {
            badge.style.display = 'none';
        }
    }
    
    // Atualizar ícone de notificação
    const icon = document.getElementById('notification-icon');
    if (icon) {
        if (count > 0) {
            icon.classList.add('has-notifications');
        } else {
            icon.classList.remove('has-notifications');
        }
    }
}

// ===== TOCAR SOM DE NOTIFICAÇÃO =====
function playNotificationSound() {
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        // Tom agradável
        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.2, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.2);
        
        // Segundo tom
        setTimeout(() => {
            const osc2 = audioContext.createOscillator();
            const gain2 = audioContext.createGain();
            
            osc2.connect(gain2);
            gain2.connect(audioContext.destination);
            
            osc2.frequency.value = 1000;
            osc2.type = 'sine';
            
            gain2.gain.setValueAtTime(0.2, audioContext.currentTime);
            gain2.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
            
            osc2.start(audioContext.currentTime);
            osc2.stop(audioContext.currentTime + 0.2);
        }, 100);
    } catch (error) {
        console.error('❌ Erro ao tocar som:', error);
    }
}

// ===== HABILITAR/DESABILITAR NOTIFICAÇÕES =====
function toggleNotifications(enabled) {
    notificationState.enabled = enabled;
    console.log(`🔔 Notificações ${enabled ? 'habilitadas' : 'desabilitadas'}`);
}

// ===== EXPORTAR FUNÇÕES =====
window.startNotificationPolling = startNotificationPolling;
window.stopNotificationPolling = stopNotificationPolling;
window.checkNewNotifications = checkNewNotifications;
window.closeInstantNotification = closeInstantNotification;
window.markNotificationAsRead = markNotificationAsRead;
window.toggleNotifications = toggleNotifications;

// ===== AUTO-INICIAR PARA CLIENTES =====
document.addEventListener('DOMContentLoaded', () => {
    // Verificar se é cliente logado
    const isCliente = document.body.classList.contains('cliente-dashboard') || 
                     document.getElementById('dashboard-cliente');
    
    if (isCliente) {
        console.log('👤 Cliente detectado, iniciando polling de notificações');
        setTimeout(() => {
            startNotificationPolling();
        }, 2000); // Aguardar 2s após carregar a página
    }
});

// ===== PARAR POLLING AO SAIR =====
window.addEventListener('beforeunload', () => {
    stopNotificationPolling();
});

console.log('✅ Sistema de notificações em tempo real pronto');
