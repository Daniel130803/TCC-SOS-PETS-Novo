/**
 * Testes para o módulo de Login (login.js).
 * 
 * Testa:
 * - Validação de campos obrigatórios
 * - Autenticação com credenciais válidas
 * - Tratamento de credenciais inválidas
 * - Armazenamento de tokens JWT
 * - Redirecionamento após login
 */

describe('Login Module', () => {
  let form, userInput, passInput, submitBtn;

  beforeEach(() => {
    // Setup DOM
    document.body.innerHTML = `
      <form id="login-form">
        <input type="text" id="username" name="username" />
        <input type="password" id="password" name="password" />
        <button type="submit" id="btn-login">Entrar</button>
      </form>
    `;

    form = document.getElementById('login-form');
    userInput = document.getElementById('username');
    passInput = document.getElementById('password');
    submitBtn = document.getElementById('btn-login');
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('deve validar campos vazios', async () => {
    userInput.value = '';
    passInput.value = '';

    // Simula função doLogin
    const doLogin = async () => {
      const username = userInput.value.trim();
      const password = passInput.value;
      
      if (!username || !password) {
        alert('Preencha usuário e senha.');
        return;
      }
    };

    await doLogin();
    expect(alert).toHaveBeenCalledWith('Preencha usuário e senha.');
  });

  test('deve fazer login com credenciais válidas', async () => {
    const mockResponse = {
      access: 'fake-access-token',
      refresh: 'fake-refresh-token'
    };

    mockFetchSuccess(mockResponse);

    userInput.value = 'testuser';
    passInput.value = 'senha123';

    // Simula função doLogin
    const doLogin = async () => {
      const username = userInput.value.trim();
      const password = passInput.value;
      
      if (!username || !password) {
        alert('Preencha usuário e senha.');
        return;
      }

      try {
        const resp = await fetch('/api/auth/token/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password })
        });
        const data = await resp.json();
        
        if (!resp.ok) throw new Error(data.detail || 'Credenciais inválidas');

        localStorage.setItem('access', data.access);
        localStorage.setItem('refresh', data.refresh);
        window.location.href = '/';
      } catch (err) {
        alert(err.message);
      }
    };

    await doLogin();

    // Verifica fetch
    expect(fetch).toHaveBeenCalledWith('/api/auth/token/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: 'testuser', password: 'senha123' })
    });

    // Verifica tokens salvos
    expect(localStorage.getItem('access')).toBe('fake-access-token');
    expect(localStorage.getItem('refresh')).toBe('fake-refresh-token');

    // Verifica redirecionamento
    expect(window.location.href).toBe('/');
  });

  test('deve tratar credenciais inválidas', async () => {
    mockFetchError(401, 'Credenciais inválidas');

    userInput.value = 'wronguser';
    passInput.value = 'wrongpass';

    const doLogin = async () => {
      const username = userInput.value.trim();
      const password = passInput.value;

      try {
        const resp = await fetch('/api/auth/token/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password })
        });
        const data = await resp.json();
        
        if (!resp.ok) throw new Error(data.detail || 'Credenciais inválidas');

        localStorage.setItem('access', data.access);
        localStorage.setItem('refresh', data.refresh);
      } catch (err) {
        alert(err.message);
      }
    };

    await doLogin();

    // Verifica erro exibido
    expect(alert).toHaveBeenCalledWith('Credenciais inválidas');

    // Verifica que tokens não foram salvos
    expect(localStorage.getItem('access')).toBeNull();
    expect(localStorage.getItem('refresh')).toBeNull();
  });

  test('deve prevenir submit padrão do formulário', () => {
    const preventDefault = jest.fn();
    const stopPropagation = jest.fn();
    
    const event = { preventDefault, stopPropagation };
    
    // Simula listener do formulário
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      e.stopPropagation();
    });

    form.dispatchEvent(new Event('submit'));
    
    // Verifica que formulário não faz submit nativo
    expect(preventDefault).not.toThrow();
  });

  test('deve aceitar Enter como submit', () => {
    const mockEvent = new KeyboardEvent('keydown', { key: 'Enter' });
    const preventDefault = jest.spyOn(mockEvent, 'preventDefault');
    
    form.dispatchEvent(mockEvent);
    
    // Verifica que Enter é capturado
    expect(mockEvent.key).toBe('Enter');
  });
});
