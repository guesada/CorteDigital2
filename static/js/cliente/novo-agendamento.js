// ===== NOVO SISTEMA DE AGENDAMENTO =====

let bookingState = {
  currentStep: 1,
  service: null,
  barber: null,
  date: null,
  time: null,
  services: [],
  barbers: [],
  currentMonth: new Date().getMonth(),
  currentYear: new Date().getFullYear()
};

// Inicializar sistema de agendamento
async function initNovoAgendamento() {
  console.log('🚀 Inicializando novo sistema de agendamento');
  
  // Resetar mês/ano para o atual
  const today = new Date();
  bookingState.currentMonth = today.getMonth();
  bookingState.currentYear = today.getFullYear();
  
  // Carregar dados
  await loadBarbersData(); // Carregar barbeiros primeiro
  await loadServicesData(); // Serviços depois
  
  // Renderizar primeira etapa (barbeiros)
  renderStep(1);
  updateProgress();
}

// Carregar serviços
async function loadServicesData() {
  try {
    // Adicionar timestamp para evitar cache
    const timestamp = new Date().getTime();
    const res = await fetch(`/api/services?_=${timestamp}`, { 
      credentials: 'include',
      cache: 'no-cache'
    });
    if (!res.ok) return;
    const data = await res.json();
    bookingState.services = data.data || [];
    console.log('📦 Serviços carregados:', bookingState.services);
    renderServices();
  } catch (error) {
    console.error('Erro ao carregar serviços:', error);
  }
}

// Carregar barbeiros
async function loadBarbersData() {
  try {
    const res = await fetch('/api/barbers', { credentials: 'include' });
    if (!res.ok) return;
    const data = await res.json();
    bookingState.barbers = data.data || [];
  } catch (error) {
    console.error('Erro ao carregar barbeiros:', error);
  }
}

// Renderizar serviços
function renderServices() {
  const container = document.getElementById('services-grid-new');
  if (!container) return;
  
  if (bookingState.services.length === 0) {
    container.innerHTML = `
      <div class="empty-state-services">
        <div class="empty-state-icon">
          <i class="fas fa-cut"></i>
        </div>
        <div class="empty-state-title">Nenhum serviço disponível</div>
        <div class="empty-state-text">Entre em contato para mais informações</div>
      </div>
    `;
    return;
  }
  
  // Ícones específicos para cada serviço
  const serviceIcons = {
    'Corte': 'fa-cut',
    'Barba': 'fa-user-tie',
    'Corte + Barba': 'fa-scissors'
  };
  
  container.innerHTML = bookingState.services.map((service, index) => {
    const isSelected = bookingState.service?.id === service.id;
    const icon = serviceIcons[service.nome] || 'fa-cut';
    const animationDelay = index * 0.1;
    
    return `
      <div class="service-card-modern ${isSelected ? 'selected' : ''}" 
           onclick="selectService(${service.id})"
           style="animation-delay: ${animationDelay}s">
        
        <!-- Badge de seleção -->
        <div class="service-selection-badge">
          <i class="fas fa-check-circle"></i>
        </div>
        
        <!-- Ícone do serviço -->
        <div class="service-icon-modern">
          <div class="service-icon-bg"></div>
          <i class="fas ${icon}"></i>
        </div>
        
        <!-- Informações do serviço -->
        <div class="service-info-modern">
          <h4 class="service-title-modern">${service.nome || 'Serviço'}</h4>
          <p class="service-desc-modern">${service.descricao || 'Serviço profissional de barbearia'}</p>
        </div>
        
        <!-- Detalhes (preço e duração) -->
        <div class="service-footer-modern">
          <div class="service-price-modern">
            <span class="price-label">A partir de</span>
            <span class="price-value">R$ ${parseFloat(service.preco || 0).toFixed(2).replace('.', ',')}</span>
          </div>
          <div class="service-duration-modern">
            <i class="fas fa-clock"></i>
            <span>${service.duracao || '30'} min</span>
          </div>
        </div>
        
        <!-- Efeito hover -->
        <div class="service-hover-effect"></div>
      </div>
    `;
  }).join('');
}

