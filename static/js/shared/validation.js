// ===== VALIDAÇÕES DE FORMULÁRIO =====

/**
 * Valida formato de email
 * @param {string} email - Email a ser validado
 * @returns {boolean} - True se válido
 */
function validarEmail(email) {
    const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return pattern.test(email);
}

/**
 * Valida formato de telefone brasileiro
 * @param {string} telefone - Telefone a ser validado
 * @returns {boolean} - True se válido
 */
function validarTelefone(telefone) {
    if (!telefone) return true; // Telefone é opcional
    
    // Remove caracteres não numéricos
    const numeros = telefone.replace(/\D/g, '');
    
    // Deve ter 10 ou 11 dígitos
    return numeros.length === 10 || numeros.length === 11;
}

/**
 * Formata telefone brasileiro
 * @param {string} telefone - Telefone a ser formatado
 * @returns {string} - Telefone formatado
 */
function formatarTelefone(telefone) {
    if (!telefone) return '';
    
    // Remove tudo que não é número
    const numeros = telefone.replace(/\D/g, '');
    
    // Formata conforme o tamanho
    if (numeros.length === 11) {
        // (11) 98765-4321
        return numeros.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
    } else if (numeros.length === 10) {
        // (11) 8765-4321
        return numeros.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
    }
    
    return telefone;
}

/**
 * Aplica máscara de telefone em tempo real
 * @param {HTMLInputElement} input - Campo de input
 */
function aplicarMascaraTelefone(input) {
    input.addEventListener('input', function(e) {
        let valor = e.target.value.replace(/\D/g, '');
        
        // Limita a 11 dígitos
        if (valor.length > 11) {
            valor = valor.substring(0, 11);
        }
        
        // Aplica formatação
        if (valor.length > 10) {
            e.target.value = valor.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
        } else if (valor.length > 6) {
            e.target.value = valor.replace(/(\d{2})(\d{4})(\d{0,4})/, '($1) $2-$3');
        } else if (valor.length > 2) {
            e.target.value = valor.replace(/(\d{2})(\d{0,5})/, '($1) $2');
        } else if (valor.length > 0) {
            e.target.value = valor.replace(/(\d{0,2})/, '($1');
        }
    });
}

/**
 * Valida senha
 * @param {string} senha - Senha a ser validada
 * @returns {object} - {valido: boolean, mensagem: string}
 */
function validarSenha(senha) {
    if (!senha || senha.length < 6) {
        return {
            valido: false,
            mensagem: 'Senha deve ter no mínimo 6 caracteres'
        };
    }
    
    return {
        valido: true,
        mensagem: ''
    };
}

/**
 * Valida nome
 * @param {string} nome - Nome a ser validado
 * @returns {object} - {valido: boolean, mensagem: string}
 */
function validarNome(nome) {
    if (!nome || nome.trim().length < 3) {
        return {
            valido: false,
            mensagem: 'Nome deve ter no mínimo 3 caracteres'
        };
    }
    
    // Verifica se tem pelo menos um espaço (nome e sobrenome)
    if (!nome.includes(' ')) {
        return {
            valido: false,
            mensagem: 'Digite nome e sobrenome'
        };
    }
    
    return {
        valido: true,
        mensagem: ''
    };
}

/**
 * Mostra mensagem de erro no campo
 * @param {HTMLInputElement} input - Campo de input
 * @param {string} mensagem - Mensagem de erro
 */
function mostrarErro(input, mensagem) {
    // Remove erro anterior
    removerErro(input);
    
    // Adiciona classe de erro
    input.classList.add('input-error');
    
    // Cria elemento de mensagem
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = mensagem;
    errorDiv.style.color = '#ef4444';
    errorDiv.style.fontSize = '12px';
    errorDiv.style.marginTop = '4px';
    
    // Insere após o input
    input.parentNode.insertBefore(errorDiv, input.nextSibling);
}

/**
 * Remove mensagem de erro do campo
 * @param {HTMLInputElement} input - Campo de input
 */
