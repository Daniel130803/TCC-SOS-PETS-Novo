document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('register-form');
  const msg  = document.getElementById('register-msg');
  if (!form) return;

  // Adiciona validação em tempo real nos campos
  addRealtimeValidation('email', validateEmail);
  addRealtimeValidation('telefone', (v) => v ? validateTelefone(v) : {valid: true, message: ''});
  addRealtimeValidation('first_name', (v) => validateNomeCompleto(v));
  addRealtimeValidation('username', (v) => validateTexto(v, 'Usuário', 3, 30));
  addRealtimeValidation('password', (v) => validateSenha(v, 6));

  // Aplica máscara de telefone
  applyMask('telefone', maskTelefone);

  // Valida confirmação de senha em tempo real
  const password2Input = document.getElementById('password2');
  if (password2Input) {
    password2Input.addEventListener('blur', function() {
      const senha = document.getElementById('password').value;
      const resultado = validateSenhaConfirmacao(senha, this.value);
      
      this.classList.remove('is-valid', 'is-invalid');
      if (resultado.valid && this.value) {
        this.classList.add('is-valid');
      } else if (!resultado.valid && this.value) {
        this.classList.add('is-invalid');
        let feedbackDiv = this.nextElementSibling;
        if (!feedbackDiv || !feedbackDiv.classList.contains('invalid-feedback')) {
          feedbackDiv = document.createElement('div');
          feedbackDiv.className = 'invalid-feedback';
          feedbackDiv.style.color = '#b00020';
          feedbackDiv.style.fontSize = '0.875rem';
          feedbackDiv.style.marginTop = '0.25rem';
          this.parentNode.appendChild(feedbackDiv);
        }
        feedbackDiv.textContent = resultado.message;
      }
    });
  }

  function showMsg(text, ok=false) {
    if (ok) {
      toast.success(text);
    } else {
      toast.error(text);
    }
    // Mantém compatibilidade com elemento msg existente
    if (msg) {
      msg.textContent = text;
      msg.style.color = ok ? '#0a7a0a' : '#b00020';
    }
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const first_name = document.getElementById('first_name').value.trim();
    const telefone = document.getElementById('telefone').value.trim();
    const password2 = document.getElementById('password2').value;

    // Validações robustas com validateForm
    const valido = validateForm({
      first_name: validateNomeCompleto(first_name),
      username: validateTexto(username, 'Usuário', 3, 30),
      email: validateEmail(email),
      password: validateSenha(password, 6),
      password2: validateSenhaConfirmacao(password, password2),
      ...(telefone && { telefone: validateTelefone(telefone) })
    });

    if (!valido) return;

    // Sanitiza inputs
    const payload = {
      username: sanitizeInput(username).toLowerCase(),
      email: sanitizeInput(email).toLowerCase(),
      password: password, // Senha não sanitiza (pode conter caracteres especiais)
      first_name: sanitizeInput(first_name),
      telefone: telefone.replace(/\D/g, ''), // Remove formatação
    };

    const submitBtn = form.querySelector('button[type="submit"]');
    setButtonLoading(submitBtn, true);

    try {
      const resp = await fetch('/api/auth/register/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await resp.json().catch(()=>({}));
      
      if (!resp.ok) {
        const detail = getFriendlyErrorMessage(data);
        throw new Error(detail);
      }
      
      showMsg('Conta criada com sucesso! Redirecionando para o login...', true);
      setTimeout(() => window.location.href = '/login/', 1500);
    } catch (err) {
      setButtonLoading(submitBtn, false);
      showMsg(err.message);
    }
  });
});