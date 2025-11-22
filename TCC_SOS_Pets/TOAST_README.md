# 🎨 Sistema de Mensagens de Erro Amigáveis - S.O.S Pets

## 📋 Visão Geral

Sistema completo de notificações **Toast** para exibir mensagens de erro, sucesso, aviso e informação de forma amigável e consistente em todo o frontend do S.O.S Pets.

## ✨ Características

- ✅ **Mensagens Amigáveis:** Traduz automaticamente erros técnicos da API
- ✅ **4 Tipos de Notificação:** Success, Error, Warning, Info
- ✅ **Animações Suaves:** Entrada/saída com CSS transitions
- ✅ **Responsivo:** Adaptado para desktop e mobile
- ✅ **Acessível:** ARIA labels e atributos de acessibilidade
- ✅ **Validação de Formulários:** Validação integrada com feedback visual
- ✅ **Loading States:** Estados de loading para botões
- ✅ **Prevenção de XSS:** Sanitização automática de mensagens

## 🚀 Como Usar

### 1. Incluir o Script

Adicione **ANTES** de outros scripts JavaScript:

```html
<script src="toast-notifications.js"></script>
<script src="login.js"></script>
```

### 2. Exibir Notificações

```javascript
// Sucesso
toast.success('Animal cadastrado com sucesso!');

// Erro
toast.error('Erro ao processar sua solicitação!');

// Aviso
toast.warning('Preencha todos os campos obrigatórios!');

// Informação
toast.info('Você tem 3 novas notificações!');
```

### 3. Com Duração Personalizada

```javascript
// Toast de 10 segundos
showToast('Mensagem importante', 'success', 10000);

// Toast permanente (precisa fechar manualmente)
showToast('Atenção crítica!', 'warning', 0);
```

## 📝 Funcionalidades Principais

### 1. Tradução Automática de Erros

O sistema traduz automaticamente mensagens técnicas da API:

| Erro da API | Mensagem Amigável |
|-------------|-------------------|
| `Invalid credentials` | Usuário ou senha incorretos. Tente novamente. |
| `This field may not be blank` | Este campo não pode ficar em branco. |
| `Email already exists` | Este e-mail já está cadastrado. |
| `Permission denied` | Você não tem permissão para realizar esta ação. |
| `Failed to fetch` | Erro de conexão. Verifique sua internet. |

**Exemplo:**

```javascript
try {
  const response = await fetch('/api/auth/token/', {
    method: 'POST',
    body: JSON.stringify({ username, password })
  });
  
  const data = await response.json();
  
  if (!response.ok) {
    const friendlyMessage = getFriendlyErrorMessage(data);
    toast.error(friendlyMessage);
  }
} catch (error) {
  toast.error('Erro de conexão. Verifique sua internet.');
}
```

### 2. Validação de Formulários

```javascript
const form = document.getElementById('meu-form');

form.addEventListener('submit', (e) => {
  e.preventDefault();
  
  // Valida formulário automaticamente
  if (!validateForm(form)) {
    toast.error('Corrija os erros no formulário');
    return;
  }
  
  // Continua o processamento...
});
```

**Validações Incluídas:**
- ✅ Campos obrigatórios
- ✅ Formato de e-mail
- ✅ Formato de telefone brasileiro
- ✅ Tamanho mínimo de senha (6 caracteres)

### 3. Loading em Botões

```javascript
const btn = document.querySelector('button[type="submit"]');

// Ativa loading
setButtonLoading(btn, true);

try {
  // Operação async
  await fetch('/api/...');
  toast.success('Operação concluída!');
} finally {
  // Desativa loading
  setButtonLoading(btn, false);
}
```

### 4. Tratamento de Erros HTTP

```javascript
async function salvarAnimal(data) {
  try {
    const response = await fetchWithErrorHandling('/api/animais/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    
    toast.success('Animal cadastrado com sucesso!');
    return await response.json();
  } catch (error) {
    // Erro já foi tratado e exibido automaticamente
    return null;
  }
}
```

## 🎯 Mensagens de Erro por Código HTTP

| Código | Mensagem Amigável |
|--------|-------------------|
| 400 | Dados inválidos. Verifique as informações e tente novamente. |
| 401 | Sessão expirada. Faça login novamente. |
| 403 | Você não tem permissão para realizar esta ação. |
| 404 | Recurso não encontrado. |
| 409 | Conflito detectado. O recurso já existe. |
| 429 | Muitas tentativas. Aguarde alguns minutos. |
| 500 | Erro no servidor. Tente novamente mais tarde. |
| 503 | Serviço em manutenção. Tente mais tarde. |