function removerErro(input) {
    input.classList.remove('input-error');
    
    const errorMsg = input.parentNode.querySelector('.error-message');
    if (errorMsg) {
        errorMsg.remove();
    }
}

/**
 * Valida formulário de registro
 * @param {HTMLFormElement} form - Formulário
 * @returns {boolean} - True se válido
 */
function validarFormularioRegistro(form) {
    let valido = true;
    
    // Nome
    const nomeInput = form.querySelector('[name="name"]');
    if (nomeInput) {
        const resultadoNome = validarNome(nomeInput.value);
        if (!resultadoNome.valido) {
            mostrarErro(nomeInput, resultadoNome.mensagem);
            valido = false;
        } else {
            removerErro(nomeInput);
        }
    }
    
    // Email
    const emailInput = form.querySelector('[name="email"]');
    if (emailInput) {
        if (!validarEmail(emailInput.value)) {
            mostrarErro(emailInput, 'Email inválido');
            valido = false;
        } else {
            removerErro(emailInput);
        }
    }
    
    // Telefone
    const telefoneInput = form.querySelector('[name="phone"]');
    if (telefoneInput && telefoneInput.value) {
        if (!validarTelefone(telefoneInput.value)) {
            mostrarErro(telefoneInput, 'Telefone inválido. Use formato: (11) 98765-4321');
            valido = false;
        } else {
            removerErro(telefoneInput);
        }
    }
    
    // Senha
    const senhaInput = form.querySelector('[name="password"]');
    if (senhaInput) {
        const resultadoSenha = validarSenha(senhaInput.value);
        if (!resultadoSenha.valido) {
            mostrarErro(senhaInput, resultadoSenha.mensagem);
            valido = false;
        } else {
            removerErro(senhaInput);
        }
    }
    
    // Confirmar senha
    const confirmarSenhaInput = form.querySelector('[name="confirmPassword"]');
    if (confirmarSenhaInput && senhaInput) {
        if (confirmarSenhaInput.value !== senhaInput.value) {
            mostrarErro(confirmarSenhaInput, 'As senhas não coincidem');
            valido = false;
        } else {
            removerErro(confirmarSenhaInput);
        }
    }
    
    return valido;
}

/**
 * Inicializa validações em tempo real
 */
function inicializarValidacoes() {
    // Validação de email em tempo real
    document.querySelectorAll('input[type="email"]').forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value && !validarEmail(this.value)) {
                mostrarErro(this, 'Email inválido');
            } else {
                removerErro(this);
            }
        });
    });
    
    // Máscara de telefone
    document.querySelectorAll('input[name="phone"], input[type="tel"]').forEach(input => {
        aplicarMascaraTelefone(input);
        
        input.addEventListener('blur', function() {
            if (this.value && !validarTelefone(this.value)) {
                mostrarErro(this, 'Telefone inválido. Use formato: (11) 98765-4321');
            } else {
                removerErro(this);
            }
        });
    });
    
    // Validação de senha em tempo real
    document.querySelectorAll('input[type="password"][name="password"]').forEach(input => {
        input.addEventListener('blur', function() {
            const resultado = validarSenha(this.value);
            if (!resultado.valido) {
                mostrarErro(this, resultado.mensagem);
            } else {
                removerErro(this);
            }
        });
    });
    
    // Validação de nome em tempo real
    document.querySelectorAll('input[name="name"]').forEach(input => {
        input.addEventListener('blur', function() {
            const resultado = validarNome(this.value);
            if (!resultado.valido) {
                mostrarErro(this, resultado.mensagem);
            } else {
                removerErro(this);
            }
        });
    });
}

// Inicializar quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inicializarValidacoes);
} else {
    inicializarValidacoes();
}

// Exportar funções
window.validarEmail = validarEmail;
window.validarTelefone = validarTelefone;
window.formatarTelefone = formatarTelefone;
window.validarSenha = validarSenha;
window.validarNome = validarNome;
window.validarFormularioRegistro = validarFormularioRegistro;
window.mostrarErro = mostrarErro;
window.removerErro = removerErro;
