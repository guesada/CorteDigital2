// ===== NOVA DASHBOARD DO CLIENTE =====

async function loadClienteDashboard() {
    console.log('📊 Carregando dashboard do cliente...');
    
    // Verificar se os elementos existem
    console.log('🔍 Verificando elementos:', {
        heroStatAtivos: !!document.getElementById('hero-stat-ativos'),
        heroStatConcluidos: !!document.getElementById('hero-stat-concluidos'),
        heroStatProximo: !!document.getElementById('hero-stat-proximo'),
        proximosLista: !!document.getElementById('proximos-agendamentos-lista')
    });
    
    try {
        const response = await fetch('/api/appointments');
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.message || 'Erro ao carregar agendamentos');
        }
        
        const appointments = result.data || [];
        console.log('📦 Agendamentos recebidos:', appointments.length);
        
        // Calcular estatísticas
        const today = new Date().toISOString().split('T')[0];
        
        const ativos = appointments.filter(a => 
            ['agendado', 'confirmado', 'pendente'].includes(a.status)
        ).length;
        
        const concluidos = appointments.filter(a => 
            a.status === 'concluido'
        ).length;
        
        // Próximo agendamento
        const proximos = appointments
            .filter(a => {
                const aptDate = a.data || a.date;
                return aptDate >= today && ['agendado', 'confirmado', 'pendente'].includes(a.status);
            })
            .sort((a, b) => {
                const dateA = a.data || a.date;
                const dateB = b.data || b.date;
                if (dateA !== dateB) return dateA.localeCompare(dateB);
                return (a.horario || a.time).localeCompare(b.horario || b.time);
            });
        
        // Atualizar stats do hero
        const statAtivos = document.getElementById('hero-stat-ativos');
        const statConcluidos = document.getElementById('hero-stat-concluidos');
        const statProximo = document.getElementById('hero-stat-proximo');
        
        if (statAtivos) statAtivos.textContent = ativos;
        if (statConcluidos) statConcluidos.textContent = concluidos;
        
        if (proximos.length > 0) {
            const proximo = proximos[0];
            const date = new Date((proximo.data || proximo.date) + 'T00:00:00');
            const dias = Math.ceil((date - new Date()) / (1000 * 60 * 60 * 24));
            if (statProximo) {
                statProximo.textContent = dias === 0 ? 'Hoje' : dias === 1 ? 'Amanhã' : `${dias}d`;
            }
        } else {
            if (statProximo) statProximo.textContent = '--';
        }
        
        // Atualizar stats antigos (se existirem - compatibilidade)
        const oldStatTotal = document.getElementById('stat-total');
        const oldStatConcluidos = document.getElementById('stat-concluidos');
        const oldStatProximo = document.getElementById('stat-proximo');
        const oldStatAtivos = document.getElementById('stat-ativos');
        
        if (oldStatTotal) oldStatTotal.textContent = ativos;
        if (oldStatConcluidos) oldStatConcluidos.textContent = concluidos;
        if (oldStatAtivos) oldStatAtivos.textContent = ativos;
        if (oldStatProximo) {
            if (proximos.length > 0) {
                const proximo = proximos[0];
                const date = new Date((proximo.data || proximo.date) + 'T00:00:00');
                const dias = Math.ceil((date - new Date()) / (1000 * 60 * 60 * 24));
                oldStatProximo.textContent = dias === 0 ? 'Hoje' : `${dias}d`;
            } else {
                oldStatProximo.textContent = '--';
            }
        }
        
        // Renderizar próximos agendamentos
        renderProximosAgendamentos(proximos.slice(0, 3));
        
    } catch (error) {
        console.error('❌ Erro ao carregar dashboard:', error);
    }
}

