document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('register-form');
  const msg  = document.getElementById('register-msg');
  if (!form) return;

  function showMsg(text, ok=false) {
    msg.textContent = text;
    msg.style.color = ok ? '#0a7a0a' : '#b00020';
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const payload = {
      username: document.getElementById('username').value.trim(),
      email: document.getElementById('email').value.trim(),
      password: document.getElementById('password').value,
      first_name: document.getElementById('first_name').value.trim(),
      telefone: document.getElementById('telefone').value.trim(),
    };
    const confirm = document.getElementById('password2').value;

    if (!payload.username || !payload.email || !payload.password) {
      showMsg('Preencha usuário, e-mail e senha.');
      return;
    }
    if (payload.password !== confirm) {
      showMsg('As senhas não conferem.');
      return;
    }

    try {
      const resp = await fetch('/api/auth/register/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await resp.json().catch(()=>({}));
      if (!resp.ok) {
        const detail = data.detail || Object.values(data).flat().join(' ') || 'Erro no registro.';
        throw new Error(detail);
      }
      showMsg('Conta criada com sucesso! Redirecionando para o login...', true);
      setTimeout(() => window.location.href = '/login/', 900);
    } catch (err) {
      showMsg(err.message);
    }
  });
});