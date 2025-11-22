/**
 * Sistema de Notificações Toast - S.O.S Pets
 * 
 * Sistema centralizado para exibir mensagens de erro, sucesso,
 * aviso e informação de forma amigável e consistente.
 * 
 * Uso:
 *   showToast('Mensagem de sucesso!', 'success');
 *   showToast('Erro ao processar!', 'error');
 *   showToast('Atenção!', 'warning');
 *   showToast('Informação', 'info');
 */

// Container para as notificações
let toastContainer = null;

/**
 * Inicializa o container de toasts
 */
function initToastContainer() {
  if (toastContainer) return;
  
  toastContainer = document.createElement('div');
  toastContainer.id = 'toast-container';
  toastContainer.className = 'toast-container';
  toastContainer.setAttribute('role', 'region');
  toastContainer.setAttribute('aria-label', 'Notificações');
  document.body.appendChild(toastContainer);
}

/**
 * Exibe uma notificação toast
 * 
 * @param {string} message - Mensagem a ser exibida
 * @param {string} type - Tipo: 'success', 'error', 'warning', 'info'
 * @param {number} duration - Duração em ms (0 = infinito)
 */
function showToast(message, type = 'info', duration = 5000) {
  initToastContainer();
  
  const toast = document.createElement('div');
  toast.className = `toast toast-${type} toast-enter`;
  toast.setAttribute('role', 'alert');
  toast.setAttribute('aria-live', 'assertive');
  
  const icon = getToastIcon(type);
  const closeBtn = document.createElement('button');
  closeBtn.className = 'toast-close';
  closeBtn.innerHTML = '&times;';
  closeBtn.setAttribute('aria-label', 'Fechar notificação');
  closeBtn.onclick = () => removeToast(toast);
  
  toast.innerHTML = `
    <div class="toast-icon">${icon}</div>
    <div class="toast-content">
      <div class="toast-message">${sanitizeHTML(message)}</div>
    </div>
  `;
  toast.appendChild(closeBtn);
  
  toastContainer.appendChild(toast);
  
  // Animação de entrada
  setTimeout(() => toast.classList.add('toast-show'), 10);
  
  // Remove automaticamente após duração
  if (duration > 0) {
    setTimeout(() => removeToast(toast), duration);
  }
  
  return toast;
}

/**
 * Remove um toast com animação
 */
function removeToast(toast) {
  if (!toast || !toast.parentElement) return;
  
  toast.classList.remove('toast-show');
  toast.classList.add('toast-exit');
  
  setTimeout(() => {
    if (toast.parentElement) {
      toast.parentElement.removeChild(toast);
    }
  }, 300);
}

/**
 * Retorna o ícone apropriado para cada tipo
 */
function getToastIcon(type) {
  const icons = {
    success: '<i class="fas fa-check-circle"></i>',
    error: '<i class="fas fa-exclamation-circle"></i>',
    warning: '<i class="fas fa-exclamation-triangle"></i>',
    info: '<i class="fas fa-info-circle"></i>'
  };
  return icons[type] || icons.info;
}

/**
 * Sanitiza HTML para prevenir XSS
 */
function sanitizeHTML(str) {
  const temp = document.createElement('div');
  temp.textContent = str;
  return temp.innerHTML;
}

/**
 * Mensagens de erro amigáveis para códigos HTTP
 */
const errorMessages = {
  // Erros de autenticação (400)
  'Invalid credentials': 'Usuário ou senha incorretos. Tente novamente.',
  'invalid_credentials': 'Usuário ou senha incorretos. Tente novamente.',
  'Incorrect authentication credentials': 'Usuário ou senha incorretos.',
  
  // Erros de validação (400)
  'This field may not be blank': 'Este campo não pode ficar em branco.',
  'This field is required': 'Este campo é obrigatório.',
  'Enter a valid email address': 'Digite um e-mail válido.',
  'Ensure this field has no more than': 'Este campo excede o tamanho máximo.',
  'Email already exists': 'Este e-mail já está cadastrado.',
  'email already exists': 'Este e-mail já está cadastrado.',
  'Username already exists': 'Este nome de usuário já está em uso.',
  'username already exists': 'Este nome de usuário já está em uso.',
  
  // Erros de permissão (403)
  'Permission denied': 'Você não tem permissão para realizar esta ação.',
  'You do not have permission': 'Você não tem permissão para acessar este recurso.',
  'Authentication credentials were not provided': 'Você precisa estar logado para continuar.',
  
  // Erros de não encontrado (404)
  'Not found': 'O recurso solicitado não foi encontrado.',
  'Page not found': 'Página não encontrada.',
  
  // Erros de servidor (500)
  'Internal server error': 'Erro no servidor. Tente novamente mais tarde.',
  'Server error': 'Erro no servidor. Nossa equipe foi notificada.',
  
  // Erros de conexão
  'Network error': 'Erro de conexão. Verifique sua internet.',
  'Failed to fetch': 'Não foi possível conectar ao servidor. Verifique sua conexão.',
  'NetworkError': 'Erro de rede. Verifique sua conexão com a internet.',
  
  // Erros específicos do sistema
  'Token has expired': 'Sua sessão expirou. Faça login novamente.',
  'Invalid token': 'Sessão inválida. Faça login novamente.',
  'File too large': 'Arquivo muito grande. Tamanho máximo: 5MB.',
  'Invalid file type': 'Tipo de arquivo não permitido.',
  'Password too common': 'Senha muito comum. Escolha uma senha mais segura.',
  'Password is too short': 'Senha muito curta. Use no mínimo 8 caracteres.',
  'Passwords do not match': 'As senhas não conferem.'
};

