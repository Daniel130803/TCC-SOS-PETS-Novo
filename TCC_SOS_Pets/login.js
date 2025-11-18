// JS dedicado à página de login
// Intercepta o formulário, envia credenciais ao endpoint JWT e redireciona para a Home

document.addEventListener('DOMContentLoaded', () => {
  // pega o primeiro <form> da página (layout existente)
  const form = document.getElementById('login-form') || document.querySelector('form');
  if (!form) return;

  // evita qualquer submit nativo (elimina GET com querystring e CSRF do /login/)
  form.addEventListener('submit', (e) => { e.preventDefault(); e.stopPropagation(); });

  // tenta achar campos por id ou name (compatível com seu HTML atual)
  const userInput = document.getElementById('username') || form.querySelector('input[name="username"]') || form.querySelector('input[type="text"]');
  const passInput = document.getElementById('password') || form.querySelector('input[name="password"]') || form.querySelector('input[type="password"]');
  const btn = document.getElementById('btn-login') || form.querySelector('button[type="submit"], button, input[type="submit"]');

  async function doLogin() {
    const username = (userInput?.value || '').trim();
    const password = passInput?.value || '';
    if (!username || !password) { alert('Preencha usuário e senha.'); return; }

    try {
      const resp = await fetch('/api/auth/token/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await resp.json().catch(() => ({}));
      if (!resp.ok) throw new Error(data.detail || 'Credenciais inválidas');

      // mantém logado (salva tokens no navegador)
      localStorage.setItem('access', data.access);
      localStorage.setItem('refresh', data.refresh);
      // redireciona para a home
      window.location.href = '/';
    } catch (err) {
      alert(err.message || 'Erro ao entrar.');
    }
  }

  btn?.addEventListener('click', (e) => { e.preventDefault(); doLogin(); });
  form.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); doLogin(); }});
});

document.addEventListener('DOMContentLoaded', () => {
  // pega o primeiro <form> da página (ou ajuste o seletor se precisar)
  const form = document.querySelector('form');
  if (!form) return;

  // evita envio nativo (nada de GET/POST para /login/)
  form.addEventListener('submit', (e) => { e.preventDefault(); e.stopPropagation(); });

  // tenta achar campos e botão (sem depender de ids)
  const userInput = form.querySelector('input[name="username"], input[type="text"]');
  const passInput = form.querySelector('input[name="password"], input[type="password"]');
  const btn = form.querySelector('button[type="submit"], button, input[type="submit"]');

  async function doLogin() {
    const username = (userInput?.value || '').trim();
    const password = passInput?.value || '';
    if (!username || !password) { alert('Preencha usuário e senha.'); return; }

    try {
      const resp = await fetch('/api/auth/token/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await resp.json().catch(() => ({}));
      if (!resp.ok) throw new Error(data.detail || 'Credenciais inválidas');

      localStorage.setItem('access', data.access);
      localStorage.setItem('refresh', data.refresh);
      window.location.href = '/'; // home
    } catch (err) {
      alert(err.message || 'Erro ao entrar.');
    }
  }

  btn?.addEventListener('click', (e) => { e.preventDefault(); doLogin(); });
  form.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); doLogin(); }});
});