function renderProximosAgendamentos(appointments) {
    const container = document.getElementById('proximos-agendamentos-lista');
    
    if (!container) {
        console.warn('⚠️ Container proximos-agendamentos-lista não encontrado');
        return;
    }
    
    if (appointments.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">
                    <i class="fas fa-calendar-times"></i>
                </div>
                <div class="empty-title">Nenhum agendamento próximo</div>
                <div class="empty-text">Que tal agendar seu próximo corte?</div>
                <button class="empty-action" onclick="showSection('agendamentos-cliente'); setTimeout(() => switchTab('novo-agendamento'), 100);">
                    Agendar Agora
                </button>
            </div>
        `;
        return;
    }
    
    container.innerHTML = appointments.map(apt => {
        const aptDate = apt.data || apt.date;
        const aptTime = apt.horario || apt.time;
        const aptService = apt.servico || apt.service;
        const aptBarber = apt.barbeiro || apt.barbeiro_nome || apt.barber_name || 'Barbeiro';
        const aptPrice = apt.total_price || apt.preco || apt.price || 0;
        
        const date = new Date(aptDate + 'T00:00:00');
        const day = date.getDate();
        const month = date.toLocaleDateString('pt-BR', { month: 'short' }).toUpperCase();
        
        return `
            <div class="appointment-card">
                <div class="appointment-header">
                    <div class="appointment-date">
                        <div class="appointment-day">
                            <div class="appointment-day-number">${day}</div>
                            <div class="appointment-day-month">${month}</div>
                        </div>
                        <div class="appointment-info">
                            <div class="appointment-time">${aptTime}</div>
                            <div class="appointment-service">${aptService}</div>
                        </div>
                    </div>
                    <div class="appointment-status ${apt.status}">${apt.status}</div>
                </div>
                <div class="appointment-details">
                    <div class="appointment-detail">
                        <i class="fas fa-user-tie"></i>
                        ${aptBarber}
                    </div>
                    <div class="appointment-detail">
                        <i class="fas fa-dollar-sign"></i>
                        R$ ${parseFloat(aptPrice).toFixed(2).replace('.', ',')}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Carregar lista completa de agendamentos
async function carregarAgendamentos() {
    console.log('📋 Carregando lista de agendamentos...');
    
    const container = document.getElementById('agendamentos-lista');
    if (!container) return;
    
    try {
        const response = await fetch('/api/appointments');
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.message || 'Erro ao carregar agendamentos');
        }
        
        const appointments = result.data || [];
        
        if (appointments.length === 0) {
            container.innerHTML = `
                <div class="empty-agendamentos">
                    <div class="empty-agendamentos-icon">
                        <i class="fas fa-calendar-times"></i>
                    </div>
                    <div class="empty-agendamentos-title">Nenhum agendamento encontrado</div>
                    <div class="empty-agendamentos-text">Você ainda não tem agendamentos. Que tal agendar seu primeiro corte?</div>
                    <button class="empty-agendamentos-btn" onclick="switchTab('novo-agendamento')">
                        <i class="fas fa-plus"></i>
                        Agendar Agora
                    </button>
                </div>
            `;
            return;
        }
        
        // Ordenar por data (mais recentes primeiro)
        appointments.sort((a, b) => {
            const dateA = a.data || a.date;
            const dateB = b.data || b.date;
            if (dateA !== dateB) return dateB.localeCompare(dateA);
            return (b.horario || b.time).localeCompare(a.horario || a.time);
        });
        
        container.innerHTML = appointments.map(apt => {
            const aptDate = apt.data || apt.date;
            const aptTime = apt.horario || apt.time;
            const aptService = apt.servico || apt.service;
            const aptBarber = apt.barbeiro || apt.barbeiro_nome || apt.barber_name || 'Barbeiro';
            const aptPrice = apt.total_price || apt.preco || apt.price || 0;
            const aptStatus = apt.status || 'pendente';
            
            const date = new Date(aptDate + 'T00:00:00');
            const day = date.getDate();
            const month = date.toLocaleDateString('pt-BR', { month: 'short' }).toUpperCase();
            const fullDate = date.toLocaleDateString('pt-BR', { 
                day: '2-digit', 
                month: 'long', 
                year: 'numeric' 
            });
            
            const statusLabels = {
                'pendente': 'PENDENTE',
                'agendado': 'AGENDADO',
                'confirmado': 'CONFIRMADO',
                'concluido': 'CONCLUÍDO',
                'cancelado': 'CANCELADO'
            };
            
            return `
                <div class="agendamento-card">
                    <div class="agendamento-header">
                        <div class="agendamento-main">
                            <div class="agendamento-date-time">
                                <div class="agendamento-date-badge">
                                    <div class="agendamento-day">${day}</div>
                                    <div class="agendamento-month">${month}</div>
                                </div>
                                <div class="agendamento-time-info">
                                    <div class="agendamento-time">
                                        <i class="fas fa-clock"></i>
                                        ${aptTime}
                                    </div>
                                    <div class="agendamento-date-full">${fullDate}</div>
                                </div>
                            </div>
                            <div class="agendamento-service">
                                <i class="fas fa-cut"></i>
                                ${aptService}
                            </div>
                        </div>
                        <div class="agendamento-status-badge ${aptStatus}">
                            ${statusLabels[aptStatus] || aptStatus.toUpperCase()}
                        </div>
                    </div>
                    
                    <div class="agendamento-details">
                        <div class="agendamento-detail">
                            <div class="agendamento-detail-icon">
                                <i class="fas fa-user-tie"></i>
                            </div>
                            <div class="agendamento-detail-text">
                                <div class="agendamento-detail-label">BARBEIRO</div>
                                <div class="agendamento-detail-value">${aptBarber}</div>
                            </div>
                        </div>
                        <div class="agendamento-detail">
                            <div class="agendamento-detail-icon">
                                <i class="fas fa-dollar-sign"></i>
                            </div>
                            <div class="agendamento-detail-text">
                                <div class="agendamento-detail-label">VALOR</div>
                                <div class="agendamento-detail-value">R$ ${parseFloat(aptPrice).toFixed(2).replace('.', ',')}</div>
                            </div>
                        </div>
                    </div>
                    
                    ${(() => {
                        // Verificar se o agendamento já passou
                        const now = new Date();
                        const appointmentDateTime = new Date(`${apt.date}T${apt.time}`);
                        const hasPassed = appointmentDateTime <= now;
                        const canCancel = aptStatus !== 'cancelado' && aptStatus !== 'concluido' && !hasPassed;
                        
                        if (canCancel) {
                            return `
                                <div class="agendamento-actions">
                                    <button class="agendamento-btn agendamento-btn-cancel" onclick="cancelarAgendamento('${apt.id}')">
                                        <i class="fas fa-times"></i>
                                        Cancelar
                                    </button>
                                </div>
                            `;
                        } else if (hasPassed && aptStatus !== 'cancelado' && aptStatus !== 'concluido') {
                            return `
                                <div class="agendamento-info-message">
                                    <i class="fas fa-info-circle"></i>
                                    Agendamento já passou
                                </div>
                            `;
                        }
                        return '';
                    })()}
                </div>
            `;
        }).join('');
        
    } catch (error) {
        console.error('❌ Erro ao carregar agendamentos:', error);
        container.innerHTML = `
            <div class="empty-agendamentos">
                <div class="empty-agendamentos-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <div class="empty-agendamentos-title">Erro ao carregar agendamentos</div>
                <div class="empty-agendamentos-text">${error.message}</div>
            </div>
        `;
    }
}

