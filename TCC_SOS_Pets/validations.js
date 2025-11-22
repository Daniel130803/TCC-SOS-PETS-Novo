/**
 * ============================================
 * VALIDATIONS.JS - Sistema de Validação Frontend
 * ============================================
 * 
 * Funções de validação robustas para formulários do S.O.S Pets.
 * Integra com sistema Toast para feedback visual.
 * 
 * @author Sistema S.O.S Pets
 * @version 1.0.0
 */

// ============================================
// VALIDAÇÕES DE FORMATO
// ============================================

/**
 * Valida formato de email
 * @param {string} email - Email a validar
 * @returns {{valid: boolean, message: string}}
 */
function validateEmail(email) {
    if (!email || email.trim() === '') {
        return { valid: false, message: 'Email é obrigatório' };
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        return { valid: false, message: 'Email inválido. Use o formato: nome@exemplo.com' };
    }

    if (email.length > 254) {
        return { valid: false, message: 'Email muito longo (máximo 254 caracteres)' };
    }

    return { valid: true, message: '' };
}

/**
 * Valida formato de telefone brasileiro
 * Aceita: (11) 99999-9999, (11) 9999-9999, 11999999999
 * @param {string} telefone - Telefone a validar
 * @returns {{valid: boolean, message: string}}
 */
function validateTelefone(telefone) {
    if (!telefone || telefone.trim() === '') {
        return { valid: false, message: 'Telefone é obrigatório' };
    }

    // Remove caracteres não numéricos
    const apenasNumeros = telefone.replace(/\D/g, '');

    if (apenasNumeros.length < 10 || apenasNumeros.length > 11) {
        return { 
            valid: false, 
            message: 'Telefone deve ter 10 ou 11 dígitos. Formato: (11) 99999-9999' 
        };
    }

    // Valida DDD (códigos válidos no Brasil)
    const ddd = parseInt(apenasNumeros.substring(0, 2));
    const dddValidos = [
        11, 12, 13, 14, 15, 16, 17, 18, 19, // SP
        21, 22, 24, // RJ
        27, 28, // ES
        31, 32, 33, 34, 35, 37, 38, // MG
        41, 42, 43, 44, 45, 46, // PR
        47, 48, 49, // SC
        51, 53, 54, 55, // RS
        61, // DF
        62, 64, // GO
        63, // TO
        65, 66, // MT
        67, // MS
        68, // AC
        69, // RO
        71, 73, 74, 75, 77, // BA
        79, // SE
        81, 87, // PE
        82, // AL
        83, // PB
        84, // RN
        85, 88, // CE
        86, 89, // PI
        91, 93, 94, // PA
        92, 97, // AM
        95, // RR
        96, // AP
        98, 99  // MA
    ];

    if (!dddValidos.includes(ddd)) {
        return { valid: false, message: 'DDD inválido' };
    }

    return { valid: true, message: '' };
}

/**
 * Valida CPF
 * @param {string} cpf - CPF a validar
 * @returns {{valid: boolean, message: string}}
 */
function validateCPF(cpf) {
    if (!cpf || cpf.trim() === '') {
        return { valid: false, message: 'CPF é obrigatório' };
    }

    // Remove caracteres não numéricos
    const cpfLimpo = cpf.replace(/\D/g, '');

    if (cpfLimpo.length !== 11) {
        return { valid: false, message: 'CPF deve ter 11 dígitos' };
    }

    // Verifica se todos os dígitos são iguais (CPF inválido)
    if (/^(\d)\1{10}$/.test(cpfLimpo)) {
        return { valid: false, message: 'CPF inválido' };
    }

    // Valida dígitos verificadores
    let soma = 0;
    let resto;

    for (let i = 1; i <= 9; i++) {
        soma += parseInt(cpfLimpo.substring(i - 1, i)) * (11 - i);
    }
    resto = (soma * 10) % 11;
    if (resto === 10 || resto === 11) resto = 0;
    if (resto !== parseInt(cpfLimpo.substring(9, 10))) {
        return { valid: false, message: 'CPF com dígitos verificadores inválidos' };
    }

    soma = 0;
    for (let i = 1; i <= 10; i++) {
        soma += parseInt(cpfLimpo.substring(i - 1, i)) * (12 - i);
    }
    resto = (soma * 10) % 11;
    if (resto === 10 || resto === 11) resto = 0;
    if (resto !== parseInt(cpfLimpo.substring(10, 11))) {
        return { valid: false, message: 'CPF com dígitos verificadores inválidos' };
    }

    return { valid: true, message: '' };
}

