// ===== SISTEMA DE AVALIAÇÕES =====
console.log('⭐ Sistema de avaliações carregado');

let reviewState = {
    currentAppointment: null,
    selectedRating: 0
};

// ===== ABRIR MODAL DE AVALIAÇÃO =====
function openReviewModal(appointmentId) {
    console.log('⭐ Abrindo modal de avaliação para:', appointmentId);
    
    // Buscar informações do agendamento
    fetch('/api/appointments')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const appointment = data.data.find(a => a.id === appointmentId);
                if (appointment) {
                    reviewState.currentAppointment = appointment;
                    reviewState.selectedRating = 0;
                    renderReviewModal(appointment);
                }
            }
        })
        .catch(err => console.error('Erro ao buscar agendamento:', err));
}

// ===== RENDERIZAR MODAL =====
function renderReviewModal(appointment) {
    // Remover modal existente
    const existingModal = document.getElementById('review-modal-overlay');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Criar modal
    const modal = document.createElement('div');
    modal.id = 'review-modal-overlay';
    modal.className = 'review-modal-overlay';
    
    modal.innerHTML = `
        <div class="review-modal">
            <div class="review-modal-header">
                <h3 class="review-modal-title">
                    <i class="fas fa-star"></i>
                    Avaliar Atendimento
                </h3>
                <button class="review-modal-close" onclick="closeReviewModal()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            
            <div class="review-appointment-info">
                <div class="review-appointment-info-row">
                    <i class="fas fa-cut"></i>
                    <strong>Serviço:</strong> ${appointment.servico}
                </div>
                <div class="review-appointment-info-row">
                    <i class="fas fa-user-tie"></i>
                    <strong>Barbeiro:</strong> ${appointment.barbeiro}
                </div>
                <div class="review-appointment-info-row">
                    <i class="fas fa-calendar"></i>
                    <strong>Data:</strong> ${formatDate(appointment.date)} às ${appointment.time}
                </div>
            </div>
            
            <div class="review-rating-section">
                <label class="review-rating-label">Como foi sua experiência?</label>
                <div class="review-stars" id="review-stars">
                    ${[1, 2, 3, 4, 5].map(rating => `
                        <i class="fas fa-star review-star" 
                           data-rating="${rating}"
                           onclick="selectRating(${rating})"></i>
                    `).join('')}
                </div>
                <div class="review-rating-text" id="review-rating-text">
                    Clique nas estrelas para avaliar
                </div>
            </div>
            
            <div class="review-comment-section">
                <label class="review-comment-label">Comentário (opcional)</label>
                <textarea 
                    id="review-comment" 
                    class="review-comment-textarea"
                    placeholder="Conte-nos sobre sua experiência..."
                    maxlength="500"></textarea>
            </div>
            
            <div class="review-modal-actions">
                <button class="review-btn review-btn-cancel" onclick="closeReviewModal()">
                    <i class="fas fa-times"></i>
                    Cancelar
                </button>
                <button class="review-btn review-btn-submit" id="review-submit-btn" onclick="submitReview()" disabled>
                    <i class="fas fa-paper-plane"></i>
                    Enviar Avaliação
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Mostrar modal com animação
    setTimeout(() => {
        modal.classList.add('show');
    }, 10);
}

// ===== SELECIONAR RATING =====
function selectRating(rating) {
    reviewState.selectedRating = rating;
    
    // Atualizar estrelas
    const stars = document.querySelectorAll('.review-star');
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
    
    // Atualizar texto
    const texts = [
        '',
        'Muito ruim 😞',
        'Ruim 😕',
        'Regular 😐',
        'Bom 😊',
        'Excelente! 🤩'
    ];
    
    const textEl = document.getElementById('review-rating-text');
    if (textEl) {
        textEl.textContent = texts[rating];
        textEl.style.color = rating >= 4 ? '#10b981' : rating >= 3 ? '#f59e0b' : '#ef4444';
    }
    
    // Habilitar botão de enviar
    const submitBtn = document.getElementById('review-submit-btn');
    if (submitBtn) {
        submitBtn.disabled = false;
    }
}

// ===== ENVIAR AVALIAÇÃO =====
async function submitReview() {
    if (!reviewState.currentAppointment || reviewState.selectedRating === 0) {
        alert('Por favor, selecione uma avaliação');
        return;
    }
    
    const comment = document.getElementById('review-comment')?.value || '';
    
    const submitBtn = document.getElementById('review-submit-btn');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
    }
    
    try {
        const response = await fetch('/api/reviews', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                appointment_id: reviewState.currentAppointment.id,
                barbeiro_id: reviewState.currentAppointment.barbeiro_id,
                rating: reviewState.selectedRating,
                comment: comment
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('✅ Avaliação enviada com sucesso!');
            
            // Fechar modal
            closeReviewModal();
            
            // Mostrar mensagem de sucesso
            showSuccessMessage('Avaliação enviada com sucesso! Obrigado pelo feedback! 🌟');
            
            // Recarregar agendamentos para atualizar a interface
            if (typeof loadClientAppointments === 'function') {
                loadClientAppointments();
            }
            
            // Recarregar histórico se estiver na aba
            if (typeof loadHistoricoData === 'function') {
                loadHistoricoData();
            }
        } else {
            alert('Erro ao enviar avaliação: ' + result.message);
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Enviar Avaliação';
            }
        }
    } catch (error) {
        console.error('❌ Erro ao enviar avaliação:', error);
        alert('Erro ao enviar avaliação. Tente novamente.');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Enviar Avaliação';
        }
    }
}

// ===== FECHAR MODAL =====
function closeReviewModal() {
    const modal = document.getElementById('review-modal-overlay');
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.remove();
        }, 300);
    }
    
    reviewState.currentAppointment = null;
    reviewState.selectedRating = 0;
}

// ===== VERIFICAR SE JÁ AVALIOU =====
async function checkIfReviewed(appointmentId) {
    try {
        const response = await fetch('/api/reviews');
        const result = await response.json();
        
        if (result.success) {
            const review = result.data.find(r => r.appointment_id === appointmentId);
            return review !== undefined;
        }
    } catch (error) {
        console.error('Erro ao verificar avaliação:', error);
    }
    return false;
}

// ===== FORMATAR DATA =====
function formatDate(dateStr) {
    try {
        const date = new Date(dateStr + 'T00:00:00');
        return date.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    } catch {
        return dateStr;
    }
}

// ===== MOSTRAR MENSAGEM DE SUCESSO =====
function showSuccessMessage(message) {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.3);
        z-index: 10001;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 12px;
        animation: slideInRight 0.3s ease;
    `;
    
    toast.innerHTML = `
        <i class="fas fa-check-circle" style="font-size: 20px;"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ===== EXPORTAR FUNÇÕES =====
window.openReviewModal = openReviewModal;
window.closeReviewModal = closeReviewModal;
window.selectRating = selectRating;
window.submitReview = submitReview;
window.checkIfReviewed = checkIfReviewed;

// Adicionar animações CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

console.log('✅ Sistema de avaliações pronto');
