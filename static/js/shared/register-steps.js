/**
 * Navegação entre etapas do cadastro progressivo
 */

let registerCurrentStep = {
    'cliente': 1,
    'barbeiro': 1
};

/**
 * Próxima etapa do cadastro
 */
function nextRegisterStep(tipo) {
    const form = document.getElementById(`register-${tipo}-form`);
    const currentStep = registerCurrentStep[tipo];
    const currentStepEl = form.querySelector(`.register-step[data-step="${currentStep}"]`);
    
    // Validar campos da etapa atual
    const inputs = currentStepEl.querySelectorAll('input[required], select[required]');
    let valid = true;
    
    inputs.forEach(input => {
        if (!input.checkValidity()) {
            input.reportValidity();
            valid = false;
        }
    });
    
    if (!valid) return;
    
    // Esconder etapa atual
    currentStepEl.style.display = 'none';
    
    // Avançar etapa
    registerCurrentStep[tipo]++;
    const nextStep = registerCurrentStep[tipo];
    
    // Mostrar próxima etapa
    const nextStepEl = form.querySelector(`.register-step[data-step="${nextStep}"]`);
    if (nextStepEl) {
        nextStepEl.style.display = 'block';
    }
    
    // Atualizar progress
    updateRegisterProgress(tipo);
}

/**
 * Etapa anterior do cadastro
 */
function prevRegisterStep(tipo) {
    const form = document.getElementById(`register-${tipo}-form`);
    const currentStep = registerCurrentStep[tipo];
    const currentStepEl = form.querySelector(`.register-step[data-step="${currentStep}"]`);
    
    // Esconder etapa atual
    currentStepEl.style.display = 'none';
    
    // Voltar etapa
    registerCurrentStep[tipo]--;
    const prevStep = registerCurrentStep[tipo];
    
    // Mostrar etapa anterior
    const prevStepEl = form.querySelector(`.register-step[data-step="${prevStep}"]`);
    if (prevStepEl) {
        prevStepEl.style.display = 'block';
    }
    
    // Atualizar progress
    updateRegisterProgress(tipo);
}

/**
 * Atualizar barra de progresso
 */
function updateRegisterProgress(tipo) {
    const container = document.getElementById(`register-${tipo}`);
    if (!container) return;
    
    const currentStep = registerCurrentStep[tipo];
    const steps = container.querySelectorAll('.progress-step');
    
    steps.forEach((step, index) => {
        const stepNum = index + 1;
        step.classList.remove('active', 'completed');
        
        if (stepNum < currentStep) {
            step.classList.add('completed');
        } else if (stepNum === currentStep) {
            step.classList.add('active');
        }
    });
}

/**
 * Resetar cadastro ao voltar
 */
function resetRegisterSteps(tipo) {
    registerCurrentStep[tipo] = 1;
    
    const form = document.getElementById(`register-${tipo}-form`);
    if (!form) return;
    
    // Mostrar apenas primeira etapa
    const steps = form.querySelectorAll('.register-step');
    steps.forEach((step, index) => {
        step.style.display = index === 0 ? 'block' : 'none';
    });
    
    // Resetar progress
    updateRegisterProgress(tipo);
}

// Exportar funções
window.nextRegisterStep = nextRegisterStep;
window.prevRegisterStep = prevRegisterStep;
window.resetRegisterSteps = resetRegisterSteps;

console.log('✅ Módulo de cadastro progressivo carregado');