/**
 * Valida senha
 * @param {string} senha - Senha a validar
 * @param {number} minLength - Tamanho mínimo (padrão: 6)
 * @returns {{valid: boolean, message: string}}
 */
function validateSenha(senha, minLength = 6) {
    if (!senha || senha.trim() === '') {
        return { valid: false, message: 'Senha é obrigatória' };
    }

    if (senha.length < minLength) {
        return { 
            valid: false, 
            message: `Senha deve ter pelo menos ${minLength} caracteres` 
        };
    }

    if (senha.length > 128) {
        return { valid: false, message: 'Senha muito longa (máximo 128 caracteres)' };
    }

    if (/^\d+$/.test(senha)) {
        return { valid: false, message: 'Senha não pode conter apenas números' };
    }

    return { valid: true, message: '' };
}

/**
 * Valida confirmação de senha
 * @param {string} senha - Senha original
 * @param {string} confirmacao - Confirmação da senha
 * @returns {{valid: boolean, message: string}}
 */
function validateSenhaConfirmacao(senha, confirmacao) {
    if (!confirmacao || confirmacao.trim() === '') {
        return { valid: false, message: 'Confirmação de senha é obrigatória' };
    }

    if (senha !== confirmacao) {
        return { valid: false, message: 'As senhas não coincidem' };
    }

    return { valid: true, message: '' };
}

// ============================================
// VALIDAÇÕES DE CONTEÚDO
// ============================================

/**
 * Valida campo de texto obrigatório
 * @param {string} texto - Texto a validar
 * @param {string} nomeCampo - Nome do campo para mensagem
 * @param {number} minLength - Tamanho mínimo
 * @param {number} maxLength - Tamanho máximo
 * @returns {{valid: boolean, message: string}}
 */
function validateTexto(texto, nomeCampo, minLength = 3, maxLength = 255) {
    if (!texto || texto.trim() === '') {
        return { valid: false, message: `${nomeCampo} é obrigatório` };
    }

    const textoLimpo = texto.trim();

    if (textoLimpo.length < minLength) {
        return { 
            valid: false, 
            message: `${nomeCampo} deve ter pelo menos ${minLength} caracteres` 
        };
    }

    if (textoLimpo.length > maxLength) {
        return { 
            valid: false, 
            message: `${nomeCampo} deve ter no máximo ${maxLength} caracteres` 
        };
    }

    return { valid: true, message: '' };
}

/**
 * Valida nome completo
 * @param {string} nome - Nome a validar
 * @returns {{valid: boolean, message: string}}
 */
function validateNomeCompleto(nome) {
    if (!nome || nome.trim() === '') {
        return { valid: false, message: 'Nome completo é obrigatório' };
    }

    const nomeLimpo = nome.trim();

    if (nomeLimpo.length < 3) {
        return { valid: false, message: 'Nome deve ter pelo menos 3 caracteres' };
    }

    if (nomeLimpo.length > 100) {
        return { valid: false, message: 'Nome muito longo (máximo 100 caracteres)' };
    }

    // Valida se tem pelo menos um espaço (nome e sobrenome)
    if (!/ /.test(nomeLimpo)) {
        return { valid: false, message: 'Digite nome e sobrenome' };
    }

    return { valid: true, message: '' };
}

/**
 * Valida idade
 * @param {number|string} idade - Idade a validar
 * @param {number} min - Idade mínima (padrão: 0)
 * @param {number} max - Idade máxima (padrão: 150)
 * @returns {{valid: boolean, message: string}}
 */
