// JS dedicado à página de login
// Intercepta o formulário, envia credenciais ao endpoint JWT e redireciona para a Home

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('login-form') || document.querySelector('form');
  if (!form) return;

  // Evita qualquer submit nativo
  form.addEventListener('submit', (e) => { e.preventDefault(); e.stopPropagation(); });

  const userInput = document.getElementById('username') || form.querySelector('input[name="username"]');
  const passInput = document.getElementById('password') || form.querySelector('input[name="password"]');
  const btn = document.getElementById('btn-login') || form.querySelector('button[type="submit"], button');

  // Adiciona validação em tempo real
  if (userInput) {
    addRealtimeValidation('username', (v) => validateTexto(v, 'Usuário', 3, 30));
  }

  async function doLogin() {
    const username = (userInput?.value || '').trim();
    const password = passInput?.value || '';
    
    // Validações robustas
    const valido = validateForm({
      username: validateTexto(username, 'Usuário', 3, 30),
      password: password ? { valid: true, message: '' } : { valid: false, message: 'Senha é obrigatória' }
    });

    if (!valido) return;

    // Sanitiza username
    const usernameLimpo = sanitizeInput(username).toLowerCase();

    setButtonLoading(btn, true);

    try {
      const resp = await fetch('/api/auth/token/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: usernameLimpo, password })
      });
      const data = await resp.json().catch(() => ({}));
      
      if (!resp.ok) {
        throw new Error(data.detail || 'Credenciais inválidas');
      }

      // Mantém logado (salva tokens no navegador)
      localStorage.setItem('access', data.access);
      localStorage.setItem('refresh', data.refresh);
      
      toast.success('Login realizado com sucesso!');
      
      // Redireciona para a home
      setTimeout(() => window.location.href = '/', 1000);
    } catch (err) {
      setButtonLoading(btn, false);
      const friendlyMessage = getFriendlyErrorMessage(err.message);
      toast.error(friendlyMessage);
    }
  }

  btn?.addEventListener('click', (e) => { e.preventDefault(); doLogin(); });
  form.addEventListener('keydown', (e) => { 
    if (e.key === 'Enter') { 
      e.preventDefault(); 
      doLogin(); 
    }
  });
});