/**
 * Traduz mensagens de erro técnicas para linguagem amigável
 */
function getFriendlyErrorMessage(error) {
  if (!error) return 'Erro desconhecido. Tente novamente.';
  
  // Se já é uma mensagem amigável, retorna
  if (typeof error === 'string') {
    const lowerError = error.toLowerCase();
    for (const [key, value] of Object.entries(errorMessages)) {
      if (lowerError.includes(key.toLowerCase())) {
        return value;
      }
    }
    return error;
  }
  
  // Se é um objeto de erro da API
  if (error.detail) {
    return getFriendlyErrorMessage(error.detail);
  }
  
  // Se é um objeto com múltiplos campos
  if (typeof error === 'object') {
    const messages = [];
    for (const [field, errors] of Object.entries(error)) {
      if (Array.isArray(errors)) {
        errors.forEach(err => messages.push(getFriendlyErrorMessage(err)));
      } else {
        messages.push(getFriendlyErrorMessage(errors));
      }
    }
    return messages.join(' ');
  }
  
  return 'Erro ao processar sua solicitação. Tente novamente.';
}

/**
 * Manipula erros de requisições fetch de forma amigável
 */
async function handleFetchError(response) {
  let errorData;
  
  try {
    errorData = await response.json();
  } catch {
    errorData = { detail: 'Erro ao processar resposta do servidor.' };
  }
  
  // Mensagens específicas por código HTTP
  const statusMessages = {
    400: 'Dados inválidos. Verifique as informações e tente novamente.',
    401: 'Sessão expirada. Faça login novamente.',
    403: 'Você não tem permissão para realizar esta ação.',
    404: 'Recurso não encontrado.',
    409: 'Conflito detectado. O recurso já existe.',
    422: 'Dados inválidos. Verifique as informações.',
    429: 'Muitas tentativas. Aguarde alguns minutos.',
    500: 'Erro no servidor. Tente novamente mais tarde.',
    502: 'Servidor temporariamente indisponível.',
    503: 'Serviço em manutenção. Tente mais tarde.'
  };
  
  const message = getFriendlyErrorMessage(errorData) || 
                  statusMessages[response.status] || 
                  'Erro ao processar sua solicitação.';
  
  showToast(message, 'error');
  return message;
}

/**
 * Wrapper para fetch com tratamento automático de erros
 */
async function fetchWithErrorHandling(url, options = {}) {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      await handleFetchError(response);
      throw new Error('Request failed');
    }
    
    return response;
  } catch (error) {
    if (error.message === 'Request failed') {
      throw error;
    }
    
    // Erro de rede
    showToast('Erro de conexão. Verifique sua internet.', 'error');
    throw error;
  }
}

/**
 * Valida formulário e exibe erros amigáveis
 */
function validateForm(formElement) {
  const inputs = formElement.querySelectorAll('input[required], textarea[required], select[required]');
  let isValid = true;
  
  inputs.forEach(input => {
    // Remove erros anteriores
    input.classList.remove('input-error');
    const existingError = input.parentElement.querySelector('.field-error');
    if (existingError) existingError.remove();
    
    // Valida campo vazio
    if (!input.value.trim()) {
      showFieldError(input, 'Este campo é obrigatório');
      isValid = false;
      return;
    }
    
    // Valida email
    if (input.type === 'email' && !isValidEmail(input.value)) {
      showFieldError(input, 'Digite um e-mail válido');
      isValid = false;
      return;
    }
    
    // Valida telefone
    if (input.type === 'tel' && !isValidPhone(input.value)) {
      showFieldError(input, 'Digite um telefone válido');
      isValid = false;
      return;
    }
    
    // Valida senha (mínimo 6 caracteres)
    if (input.type === 'password' && input.value.length < 6) {
      showFieldError(input, 'A senha deve ter no mínimo 6 caracteres');
      isValid = false;
      return;
    }
  });
  
  return isValid;
}

/**
 * Exibe erro em campo específico
 */
function showFieldError(input, message) {
  input.classList.add('input-error');
  
  const errorDiv = document.createElement('div');
  errorDiv.className = 'field-error';
  errorDiv.textContent = message;
  errorDiv.setAttribute('role', 'alert');
  
  input.parentElement.appendChild(errorDiv);
}

/**
 * Valida formato de email
 */
function isValidEmail(email) {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}

/**
 * Valida formato de telefone brasileiro
 */
function isValidPhone(phone) {
  const cleaned = phone.replace(/\D/g, '');
  return cleaned.length >= 10 && cleaned.length <= 11;
}

/**
 * Exibe loading em botão
 */
function setButtonLoading(button, loading = true) {
  if (loading) {
    button.dataset.originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Aguarde...';
    button.classList.add('btn-loading');
  } else {
    button.disabled = false;
    button.innerHTML = button.dataset.originalText || button.innerHTML;
    button.classList.remove('btn-loading');
  }
}

/**
 * Atalhos para tipos comuns de toast
 */
const toast = {
  success: (msg, duration) => showToast(msg, 'success', duration),
  error: (msg, duration) => showToast(msg, 'error', duration),
  warning: (msg, duration) => showToast(msg, 'warning', duration),
  info: (msg, duration) => showToast(msg, 'info', duration)
};

// Exporta funções globalmente
window.showToast = showToast;
window.toast = toast;
window.handleFetchError = handleFetchError;
window.fetchWithErrorHandling = fetchWithErrorHandling;
window.getFriendlyErrorMessage = getFriendlyErrorMessage;
window.validateForm = validateForm;
window.showFieldError = showFieldError;
window.setButtonLoading = setButtonLoading;
window.isValidEmail = isValidEmail;
window.isValidPhone = isValidPhone;
