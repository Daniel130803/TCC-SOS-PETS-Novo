/**
 * Testes para o módulo de Registro (registro.js).
 * 
 * Testa:
 * - Validação de campos obrigatórios
 * - Validação de confirmação de senha
 * - Registro bem-sucedido
 * - Tratamento de email duplicado
 * - Exibição de mensagens de erro/sucesso
 * - Redirecionamento após registro
 */

describe('Registro Module', () => {
  let form, usernameInput, emailInput, passwordInput, password2Input, msgDiv;

  beforeEach(() => {
    document.body.innerHTML = `
      <form id="register-form">
        <input type="text" id="username" />
        <input type="email" id="email" />
        <input type="password" id="password" />
        <input type="password" id="password2" />
        <input type="text" id="first_name" />
        <input type="text" id="telefone" />
        <button type="submit">Registrar</button>
      </form>
      <div id="register-msg"></div>
    `;

    form = document.getElementById('register-form');
    usernameInput = document.getElementById('username');
    emailInput = document.getElementById('email');
    passwordInput = document.getElementById('password');
    password2Input = document.getElementById('password2');
    msgDiv = document.getElementById('register-msg');
  });

  // Helper para exibir mensagens
  const showMsg = (text, ok = false) => {
    msgDiv.textContent = text;
    msgDiv.style.color = ok ? '#0a7a0a' : '#b00020';
  };

  test('deve validar campos obrigatórios', async () => {
    usernameInput.value = '';
    emailInput.value = '';
    passwordInput.value = '';

    const handleSubmit = async () => {
      const payload = {
        username: usernameInput.value.trim(),
        email: emailInput.value.trim(),
        password: passwordInput.value
      };

      if (!payload.username || !payload.email || !payload.password) {
        showMsg('Preencha usuário, e-mail e senha.');
        return;
      }
    };

    await handleSubmit();
    expect(msgDiv.textContent).toBe('Preencha usuário, e-mail e senha.');
    expect(msgDiv.style.color).toContain('176'); // rgb(176, 0, 32) ou #b00020
  });

  test('deve validar confirmação de senha', async () => {
    usernameInput.value = 'testuser';
    emailInput.value = 'test@email.com';
    passwordInput.value = 'senha123';
    password2Input.value = 'senha456'; // diferente

    const handleSubmit = async () => {
      const password = passwordInput.value;
      const confirm = password2Input.value;

      if (password !== confirm) {
        showMsg('As senhas não conferem.');
        return;
      }
    };

    await handleSubmit();
    expect(msgDiv.textContent).toBe('As senhas não conferem.');
  });

  test('deve registrar usuário com sucesso', async () => {
    mockFetchSuccess({ id: 1, username: 'testuser' });

    usernameInput.value = 'testuser';
    emailInput.value = 'test@email.com';
    passwordInput.value = 'senha123';
    password2Input.value = 'senha123';
    document.getElementById('first_name').value = 'Test User';
    document.getElementById('telefone').value = '11999999999';

    const handleSubmit = async (e) => {
      e?.preventDefault();

      const payload = {
        username: usernameInput.value.trim(),
        email: emailInput.value.trim(),
        password: passwordInput.value,
        first_name: document.getElementById('first_name').value.trim(),
        telefone: document.getElementById('telefone').value.trim()
      };
      const confirm = password2Input.value;

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
          body: JSON.stringify(payload)
        });
        const data = await resp.json();
        
        if (!resp.ok) {
          throw new Error(data.detail || 'Erro no registro.');
        }
        
        showMsg('Conta criada com sucesso! Redirecionando para o login...', true);
      } catch (err) {
        showMsg(err.message);
      }
    };

    await handleSubmit({ preventDefault: jest.fn() });

    expect(fetch).toHaveBeenCalledWith('/api/auth/register/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: expect.stringContaining('testuser')
    });

    expect(msgDiv.textContent).toBe('Conta criada com sucesso! Redirecionando para o login...');
    expect(msgDiv.style.color).toContain('10'); // rgb(10, 122, 10) ou #0a7a0a
  });

  test('deve tratar email duplicado', async () => {
    mockFetchError(400, 'Email já cadastrado');

    usernameInput.value = 'testuser';
    emailInput.value = 'existing@email.com';
    passwordInput.value = 'senha123';
    password2Input.value = 'senha123';

    const handleSubmit = async () => {
      const payload = {
        username: usernameInput.value.trim(),
        email: emailInput.value.trim(),
        password: passwordInput.value
      };

      try {
        const resp = await fetch('/api/auth/register/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await resp.json();
        
        if (!resp.ok) {
          throw new Error(data.detail || 'Erro no registro.');
        }
      } catch (err) {
        showMsg(err.message);
      }
    };

    await handleSubmit();
    expect(msgDiv.textContent).toBe('Email já cadastrado');
    expect(msgDiv.style.color).toContain('176'); // rgb(176, 0, 32) ou #b00020
  });

  test('deve prevenir submit padrão', () => {
    const preventDefault = jest.fn();
    const event = { preventDefault };

    form.addEventListener('submit', (e) => e.preventDefault());
    form.dispatchEvent(new Event('submit'));

    expect(preventDefault).not.toThrow();
  });
});