// Selecionar serviço
function selectService(serviceId) {
  const service = bookingState.services.find(s => s.id === serviceId);
  if (!service) return;
  
  bookingState.service = service;
  renderServices();
  updateNextButton();
}

// Renderizar barbeiros
function renderBarbers() {
  const container = document.getElementById('barbers-grid-new');
  if (!container) return;
  
  if (bookingState.barbers.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 3rem;">
        <i class="fas fa-user-tie" style="font-size: 3rem; color: #6366f1; opacity: 0.3; margin-bottom: 1rem;"></i>
        <p style="color: var(--color-text-secondary);">Nenhum barbeiro disponível no momento.</p>
      </div>
    `;
    return;
  }
  
  container.innerHTML = bookingState.barbers.map(barber => {
    const initial = (barber.nome || 'B')[0].toUpperCase();
    return `
      <div class="barber-card ${bookingState.barber?.id === barber.id ? 'selected' : ''}" 
           onclick="selectBarber(${barber.id})">
        <div class="barber-check">
          <i class="fas fa-check"></i>
        </div>
        <div class="barber-avatar">${initial}</div>
        <div class="barber-name">${barber.nome || 'Barbeiro'}</div>
        <div class="barber-rating">
          <i class="fas fa-star"></i>
          <i class="fas fa-star"></i>
          <i class="fas fa-star"></i>
          <i class="fas fa-star"></i>
          <i class="fas fa-star"></i>
        </div>
        <div class="barber-specialty">Especialista</div>
      </div>
    `;
  }).join('');
}

// Selecionar barbeiro
async function selectBarber(barberId) {
  const barber = bookingState.barbers.find(b => b.id === barberId);
  if (!barber) return;
  
  bookingState.barber = barber;
  renderBarbers();
  
  // Carregar preços personalizados do barbeiro
  console.log('💰 Carregando preços do barbeiro:', barberId);
  await loadBarberPrices(barberId);
  
  updateNextButton();
}

// Carregar preços personalizados do barbeiro
async function loadBarberPrices(barberId) {
  try {
    const response = await fetch(`/api/barber-prices?barbeiro_id=${barberId}`);
    const result = await response.json();
    
    if (result.success && result.data) {
      console.log('💰 Preços recebidos:', result.data);
      
      // Atualizar preços dos serviços
      bookingState.services.forEach(service => {
        const customPrice = result.data[service.nome];
        if (customPrice !== undefined) {
          service.preco = customPrice;
          console.log(`✅ Preço atualizado: ${service.nome} = R$ ${customPrice}`);
        }
      });
      
      // Re-renderizar serviços se já estiver na etapa de serviços
      if (bookingState.currentStep === 2) {
        renderServices();
      }
    }
  } catch (error) {
    console.error('❌ Erro ao carregar preços do barbeiro:', error);
  }
}

// Renderizar calendário
function renderCalendar() {
  const container = document.getElementById('calendar-grid-new');
  if (!container) return;
  
  const today = new Date();
  const currentMonth = bookingState.currentMonth;
  const currentYear = bookingState.currentYear;
  
  // Atualizar título
  const titleEl = document.getElementById('calendar-title-new');
  if (titleEl) {
    const monthNames = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
    titleEl.textContent = `${monthNames[currentMonth]} ${currentYear}`;
  }
  
  // Dias da semana
  const dayLabels = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
  let html = dayLabels.map(day => `<div class="calendar-day-label">${day}</div>`).join('');
  
  // Primeiro dia do mês
  const firstDay = new Date(currentYear, currentMonth, 1).getDay();
  
  // Dias vazios
  for (let i = 0; i < firstDay; i++) {
    html += '<div></div>';
  }
  
  // Dias do mês
  const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
  const todayDate = new Date();
  todayDate.setHours(0, 0, 0, 0);
  
  for (let day = 1; day <= daysInMonth; day++) {
    const date = new Date(currentYear, currentMonth, day);
    const dateStr = date.toISOString().split('T')[0];
    const isToday = day === today.getDate() && 
                    currentMonth === today.getMonth() && 
                    currentYear === today.getFullYear();
    const isPast = date < todayDate;
    const isSelected = bookingState.date === dateStr;
    
    const classes = [
      'calendar-day',
      isToday ? 'today' : '',
      isPast ? 'disabled' : '',
      isSelected ? 'selected' : ''
    ].filter(Boolean).join(' ');
    
    html += `<div class="${classes}" onclick="selectDate('${dateStr}')">${day}</div>`;
  }
  
  container.innerHTML = html;
}

// Selecionar data
async function selectDate(dateStr) {
  const date = new Date(dateStr + 'T00:00:00');
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  if (date < today) return;
  
  bookingState.date = dateStr;
  renderCalendar();
  await loadAvailableTimes();
  updateNextButton();
}

// Carregar horários disponíveis
async function loadAvailableTimes() {
  const container = document.getElementById('time-slots-new');
  if (!container) return;
  
  if (!bookingState.barber || !bookingState.date) {
    container.innerHTML = '';
    return;
  }
  
  try {
    // Buscar horários de trabalho do barbeiro
    const scheduleRes = await fetch(`/api/barber-schedule/${bookingState.barber.id}`);
    let barberSchedule = [];
    
    if (scheduleRes.ok) {
      const scheduleData = await scheduleRes.json();
      if (scheduleData.success) {
        barberSchedule = scheduleData.data || [];
      }
    }
    
    // Buscar horários ocupados
    const res = await fetch(`/api/appointments/for_barber/${bookingState.barber.id}?date=${bookingState.date}`, {
      credentials: 'include'
    });
    
    let occupied = [];
    if (res.ok) {
      const data = await res.json();
      occupied = (data.data || [])
        .filter(a => a.status !== 'cancelado')
        .map(a => a.time);
    }
    
    // Determinar dia da semana da data selecionada
    const selectedDate = new Date(bookingState.date + 'T00:00:00');
    const dayNames = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'];
    const dayOfWeek = dayNames[selectedDate.getDay()];
    
    // Buscar horários de trabalho para este dia
    const daySchedule = barberSchedule.find(d => d.dia === dayOfWeek);
    
    let times = [];
    if (daySchedule && daySchedule.ativo && daySchedule.horarios && daySchedule.horarios.length > 0) {
      // Usar horários configurados pelo barbeiro
      times = daySchedule.horarios.sort();
    } else {
      // Se não houver configuração, mostrar mensagem
      container.innerHTML = `
        <div class="no-schedule-message">
          <i class="fas fa-calendar-times"></i>
          <p>O barbeiro não trabalha neste dia</p>
        </div>
      `;
      return;
    }
    
    // Verificar se é hoje
    const today = new Date();
    const isToday = selectedDate.toDateString() === today.toDateString();
    
    container.innerHTML = times.map(time => {
      const isOccupied = occupied.includes(time);
      let isPast = false;
      
      if (isToday) {
        const [hours, minutes] = time.split(':').map(Number);
        const timeDate = new Date();
        timeDate.setHours(hours, minutes, 0, 0);
        isPast = timeDate <= today;
      }
      
      const isDisabled = isOccupied || isPast;
      const isSelected = bookingState.time === time;
      
      const classes = [
        'time-slot',
        isDisabled ? 'disabled' : '',
        isSelected ? 'selected' : ''
      ].filter(Boolean).join(' ');
      
      let statusText = '';
      if (isOccupied) {
        statusText = '<div class="time-slot-status occupied">Ocupado</div>';
      } else if (isPast) {
        statusText = '<div class="time-slot-status past">Passou</div>';
      }
      
      return `
        <div class="${classes}" onclick="selectTime('${time}')">
          <div class="time-slot-time">${time}</div>
          ${statusText}
        </div>
      `;
    }).join('');
    
  } catch (error) {
    console.error('Erro ao carregar horários:', error);
    container.innerHTML = `
      <div class="error-message">
        <i class="fas fa-exclamation-triangle"></i>
        <p>Erro ao carregar horários disponíveis</p>
      </div>
    `;
  }
}

// Selecionar horário
function selectTime(time) {
  const timeSlot = event.target.closest('.time-slot');
  if (timeSlot && timeSlot.classList.contains('disabled')) return;
  
  bookingState.time = time;
  loadAvailableTimes();
  updateNextButton();
}

// Renderizar resumo
function renderSummary() {
  const container = document.getElementById('booking-summary-new');
  if (!container) return;
  
  const dateObj = new Date(bookingState.date + 'T00:00:00');
  const dateFormatted = dateObj.toLocaleDateString('pt-BR', { 
    day: '2-digit', 
    month: 'long', 
    year: 'numeric' 
  });
  
  container.innerHTML = `
    <div class="summary-title">
      <i class="fas fa-clipboard-check"></i>
      Resumo do Agendamento
    </div>
    <div class="summary-item">
      <div class="summary-label">Serviço</div>
      <div class="summary-value">${bookingState.service?.nome || '-'}</div>
    </div>
    <div class="summary-item">
      <div class="summary-label">Barbeiro</div>
      <div class="summary-value">${bookingState.barber?.nome || '-'}</div>
    </div>
    <div class="summary-item">
      <div class="summary-label">Data</div>
      <div class="summary-value">${dateFormatted}</div>
    </div>
    <div class="summary-item">
      <div class="summary-label">Horário</div>
      <div class="summary-value">${bookingState.time || '-'}</div>
    </div>
    <div class="summary-item summary-total">
      <div class="summary-label">Total</div>
      <div class="summary-value">R$ ${parseFloat(bookingState.service?.preco || 0).toFixed(2)}</div>
    </div>
  `;
}

// Renderizar etapa
function renderStep(step) {
  // Esconder todas as etapas
  document.querySelectorAll('.booking-step').forEach(el => {
    el.classList.remove('active');
  });
  
  // Mostrar etapa atual
  const stepEl = document.getElementById(`booking-step-${step}`);
  if (stepEl) {
    stepEl.classList.add('active');
  }
  
  // Renderizar conteúdo específico
  if (step === 1) {
    renderBarbers(); // Primeiro escolhe o barbeiro
  } else if (step === 2) {
    renderServices(); // Depois escolhe o serviço (com preços atualizados)
  } else if (step === 3) {
    renderCalendar();
    if (bookingState.date) {
      loadAvailableTimes();
    }
  } else if (step === 4) {
    renderSummary();
  }
  
  updateNextButton();
}

// Atualizar progresso
function updateProgress() {
  const steps = document.querySelectorAll('.progress-step');
  const progressLine = document.querySelector('.progress-line');
  
  steps.forEach((step, index) => {
    const stepNum = index + 1;
    step.classList.remove('active', 'completed');
    
    if (stepNum < bookingState.currentStep) {
      step.classList.add('completed');
    } else if (stepNum === bookingState.currentStep) {
      step.classList.add('active');
    }
  });
  
  // Atualizar linha de progresso
  if (progressLine) {
    const progress = ((bookingState.currentStep - 1) / 3) * 100;
    progressLine.style.width = `${progress}%`;
  }
}

// Próxima etapa
function nextBookingStep() {
  if (bookingState.currentStep < 4) {
    bookingState.currentStep++;
    renderStep(bookingState.currentStep);
    updateProgress();
  } else {
    confirmarNovoAgendamento();
  }
}

// Etapa anterior
function prevBookingStep() {
  if (bookingState.currentStep > 1) {
    bookingState.currentStep--;
    renderStep(bookingState.currentStep);
    updateProgress();
  }
}

// Atualizar botão próximo
function updateNextButton() {
  const btn = document.getElementById('btn-booking-next');
  if (!btn) return;
  
  let canProceed = false;
  
  if (bookingState.currentStep === 1) {
    canProceed = bookingState.barber !== null; // Primeiro escolhe barbeiro
    btn.innerHTML = '<span>Próximo</span><i class="fas fa-arrow-right"></i>';
  } else if (bookingState.currentStep === 2) {
    canProceed = bookingState.service !== null; // Depois escolhe serviço
    btn.innerHTML = '<span>Próximo</span><i class="fas fa-arrow-right"></i>';
  } else if (bookingState.currentStep === 3) {
    canProceed = bookingState.date !== null && bookingState.time !== null;
    btn.innerHTML = '<span>Próximo</span><i class="fas fa-arrow-right"></i>';
  } else if (bookingState.currentStep === 4) {
    canProceed = true;
    btn.innerHTML = '<i class="fas fa-check"></i><span>Confirmar Agendamento</span>';
  }
  
  btn.disabled = !canProceed;
}

// Confirmar agendamento
async function confirmarNovoAgendamento() {
  const btn = document.getElementById('btn-booking-next');
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Agendando...</span>';
  }
  
  try {
    const body = {
      barberId: bookingState.barber.id,
      barberName: bookingState.barber.nome,
      serviceId: bookingState.service.id,
      serviceName: bookingState.service.nome,
      date: bookingState.date,
      time: bookingState.time,
      total: parseFloat(bookingState.service.preco || 0)
    };
    
    const res = await fetch('/api/appointments', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    
    const data = await res.json();
    
    // Verificar se foi sucesso (201 Created ou 200 OK)
    if (res.ok || res.status === 201 || data.success) {
      showNotificationToast('Agendamento criado com sucesso!', 'success');
      
      // Resetar estado
      bookingState = {
        currentStep: 1,
        service: null,
        barber: null,
        date: null,
        time: null,
        services: bookingState.services,
        barbers: bookingState.barbers,
        currentMonth: new Date().getMonth(),
        currentYear: new Date().getFullYear()
      };
      
      // Voltar para lista de agendamentos
      setTimeout(() => {
        switchTab('meus-agendamentos');
        loadAppointmentsAndStats();
        carregarAgendamentos();
      }, 1500);
    } else {
      throw new Error(data.message || 'Erro ao criar agendamento');
    }
  } catch (error) {
    console.error('Erro:', error);
    showNotificationToast(error.message || 'Erro ao criar agendamento', 'error');
    
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<i class="fas fa-check"></i><span>Confirmar Agendamento</span>';
    }
  }
}

// Navegação do calendário
function prevMonth() {
  bookingState.currentMonth--;
  
  if (bookingState.currentMonth < 0) {
    bookingState.currentMonth = 11;
    bookingState.currentYear--;
  }
  
  renderCalendar();
}

function nextMonth() {
  bookingState.currentMonth++;
  
  if (bookingState.currentMonth > 11) {
    bookingState.currentMonth = 0;
    bookingState.currentYear++;
  }
  
  renderCalendar();
}

// Exportar funções
window.initNovoAgendamento = initNovoAgendamento;
window.selectService = selectService;
window.selectBarber = selectBarber;
window.selectDate = selectDate;
window.selectTime = selectTime;
window.nextBookingStep = nextBookingStep;
window.prevBookingStep = prevBookingStep;
window.confirmarNovoAgendamento = confirmarNovoAgendamento;
window.prevMonth = prevMonth;
window.nextMonth = nextMonth;

console.log('✅ Novo sistema de agendamento carregado');