// Cancelar agendamento
async function cancelarAgendamento(id) {
    // Criar modal de confirmação
    const modal = document.createElement('div');
    modal.className = 'cancel-modal-overlay';
    modal.innerHTML = `
        <div class="cancel-modal">
            <div class="cancel-modal-header">
                <div class="cancel-modal-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h3 class="cancel-modal-title">Cancelar Agendamento</h3>
                <p class="cancel-modal-subtitle">Esta ação não pode ser desfeita</p>
            </div>
            
            <div class="cancel-modal-body">
                <label class="cancel-checkbox-container">
                    <input type="checkbox" id="confirm-cancel-checkbox" class="cancel-checkbox-input">
                    <span class="cancel-checkbox-custom"></span>
                    <span class="cancel-checkbox-label">Confirmo que desejo cancelar este agendamento</span>
                </label>
            </div>
            
            <div class="cancel-modal-footer">
                <button class="cancel-modal-btn cancel-modal-btn-secondary" onclick="fecharModalCancelamento()">
                    <i class="fas fa-times"></i>
                    Voltar
                </button>
                <button class="cancel-modal-btn cancel-modal-btn-danger" id="confirm-cancel-btn" disabled onclick="confirmarCancelamento('${id}')">
                    <i class="fas fa-trash"></i>
                    Cancelar Agendamento
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Animar entrada
    setTimeout(() => modal.classList.add('active'), 10);
    
    // Habilitar botão quando checkbox for marcado
    const checkbox = document.getElementById('confirm-cancel-checkbox');
    const confirmBtn = document.getElementById('confirm-cancel-btn');
    
    checkbox.addEventListener('change', () => {
        confirmBtn.disabled = !checkbox.checked;
    });
}

// Fechar modal de cancelamento
function fecharModalCancelamento() {
    const modal = document.querySelector('.cancel-modal-overlay');
    if (modal) {
        modal.classList.remove('active');
        setTimeout(() => modal.remove(), 300);
    }
}

// Confirmar cancelamento
async function confirmarCancelamento(id) {
    const confirmBtn = document.getElementById('confirm-cancel-btn');
    confirmBtn.disabled = true;
    confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cancelando...';
    
    try {
        const response = await fetch(`/api/appointments/${id}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        const result = await response.json();
        
        if (result.success || response.ok) {
            showNotificationToast('Agendamento cancelado com sucesso!', 'success');
            fecharModalCancelamento();
            carregarAgendamentos();
            loadClienteDashboard();
        } else {
            throw new Error(result.message || 'Erro ao cancelar agendamento');
        }
    } catch (error) {
        console.error('❌ Erro ao cancelar:', error);
        showNotificationToast(error.message || 'Erro ao cancelar agendamento', 'error');
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = '<i class="fas fa-trash"></i> Cancelar Agendamento';
    }
}

