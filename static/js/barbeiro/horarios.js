/**
 * Gerenciamento de Horários de Trabalho do Barbeiro
 */

// Estado global dos horários
let horariosState = [];

// Horários disponíveis para seleção
const HORARIOS_DISPONIVEIS = [
    "08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
    "11:00", "11:30", "12:00", "12:30", "13:00", "13:30",
    "14:00", "14:30", "15:00", "15:30", "16:00", "16:30",
    "17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00"
];

/**
 * Inicializa o módulo de horários
 */
async function initHorarios() {
    console.log('🕐 Inicializando módulo de horários');
    await loadHorarios();
    renderHorarios();
}

/**
 * Carrega os horários do barbeiro
 */
async function loadHorarios() {
    try {
        const response = await fetch('/api/barber-schedule');
        const result = await response.json();
        
        if (result.success) {
            horariosState = result.data;
            console.log('✅ Horários carregados:', horariosState);
        } else {
            console.error('❌ Erro ao carregar horários:', result.message);
            showNotification('Erro ao carregar horários', 'error');
        }
    } catch (error) {
        console.error('❌ Erro ao carregar horários:', error);
        showNotification('Erro ao carregar horários', 'error');
    }
}

/**
 * Renderiza a interface de horários
 */
function renderHorarios() {
    const container = document.getElementById('horarios-container');
    if (!container) return;
    
    container.innerHTML = `
        <div class="horarios-grid">
            ${horariosState.map((dia, index) => `
                <div class="horario-dia-card ${dia.ativo ? 'ativo' : 'inativo'}">
                    <div class="horario-dia-header">
                        <div class="horario-dia-info">
                            <h3 class="horario-dia-nome">${dia.dia}</h3>
                            <span class="horario-dia-status">
                                ${dia.ativo ? `${dia.horarios.length} horários` : 'Fechado'}
                            </span>
                        </div>
                        <label class="horario-toggle">
                            <input 
                                type="checkbox" 
                                ${dia.ativo ? 'checked' : ''} 
                                onchange="toggleDia(${index})"
                            >
                            <span class="toggle-slider"></span>
                        </label>
                    </div>
                    
                    ${dia.ativo ? `
                        <div class="horario-dia-content">
                            <div class="horarios-selecionados">
                                ${dia.horarios.length > 0 ? dia.horarios.map(h => `
                                    <span class="horario-tag">
                                        ${h}
                                        <button 
                                            class="horario-tag-remove" 
                                            onclick="removeHorario(${index}, '${h}')"
                                            title="Remover horário"
                                        >
                                            <i class="fas fa-times"></i>
                                        </button>
                                    </span>
                                `).join('') : '<p class="horarios-empty">Nenhum horário selecionado</p>'}
                            </div>
                            <button 
                                class="btn-adicionar-horario" 
                                onclick="openHorarioSelector(${index})"
                            >
                                <i class="fas fa-plus"></i>
                                <span>Adicionar Horários</span>
                            </button>
                        </div>
                    ` : ''}
                </div>
            `).join('')}
        </div>
        
        <div class="horarios-actions">
            <button class="btn-salvar-horarios" onclick="salvarHorarios()">
                <i class="fas fa-save"></i>
                Salvar Horários
            </button>
        </div>
    `;
}

/**
 * Ativa/desativa um dia da semana
 */
function toggleDia(index) {
    horariosState[index].ativo = !horariosState[index].ativo;
    
    // Se desativou, limpa os horários
    if (!horariosState[index].ativo) {
        horariosState[index].horarios = [];
    }
    
    renderHorarios();
}

/**
 * Remove um horário específico
 */
function removeHorario(diaIndex, horario) {
    horariosState[diaIndex].horarios = horariosState[diaIndex].horarios.filter(h => h !== horario);
    renderHorarios();
}

/**
 * Abre o seletor de horários
 */