function validateIdade(idade, min = 0, max = 150) {
    const idadeNum = parseInt(idade);

    if (isNaN(idadeNum)) {
        return { valid: false, message: 'Idade deve ser um número' };
    }

    if (idadeNum < min) {
        return { valid: false, message: `Idade mínima: ${min} anos` };
    }

    if (idadeNum > max) {
        return { valid: false, message: `Idade máxima: ${max} anos` };
    }

    return { valid: true, message: '' };
}

// ============================================
// VALIDAÇÕES DE ARQUIVOS
// ============================================

/**
 * Valida arquivo de imagem
 * @param {File} arquivo - Arquivo a validar
 * @param {number} maxSizeMB - Tamanho máximo em MB (padrão: 5)
 * @returns {{valid: boolean, message: string}}
 */
function validateImagem(arquivo, maxSizeMB = 5) {
    if (!arquivo) {
        return { valid: false, message: 'Nenhuma imagem selecionada' };
    }

    // Valida tipo
    const tiposPermitidos = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!tiposPermitidos.includes(arquivo.type)) {
        return { 
            valid: false, 
            message: 'Apenas imagens JPG, PNG ou WebP são permitidas' 
        };
    }

    // Valida tamanho
    const tamanhoMB = arquivo.size / (1024 * 1024);
    if (tamanhoMB > maxSizeMB) {
        return { 
            valid: false, 
            message: `Imagem muito grande (${tamanhoMB.toFixed(1)}MB). Máximo: ${maxSizeMB}MB` 
        };
    }

    return { valid: true, message: '' };
}

/**
 * Valida arquivo de vídeo
 * @param {File} arquivo - Arquivo a validar
 * @param {number} maxSizeMB - Tamanho máximo em MB (padrão: 20)
 * @returns {{valid: boolean, message: string}}
 */
function validateVideo(arquivo, maxSizeMB = 20) {
    if (!arquivo) {
        return { valid: false, message: 'Nenhum vídeo selecionado' };
    }

    // Valida tipo
    const tiposPermitidos = ['video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/webm'];
    if (!tiposPermitidos.includes(arquivo.type)) {
        return { 
            valid: false, 
            message: 'Apenas vídeos MP4, AVI, MOV, WMV ou WebM são permitidos' 
        };
    }

    // Valida tamanho
    const tamanhoMB = arquivo.size / (1024 * 1024);
    if (tamanhoMB > maxSizeMB) {
        return { 
            valid: false, 
            message: `Vídeo muito grande (${tamanhoMB.toFixed(1)}MB). Máximo: ${maxSizeMB}MB` 
        };
    }

    return { valid: true, message: '' };
}

// ============================================
// VALIDAÇÃO DE FORMULÁRIOS COMPLETOS
// ============================================

/**
 * Valida formulário completo e mostra erros com Toast
 * @param {Object} validacoes - Objeto com validações {campo: resultado}
 * @returns {boolean} true se válido, false se inválido
 * 
 * @example
 * const valido = validateForm({
 *     email: validateEmail(email),
 *     senha: validateSenha(senha),
 *     nome: validateNomeCompleto(nome)
 * });
 */
function validateForm(validacoes) {
    let primeiroErro = null;
    let todosValidos = true;

    for (const [campo, resultado] of Object.entries(validacoes)) {
        if (!resultado.valid) {
            todosValidos = false;
            if (!primeiroErro) {
                primeiroErro = { campo, mensagem: resultado.message };
            }
        }
    }

    // Mostra apenas o primeiro erro com Toast
    if (primeiroErro) {
        if (typeof toast !== 'undefined') {
            toast.error(primeiroErro.mensagem);
        } else {
            alert(primeiroErro.mensagem);
        }
        return false;
    }

    return true;
}

/**
 * Adiciona validação em tempo real a um campo
 * @param {string} inputId - ID do input
 * @param {Function} validatorFunc - Função de validação
 */