// Carregar dashboard quando estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        loadClienteDashboard();
        carregarAgendamentos();
        loadHistoricoCliente();
    });
} else {
    loadClienteDashboard();
    carregarAgendamentos();
    loadHistoricoCliente();
}

// Exportar
window.loadClienteDashboard = loadClienteDashboard;
window.carregarAgendamentos = carregarAgendamentos;
window.cancelarAgendamento = cancelarAgendamento;
window.loadHistoricoCliente = loadHistoricoCliente;
window.fecharModalCancelamento = fecharModalCancelamento;
window.confirmarCancelamento = confirmarCancelamento;


// ===== HISTÓRICO DE SERVIÇOS =====
async function loadHistoricoCliente() {
    console.log('📜 Carregando histórico de serviços...');
    
    const container = document.getElementById('historico-lista');
    if (!container) return;
    
    // Mostrar loading
    container.innerHTML = `
        <div class="historico-loading">
            <i class="fas fa-spinner fa-spin"></i>
            Carregando histórico...
        </div>
    `;
    
    try {
        const response = await fetch('/api/appointments');
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.message || 'Erro ao carregar histórico');
        }
        
        const appointments = result.data || [];
        
        console.log('📦 Total de agendamentos:', appointments.length);
        console.log('📋 Status dos agendamentos:', appointments.map(a => ({ id: a.id, status: a.status })));
        
        // Normalizar campos
        appointments.forEach(a => {
            if (!a.data && a.date) a.data = a.date;
            if (!a.horario && a.time) a.horario = a.time;
            if (!a.preco && a.total_price) a.preco = a.total_price;
            if (!a.servico && a.service) a.servico = a.service;
            if (!a.barbeiro && a.barber_name) a.barbeiro = a.barber_name;
        });
        
        // Filtrar apenas concluídos
        const concluidos = appointments.filter(a => a.status === 'concluido');
        
        console.log('✅ Agendamentos concluídos:', concluidos.length);
        
        // Ordenar por data (mais recentes primeiro)
        concluidos.sort((a, b) => {
            const dateA = a.data;
            const dateB = b.data;
            if (dateA !== dateB) return dateB.localeCompare(dateA);
            return b.horario.localeCompare(a.horario);
        });
        
        // Atualizar stats
        const totalElement = document.getElementById('historico-total');
        const gastoElement = document.getElementById('historico-gasto');
        
        if (totalElement) totalElement.textContent = concluidos.length;
        
        const totalGasto = concluidos.reduce((sum, a) => {
            return sum + (parseFloat(a.preco || 0));
        }, 0);
        
        console.log('💰 Total gasto:', totalGasto);
        
        if (gastoElement) gastoElement.textContent = totalGasto.toFixed(2).replace('.', ',');
        
        // Renderizar histórico
        if (concluidos.length === 0) {
            container.innerHTML = `
                <div class="historico-empty">
                    <div class="historico-empty-icon">
                        <i class="fas fa-calendar-times"></i>
                    </div>
                    <div class="historico-empty-title">Nenhum serviço realizado ainda</div>
                    <div class="historico-empty-text">
                        Quando você concluir seus primeiros atendimentos, eles aparecerão aqui.
                    </div>
                    <button class="historico-empty-btn" onclick="showSection('agendamentos-cliente'); setTimeout(() => switchTab('novo-agendamento'), 100);">
                        <i class="fas fa-calendar-plus"></i>
                        Agendar Agora
                    </button>
                </div>
            `;
            return;
        }
        
        container.innerHTML = concluidos.map(apt => {
            const aptDate = apt.data;
            const aptTime = apt.horario;
            const aptService = apt.servico;
            const aptBarber = apt.barbeiro;
            const aptPrice = apt.preco;
            
            const date = new Date(aptDate + 'T00:00:00');
            const dateFormatted = date.toLocaleDateString('pt-BR', { 
                day: '2-digit', 
                month: 'long',
                year: 'numeric'
            });
            
            return `
                <div class="historico-item">
                    <div class="historico-item-header">
                        <div class="historico-item-date">
                            <i class="fas fa-calendar"></i>
                            ${dateFormatted} às ${aptTime}
                        </div>
                        <div class="historico-item-badge">
                            <i class="fas fa-check-circle"></i> Concluído
                        </div>
                    </div>
                    <div class="historico-item-content">
                        <div class="historico-item-info">
                            <div class="historico-item-service">
                                <i class="fas fa-cut"></i>
                                ${aptService}
                            </div>
                            <div class="historico-item-details">
                                <div class="historico-item-detail">
                                    <i class="fas fa-user"></i>
                                    ${aptBarber}
                                </div>
                            </div>
                        </div>
                        <div class="historico-item-price">
                            R$ ${parseFloat(aptPrice).toFixed(2).replace('.', ',')}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        console.log('✅ Histórico carregado:', concluidos.length, 'serviços');
        
    } catch (error) {
        console.error('❌ Erro ao carregar histórico:', error);
        container.innerHTML = `
            <div class="historico-empty">
                <div class="historico-empty-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <div class="historico-empty-title">Erro ao carregar histórico</div>
                <div class="historico-empty-text">
                    Não foi possível carregar seu histórico de serviços. Tente novamente.
                </div>
            </div>
        `;
    }
}
