// ===== GERENCIAMENTO DE PREÇOS DO BARBEIRO =====
console.log('📦 Arquivo precos.js carregado');

let precosState = {
    loading: false,
    precos: {
        'Corte': 35.00,
        'Corte + Barba': 55.00,
        'Barba': 25.00
    }
};

// ===== INICIALIZAÇÃO =====
async function initPrecos() {
    console.log('💰 Inicializando gerenciamento de preços');
    await loadCurrentPrices();
    updatePreview();
}

// ===== CARREGAR PREÇOS ATUAIS =====
async function loadCurrentPrices() {
    try {
        const response = await fetch('/api/barber-prices');
        const result = await response.json();
        
        if (result.success) {
            precosState.precos = result.data;
            
            // Preencher inputs
            document.getElementById('price-corte').value = result.data['Corte'].toFixed(2);
            document.getElementById('price-corte-barba').value = result.data['Corte + Barba'].toFixed(2);
            document.getElementById('price-barba').value = result.data['Barba'].toFixed(2);
            
            console.log('✅ Preços carregados:', result.data);
        }
    } catch (error) {
        console.error('❌ Erro ao carregar preços:', error);
    }
}

// ===== ATUALIZAR PREVIEW =====
function updatePreview() {
    const corte = parseFloat(document.getElementById('price-corte').value) || 0;
    const corteBarba = parseFloat(document.getElementById('price-corte-barba').value) || 0;
    const barba = parseFloat(document.getElementById('price-barba').value) || 0;
    
    // Atualizar preview
    document.getElementById('preview-corte').textContent = `R$ ${corte.toFixed(2).replace('.', ',')}`;
    document.getElementById('preview-corte-barba').textContent = `R$ ${corteBarba.toFixed(2).replace('.', ',')}`;
    document.getElementById('preview-barba').textContent = `R$ ${barba.toFixed(2).replace('.', ',')}`;
}

// ===== SALVAR PREÇOS =====
async function handlePricesSubmit(event) {
    event.preventDefault();
    
    if (precosState.loading) return;
    
    const corte = parseFloat(document.getElementById('price-corte').value);
    const corteBarba = parseFloat(document.getElementById('price-corte-barba').value);
    const barba = parseFloat(document.getElementById('price-barba').value);
    
    // Validações
    if (corte <= 0 || corteBarba <= 0 || barba <= 0) {
        showNotification('Todos os preços devem ser maiores que zero', 'error');
        return;
    }
    
    if (corteBarba < corte) {
        showNotification('O preço de "Corte + Barba" deve ser maior ou igual ao preço do "Corte"', 'warning');
        return;
    }
    
    precosState.loading = true;
    
    // Atualizar botão
    const btn = document.querySelector('.btn-salvar-precos');
    const btnText = btn.querySelector('span');
    const btnIcon = btn.querySelector('i');
    
    btnText.textContent = 'Salvando...';
    btnIcon.className = 'fas fa-spinner fa-spin';
    btn.disabled = true;
    
    try {
        const response = await fetch('/api/barber-prices', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                'Corte': corte,
                'Corte + Barba': corteBarba,
                'Barba': barba
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            precosState.precos = {
                'Corte': corte,
                'Corte + Barba': corteBarba,
                'Barba': barba
            };
            
            // Mostrar mensagem de sucesso
            let message = 'Preços atualizados com sucesso!';
            if (result.clientes_notificados > 0) {
                message += ` ${result.clientes_notificados} cliente${result.clientes_notificados > 1 ? 's frequentes foram notificados' : ' frequente foi notificado'}.`;
            } else if (result.clientes_frequentes === false) {
                message += ' Nenhum cliente frequente (>5 agendamentos) para notificar.';
            }
            
            showSuccessMessage(message);
            showNotification(message, 'success');
            
            // Atualizar status
            updateStatus('Última atualização: agora');
        } else {
            showNotification(result.message || 'Erro ao salvar preços', 'error');
        }
    } catch (error) {
        console.error('❌ Erro ao salvar preços:', error);
        showNotification('Erro ao salvar preços. Tente novamente.', 'error');
    } finally {
        precosState.loading = false;
        btnText.textContent = 'Salvar Preços';
        btnIcon.className = 'fas fa-save';
        btn.disabled = false;
    }
}

// ===== MOSTRAR MENSAGEM DE SUCESSO =====
function showSuccessMessage(message) {
    // Remover mensagem anterior se existir
    const oldMessage = document.querySelector('.precos-success-message');
    if (oldMessage) {
        oldMessage.remove();
    }
    
    // Criar nova mensagem
    const successDiv = document.createElement('div');
    successDiv.className = 'precos-success-message';
    successDiv.innerHTML = `
        <i class="fas fa-check-circle"></i>
        <span>${message}</span>
    `;
    
    // Inserir antes do formulário
    const formCard = document.querySelector('.precos-form-card');
    formCard.parentNode.insertBefore(successDiv, formCard);
    
    // Remover após 5 segundos
    setTimeout(() => {
        successDiv.style.opacity = '0';
        successDiv.style.transform = 'translateY(-10px)';
        setTimeout(() => successDiv.remove(), 300);
    }, 5000);
}

// ===== ATUALIZAR STATUS =====
function updateStatus(text) {
    const statusEl = document.querySelector('.precos-status');
    if (statusEl) {
        statusEl.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span>${text}</span>
        `;
    }
}

// ===== NOTIFICAÇÃO TOAST =====
function showNotification(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `notification-toast ${type}`;
    
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    
    toast.innerHTML = `
        <i class="fas fa-${icons[type] || 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 10);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ===== VALIDAÇÃO EM TEMPO REAL =====
function setupRealtimeValidation() {
    const inputs = ['price-corte', 'price-corte-barba', 'price-barba'];
    
    inputs.forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.addEventListener('input', () => {
                updatePreview();
                
                // Validar valor
                const value = parseFloat(input.value);
                if (value < 0) {
                    input.value = 0;
                }
                
                // Limitar casas decimais
                if (input.value.includes('.')) {
                    const parts = input.value.split('.');
                    if (parts[1].length > 2) {
                        input.value = parseFloat(input.value).toFixed(2);
                    }
                }
            });
        }
    });
}

// ===== EXPORTAR FUNÇÕES =====
window.initPrecos = initPrecos;
window.handlePricesSubmit = handlePricesSubmit;
window.updatePreview = updatePreview;

// ===== INICIALIZAR =====
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setupRealtimeValidation();
    });
} else {
    setupRealtimeValidation();
}

console.log('✅ Sistema de preços pronto');