function openHorarioSelector(diaIndex) {
    const dia = horariosState[diaIndex];
    const horariosJaSelecionados = dia.horarios;
    
    // Criar modal
    const modal = document.createElement('div');
    modal.className = 'horario-selector-modal';
    modal.innerHTML = `
        <div class="horario-selector-content">
            <div class="horario-selector-header">
                <h3>Selecionar Horários - ${dia.dia}</h3>
                <button class="horario-selector-close" onclick="closeHorarioSelector()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            
            <div class="horario-selector-body">
                <div class="horario-selector-grid">
                    ${HORARIOS_DISPONIVEIS.map(h => {
                        const selecionado = horariosJaSelecionados.includes(h);
                        return `
                            <button 
                                class="horario-selector-item ${selecionado ? 'selecionado' : ''}" 
                                data-horario="${h}"
                                onclick="toggleHorarioSelector(this, ${diaIndex}, '${h}')"
                            >
                                <span>${h}</span>
                                ${selecionado ? '<i class="fas fa-check"></i>' : ''}
                            </button>
                        `;
                    }).join('')}
                </div>
            </div>
            
            <div class="horario-selector-footer">
                <button class="btn-secondary" onclick="closeHorarioSelector()">
                    <i class="fas fa-times"></i>
                    <span>Cancelar</span>
                </button>
                <button class="btn-primary" onclick="confirmarHorarios(${diaIndex})">
                    <i class="fas fa-check"></i>
                    <span>Confirmar Seleção</span>
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Animar entrada
    setTimeout(() => modal.classList.add('active'), 10);
}

/**
 * Fecha o seletor de horários
 */
function closeHorarioSelector() {
    const modal = document.querySelector('.horario-selector-modal');
    if (modal) {
        modal.classList.remove('active');
        setTimeout(() => modal.remove(), 300);
    }
}

/**
 * Toggle de seleção de horário no modal
 */
function toggleHorarioSelector(button, diaIndex, horario) {
    button.classList.toggle('selecionado');
    
    const icon = button.querySelector('i');
    if (button.classList.contains('selecionado')) {
        if (!icon) {
            button.innerHTML += '<i class="fas fa-check"></i>';
        }
    } else {
        if (icon) {
            icon.remove();
        }
    }
}

/**
 * Confirma a seleção de horários
 */
function confirmarHorarios(diaIndex) {
    const selecionados = Array.from(document.querySelectorAll('.horario-selector-item.selecionado'))
        .map(btn => btn.dataset.horario)
        .sort();
    
    horariosState[diaIndex].horarios = selecionados;
    closeHorarioSelector();
    renderHorarios();
}

/**
 * Salva os horários no servidor
 */
async function salvarHorarios() {
    try {
        const button = document.querySelector('.btn-salvar-horarios');
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Salvando...';
        
        const response = await fetch('/api/barber-schedule', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                disponibilidade: horariosState
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Horários salvos com sucesso!', 'success');
        } else {
            showNotification('Erro ao salvar horários: ' + result.message, 'error');
        }
    } catch (error) {
        console.error('❌ Erro ao salvar horários:', error);
        showNotification('Erro ao salvar horários', 'error');
    } finally {
        const button = document.querySelector('.btn-salvar-horarios');
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-save"></i> Salvar Horários';
    }
}

/**
 * Mostra notificação
 */
function showNotification(message, type = 'info') {
    // Usar sistema de notificação existente ou criar um simples
    if (typeof showToast === 'function') {
        showToast(message, type);
    } else {
        alert(message);
    }
}

// Exportar funções globais
window.initHorarios = initHorarios;
window.toggleDia = toggleDia;
window.removeHorario = removeHorario;
window.openHorarioSelector = openHorarioSelector;
window.closeHorarioSelector = closeHorarioSelector;
window.toggleHorarioSelector = toggleHorarioSelector;
window.confirmarHorarios = confirmarHorarios;
window.salvarHorarios = salvarHorarios;

console.log('✅ Módulo de horários carregado');
