// ===== MICRO-INTERAÇÕES E ANIMAÇÕES =====

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
  initMicroInteractions();
  initThemeToggle();
  initDateTime();
  initAnimations();
});

// Micro-interações gerais
function initMicroInteractions() {
  // Ripple effect em botões
  document.querySelectorAll('.btn, .btn-modern, .header-btn').forEach(button => {
    button.addEventListener('click', createRipple);
  });

  // Hover effect suave em cards
  document.querySelectorAll('.elegant-card, .stat-card-modern').forEach(card => {
    card.addEventListener('mouseenter', (e) => {
      e.currentTarget.style.transform = 'translateY(-4px)';
    });
    card.addEventListener('mouseleave', (e) => {
      e.currentTarget.style.transform = 'translateY(0)';
    });
  });

  // Animação de entrada para elementos visíveis
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.animate-fade-in-up').forEach(el => {
    observer.observe(el);
  });
}

// Efeito ripple
function createRipple(event) {
  const button = event.currentTarget;
  const ripple = document.createElement('span');
  const diameter = Math.max(button.clientWidth, button.clientHeight);
  const radius = diameter / 2;

  const rect = button.getBoundingClientRect();
  ripple.style.width = ripple.style.height = `${diameter}px`;
  ripple.style.left = `${event.clientX - rect.left - radius}px`;
  ripple.style.top = `${event.clientY - rect.top - radius}px`;
  ripple.classList.add('ripple');

  const existingRipple = button.querySelector('.ripple');
  if (existingRipple) {
    existingRipple.remove();
  }

  button.appendChild(ripple);

  setTimeout(() => {
    ripple.remove();
  }, 600);
}

// CSS para ripple (adicionar dinamicamente)
const rippleStyle = document.createElement('style');
rippleStyle.textContent = `
  .ripple {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.6);
    transform: scale(0);
    animation: ripple-animation 0.6s ease-out;
    pointer-events: none;
  }

  @keyframes ripple-animation {
    to {
      transform: scale(4);
      opacity: 0;
    }
  }

  button, .btn, .btn-modern, .header-btn {
    position: relative;
    overflow: hidden;
  }
`;
document.head.appendChild(rippleStyle);

// Toggle de tema com animação
function initThemeToggle() {
  // Carregar tema salvo ou usar dark como padrão
  const savedTheme = localStorage.getItem('theme') || 'dark';
  document.documentElement.setAttribute('data-color-scheme', savedTheme);
  
  const themeIcon = document.getElementById('theme-icon');
  if (themeIcon) {
    themeIcon.className = savedTheme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
  }
}

function toggleTheme() {
  const html = document.documentElement;
  const currentTheme = html.getAttribute('data-color-scheme') || 'dark';
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  
  // Animação de transição
  html.style.transition = 'background-color 0.3s ease, color 0.3s ease';
  html.setAttribute('data-color-scheme', newTheme);
  localStorage.setItem('theme', newTheme);
  
  // Atualizar ícone
  const themeIcon = document.getElementById('theme-icon');
  if (themeIcon) {
    themeIcon.style.transform = 'rotate(360deg)';
    setTimeout(() => {
      themeIcon.className = newTheme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
      themeIcon.style.transform = 'rotate(0deg)';
    }, 150);
  }

  // Feedback visual
  showNotificationToast(
    `Tema ${newTheme === 'dark' ? 'escuro' : 'claro'} ativado`,
    'info'
  );
}

// Atualizar data e hora em tempo real
function initDateTime() {
  const dateTimeElement = document.getElementById('current-datetime');
  if (!dateTimeElement) return;

  function updateDateTime() {
    const now = new Date();
    const options = { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    dateTimeElement.textContent = now.toLocaleDateString('pt-BR', options);
  }

  updateDateTime();
  setInterval(updateDateTime, 60000); // Atualizar a cada minuto
}

// Animações de entrada
function initAnimations() {
  // Animar cards ao carregar
  const cards = document.querySelectorAll('.stat-card-modern, .elegant-card');
  cards.forEach((card, index) => {
    card.style.animationDelay = `${index * 0.1}s`;
    card.classList.add('animate-fade-in-up');
  });
}

// Notificação toast moderna
function showNotificationToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  const icons = {
    success: 'fa-check-circle',
    error: 'fa-exclamation-circle',
    warning: 'fa-exclamation-triangle',
    info: 'fa-info-circle'
  };

  toast.innerHTML = `
    <i class="fas ${icons[type]}"></i>
    <span>${message}</span>
  `;

  document.body.appendChild(toast);

  // Animar entrada
  setTimeout(() => toast.classList.add('show'), 10);

  // Remover após 3 segundos
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// CSS para toast (adicionar dinamicamente)
const toastStyle = document.createElement('style');
toastStyle.textContent = `
  .toast {
    position: fixed;
    top: 20px;
    right: 20px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    padding: 1rem 1.5rem;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
    display: flex;
    align-items: center;
    gap: 0.75rem;
    z-index: 10000;
    transform: translateX(400px);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    border-left: 4px solid;
    font-size: 0.875rem;
    font-weight: 500;
  }

  [data-color-scheme="dark"] .toast {
    background: rgba(38, 40, 40, 0.95);
    color: var(--color-text);
  }

  .toast.show {
    transform: translateX(0);
  }

  .toast-success {
    border-left-color: var(--color-success);
    color: var(--color-success);
  }

  .toast-error {
    border-left-color: var(--color-error);
    color: var(--color-error);
  }

  .toast-warning {
    border-left-color: var(--color-warning);
    color: var(--color-warning);
  }

  .toast-info {
    border-left-color: var(--color-teal-500);
    color: var(--color-teal-600);
  }

  .toast i {
    font-size: 1.25rem;
  }

  @media (max-width: 768px) {
    .toast {
      right: 10px;
      left: 10px;
      transform: translateY(-100px);
    }

    .toast.show {
      transform: translateY(0);
    }
  }
`;
document.head.appendChild(toastStyle);

// Smooth scroll para navegação
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  });
});

// Loading state para botões
function setButtonLoading(button, loading = true) {
  if (loading) {
    button.disabled = true;
    button.dataset.originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Carregando...';
  } else {
    button.disabled = false;
    button.innerHTML = button.dataset.originalText || button.innerHTML;
  }
}

// Contador animado para números
function animateCounter(element, target, duration = 1000) {
  const start = 0;
  const increment = target / (duration / 16);
  let current = start;

  const timer = setInterval(() => {
    current += increment;
    if (current >= target) {
      element.textContent = target;
      clearInterval(timer);
    } else {
      element.textContent = Math.floor(current);
    }
  }, 16);
}

// Inicializar contadores quando visíveis
const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting && !entry.target.dataset.animated) {
      const targetText = entry.target.dataset.count || entry.target.textContent;
      const target = parseInt(targetText);
      
      // Só animar se for um número válido
      if (!isNaN(target) && target >= 0) {
        animateCounter(entry.target, target);
        entry.target.dataset.animated = 'true';
      }
    }
  });
}, { threshold: 0.5 });

// Observar apenas elementos com números
document.querySelectorAll('.stat-number-modern, .stat-number').forEach(el => {
  // Não observar elementos que contêm texto não-numérico
  const text = el.textContent.trim();
  if (!text.includes('R$') && !text.includes('--') && !text.includes(':')) {
    counterObserver.observe(el);
  }
});

// Exportar funções globais
window.toggleTheme = toggleTheme;
window.showNotificationToast = showNotificationToast;
window.setButtonLoading = setButtonLoading;
window.animateCounter = animateCounter;