function addRealtimeValidation(inputId, validatorFunc) {
    const input = document.getElementById(inputId);
    if (!input) return;

    input.addEventListener('blur', function() {
        const resultado = validatorFunc(this.value);
        
        // Remove classes anteriores
        this.classList.remove('is-valid', 'is-invalid');
        
        // Adiciona classe apropriada
        if (resultado.valid) {
            this.classList.add('is-valid');
        } else if (this.value.trim() !== '') {
            this.classList.add('is-invalid');
            
            // Mostra mensagem de erro
            let feedbackDiv = this.nextElementSibling;
            if (!feedbackDiv || !feedbackDiv.classList.contains('invalid-feedback')) {
                feedbackDiv = document.createElement('div');
                feedbackDiv.className = 'invalid-feedback';
                this.parentNode.insertBefore(feedbackDiv, this.nextSibling);
            }
            feedbackDiv.textContent = resultado.message;
        }
    });

    // Remove erro ao começar a digitar
    input.addEventListener('input', function() {
        if (this.classList.contains('is-invalid')) {
            this.classList.remove('is-invalid');
            const feedbackDiv = this.nextElementSibling;
            if (feedbackDiv && feedbackDiv.classList.contains('invalid-feedback')) {
                feedbackDiv.textContent = '';
            }
        }
    });
}

// ============================================
// MÁSCARAS DE FORMATAÇÃO
// ============================================

/**
 * Aplica máscara de telefone
 * @param {string} valor - Valor a formatar
 * @returns {string} Valor formatado
 */
function maskTelefone(valor) {
    let v = valor.replace(/\D/g, '');
    v = v.replace(/^(\d{2})(\d)/g, '($1) $2');
    v = v.replace(/(\d)(\d{4})$/, '$1-$2');
    return v;
}

/**
 * Aplica máscara de CPF
 * @param {string} valor - Valor a formatar
 * @returns {string} Valor formatado
 */
function maskCPF(valor) {
    let v = valor.replace(/\D/g, '');
    v = v.replace(/(\d{3})(\d)/, '$1.$2');
    v = v.replace(/(\d{3})(\d)/, '$1.$2');
    v = v.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
    return v;
}

/**
 * Aplica máscara a um input
 * @param {string} inputId - ID do input
 * @param {Function} maskFunc - Função de máscara
 */
function applyMask(inputId, maskFunc) {
    const input = document.getElementById(inputId);
    if (!input) return;

    input.addEventListener('input', function(e) {
        const start = this.selectionStart;
        const end = this.selectionEnd;
        this.value = maskFunc(this.value);
        this.setSelectionRange(start, end);
    });
}

// ============================================
// SANITIZAÇÃO BÁSICA
// ============================================

/**
 * Remove caracteres perigosos (XSS básico)
 * @param {string} texto - Texto a sanitizar
 * @returns {string} Texto sanitizado
 */
function sanitizeInput(texto) {
    if (!texto) return '';
    
    // Remove tags HTML
    let sanitizado = texto.replace(/<[^>]*>/g, '');
    
    // Remove scripts
    sanitizado = sanitizado.replace(/<script[^>]*>.*?<\/script>/gi, '');
    
    // Escapa caracteres especiais HTML
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        "/": '&#x2F;',
    };
    const reg = /[&<>"'/]/ig;
    return sanitizado.replace(reg, (match) => (map[match]));
}

// Exporta para uso global
if (typeof window !== 'undefined') {
    window.validateEmail = validateEmail;
    window.validateTelefone = validateTelefone;
    window.validateCPF = validateCPF;
    window.validateSenha = validateSenha;
    window.validateSenhaConfirmacao = validateSenhaConfirmacao;
    window.validateTexto = validateTexto;
    window.validateNomeCompleto = validateNomeCompleto;
    window.validateIdade = validateIdade;
    window.validateImagem = validateImagem;
    window.validateVideo = validateVideo;
    window.validateForm = validateForm;
    window.addRealtimeValidation = addRealtimeValidation;
    window.maskTelefone = maskTelefone;
    window.maskCPF = maskCPF;
    window.applyMask = applyMask;
    window.sanitizeInput = sanitizeInput;
}