## 📦 API Completa

### Funções Principais

```javascript
// Exibir toast
showToast(message, type, duration)
// message: string - Mensagem a exibir
// type: 'success' | 'error' | 'warning' | 'info'
// duration: number - Duração em ms (0 = infinito)

// Atalhos
toast.success(message, duration?)
toast.error(message, duration?)
toast.warning(message, duration?)
toast.info(message, duration?)

// Traduzir mensagem de erro
getFriendlyErrorMessage(error)

// Tratar erro de fetch
handleFetchError(response)

// Fetch com tratamento automático
fetchWithErrorHandling(url, options)

// Validar formulário
validateForm(formElement)

// Exibir erro em campo
showFieldError(input, message)

// Loading em botão
setButtonLoading(button, loading)

// Validações
isValidEmail(email)
isValidPhone(phone)
```

## 🎨 Personalização via CSS

As classes CSS podem ser customizadas:

```css
/* Container */
.toast-container { }

/* Toast individual */
.toast { }
.toast-show { }
.toast-exit { }

/* Tipos */
.toast-success { }
.toast-error { }
.toast-warning { }
.toast-info { }

/* Componentes */
.toast-icon { }
.toast-message { }
.toast-close { }

/* Validação */
.input-error { }
.field-error { }

/* Loading */
.btn-loading { }
```

## 📱 Responsividade

O sistema é totalmente responsivo:

- **Desktop:** Toasts no canto superior direito
- **Mobile:** Toasts ocupam largura total com margens laterais

## ♿ Acessibilidade

- Atributos ARIA (role, aria-live, aria-label)
- Navegação por teclado
- Suporte a leitores de tela
- Contraste adequado de cores

## 🔒 Segurança

- Sanitização automática contra XSS
- Validação de entrada no client-side
- Escape de HTML em mensagens

## 📊 Exemplos Práticos

### Login com Mensagens Amigáveis

```javascript
async function doLogin() {
  const username = userInput.value.trim();
  const password = passInput.value;
  
  if (!username || !password) {
    toast.error('Preencha usuário e senha.');
    return;
  }
  
  const btn = document.querySelector('button[type="submit"]');
  setButtonLoading(btn, true);
  
  try {
    const response = await fetch('/api/auth/token/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail);
    }
    
    localStorage.setItem('access', data.access);
    localStorage.setItem('refresh', data.refresh);
    
    toast.success('Login realizado com sucesso!');
    setTimeout(() => window.location.href = '/', 500);
  } catch (error) {
    const friendlyMessage = getFriendlyErrorMessage(error.message);
    toast.error(friendlyMessage);
  } finally {
    setButtonLoading(btn, false);
  }
}
```

### Cadastro de Animal

```javascript
async function cadastrarAnimal(formData) {
  const form = document.getElementById('form-animal');
  
  if (!validateForm(form)) {
    toast.error('Corrija os erros no formulário');
    return;
  }
  
  const btn = form.querySelector('button[type="submit"]');
  setButtonLoading(btn, true);
  
  try {
    const response = await fetchWithErrorHandling('/api/animais/', {
      method: 'POST',
      body: formData
    });
    
    toast.success('Animal cadastrado com sucesso!');
    form.reset();
  } catch (error) {
    // Erro já foi tratado automaticamente
  } finally {
    setButtonLoading(btn, false);
  }
}
```

## 🎓 Valor para o TCC

Este sistema demonstra:

1. **UX Profissional:** Feedback visual consistente
2. **Acessibilidade:** Conformidade com WCAG
3. **Segurança:** Prevenção de XSS
4. **Manutenibilidade:** Código centralizado e reutilizável
5. **Qualidade:** Mensagens amigáveis ao usuário

## 📄 Arquivos

- `toast-notifications.js` - Sistema principal (400+ linhas)
- `style.css` - Estilos das notificações (180+ linhas adicionadas)
- `toast-demo.html` - Página de demonstração
- `login.js` - Atualizado para usar toasts
- `registro.js` - Atualizado para usar toasts

## 🔄 Migração de Código Existente

### Antes (alert nativo):
```javascript
alert('Erro ao enviar!');
```

### Depois (toast amigável):
```javascript
toast.error('Erro ao enviar sua mensagem. Tente novamente.');
```

---

**Desenvolvido por:** Daniel (TCC S.O.S Pets)  
**Framework:** Vanilla JavaScript  
**Última Atualização:** 21/11/2025
